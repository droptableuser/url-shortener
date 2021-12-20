from aws_cdk import core
from aws_cdk.core import Duration
from aws_cdk import aws_dynamodb, aws_lambda, aws_apigateway, aws_certificatemanager, aws_route53, aws_route53_targets, aws_iam
import sys
import os

ZONE_NAME = os.environ.get("DROPTABLEUSER_ZONE", "droptableuser.me")


class UrlshortenerStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, appdetails, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        if appdetails["id"] != "urlshortener":
            sys.exit(1)

        subdomain = appdetails["domain"]
        app_id = appdetails["id"]
        user_name = appdetails["user"]
        domain_name = subdomain + "." + ZONE_NAME

        # define the table that maps short codes to URLs.
        table = aws_dynamodb.Table(self, "Table",
                                   partition_key=aws_dynamodb.Attribute(
                                       name="id",
                                       type=aws_dynamodb.AttributeType.STRING),
                                   read_capacity=10,
                                   write_capacity=5)

        # define the API gateway request handler. all API requests will go to the same function.
        read_handler = aws_lambda.Function(self, app_id+"ReadFunction",
                                           code=aws_lambda.Code.from_asset(
                                               "./lambda/read"),
                                           handler="handler.main",
                                           timeout=Duration.minutes(5),
                                           runtime=aws_lambda.Runtime.PYTHON_3_7)

        read_handler.add_environment('TABLE_NAME', table.table_name)
        table.grant_read_data(read_handler)

        write_handler = aws_lambda.Function(self, app_id+"CreateFunction",
                                            code=aws_lambda.Code.from_asset(
                                                "./lambda/create"),
                                            handler="handler.main",
                                            timeout=Duration.minutes(5),
                                            runtime=aws_lambda.Runtime.PYTHON_3_7)
        table.grant_read_write_data(write_handler)
        write_handler.add_environment('TABLE_NAME', table.table_name)

        read_integration = aws_apigateway.LambdaIntegration(read_handler)
        write_integration = aws_apigateway.LambdaIntegration(write_handler)

        api = api = aws_apigateway.RestApi(
            self, app_id+"Api", default_integration=read_integration)
        
        reader = api.root.add_resource("{proxy+}")
        reader.add_method("ANY",read_integration)

        writer = api.root.add_resource("targetUrl")
        writer_get = writer.add_method("GET", write_integration,
                                       authorization_type=aws_apigateway.AuthorizationType.IAM,
                                       api_key_required=False)
        writer_post = writer.add_method("POST", write_integration,
                                        authorization_type=aws_apigateway.AuthorizationType.IAM,
                                        api_key_required=False)

        iam_user = aws_iam.User.from_user_name(self,app_id+"User",user_name)

        iam_user.attach_inline_policy(aws_iam.Policy(self, "AllowBooks",
                                                     statements=[
                                                         aws_iam.PolicyStatement(
                                                             actions=[
                                                                 "execute-api:Invoke"],
                                                             effect=aws_iam.Effect.ALLOW,
                                                             resources=[
                                                                 writer_get.method_arn, writer_post.method_arn]
                                                         )
                                                     ]
                                                     ))

        hosted_zone = aws_route53.HostedZone.from_lookup(
            self, app_id+"HostedZone", domain_name=ZONE_NAME)

        cert = aws_certificatemanager.Certificate(
            self, "Certificate",
            domain_name=domain_name,
            validation=aws_certificatemanager.CertificateValidation.from_dns(hosted_zone))
        domain = api.add_domain_name(
            'Domain',
            certificate=cert,
            domain_name=domain_name)

        aws_route53.ARecord(self, app_id+"Domain", record_name=subdomain, zone=hosted_zone,
                            target=aws_route53.RecordTarget.from_alias(aws_route53_targets.ApiGatewayDomain(domain)))
