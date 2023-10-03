from aws_cdk import Stack
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ssm import StringParameter
from constructs import Construct


class SSMStack(Stack):
    def __init__(self, scope: Construct, id: str, *, vpc=Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc_id = StringParameter(self, "MLOpsVpcId",
                                 parameter_name="/mlops/vpc/id",
                                 string_value=vpc.vpc_id
                                 )

        vpc_public_subnets = StringParameter(self, "MLOpsVpcId",
                                             parameter_name="/mlops/vpc/public/subnet/id",
                                             string_value=vpc.public_subnets
                                             )

        vpc_private_subnets = StringParameter(self, "MLOpsVpcId",
                                              parameter_name="/mlops/vpc/private/subnet/id",
                                              string_value=vpc.private_subnets
                                              )

        vpc_isolated_subnets = StringParameter(self, "MLOpsVpcId",
                                               parameter_name="/mlops/vpc/private/subnet/id",
                                               string_value=vpc.isolated_subnets
                                               )
