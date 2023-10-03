from aws_cdk import Stack
from aws_cdk.aws_ec2 import Vpc, SubnetType, SubnetSelection, Subnet
from aws_cdk.aws_ssm import StringParameter
from constructs import Construct


class SSMStack(Stack):
    def __init__(self, scope: Construct, id: str, *, vpc=Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc_id = StringParameter(self, "MLOpsVpcId",
                                 parameter_name="/mlops/vpc/id",
                                 string_value=vpc.vpc_id
                                 )


        public_subnet0 = vpc.public_subnets[0]


        vpc_public_subnets = StringParameter(self, "MLOpsVpcPublicSubnets",
                                             parameter_name="/mlops/vpc/public/subnet/id",
                                             string_value=public_subnet0.subnet_id
                                             )
        #
        # vpc_private_subnets = StringParameter(self, "MLOpsVpcPrivateSubnets",
        #                                       parameter_name="/mlops/vpc/private/subnet/id",
        #                                       string_value=vpc.private_subnets
        #                                       )
        #
        # vpc_isolated_subnets = StringParameter(self, "MLOpsVpcIsolatedSubnets",
        #                                        parameter_name="/mlops/vpc/isolated/subnet/id",
        #                                        string_value=vpc.isolated_subnets
        #                                        )
