from aws_cdk import Stack, CfnOutput
from aws_cdk.aws_ec2 import (
    SubnetType,
    SubnetConfiguration,
    IpAddresses,
    Vpc,
    NatProvider,
    GatewayVpcEndpointAwsService
)
from aws_cdk.aws_ssm import StringParameter
from constructs import Construct


class VPCStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ==================================================
        # ==================== VPC =========================
        # ==================================================
        public_subnet = SubnetConfiguration(
            name="Public", subnet_type=SubnetType.PUBLIC, cidr_mask=28
        )
        private_subnet = SubnetConfiguration(
            name="Private", subnet_type=SubnetType.PRIVATE_WITH_EGRESS, cidr_mask=28
        )
        isolated_subnet = SubnetConfiguration(
            name="DB", subnet_type=SubnetType.PRIVATE_ISOLATED, cidr_mask=28
        )

        self.vpc = Vpc(
            scope=self,
            id="mlflow-vpc",
            ip_addresses=IpAddresses.cidr("10.0.0.0/24"),
            nat_gateway_provider=NatProvider.gateway(),
            nat_gateways=1,
            availability_zones=["eu-central-1a", "eu-central-1b"],
            subnet_configuration=[public_subnet, private_subnet, isolated_subnet],
        )

        self.vpc.add_gateway_endpoint(
            "S3Endpoint", service=GatewayVpcEndpointAwsService.S3
        )
