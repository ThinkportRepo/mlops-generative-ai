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
        public_subnet1 = vpc.public_subnets[1]

        vpc_public_subnet0 = StringParameter(self, "MLOpsVpcPublicSubnet0",
                                             parameter_name="/mlops/vpc/public/subnet0/id",
                                             string_value=public_subnet0.subnet_id
                                             )
        vpc_public_subnet1 = StringParameter(self, "MLOpsVpcPublicSubnet1",
                                             parameter_name="/mlops/vpc/public/subnet1/id",
                                             string_value=public_subnet1.subnet_id
                                             )

        private_subnet0 = vpc.private_subnets[0]
        private_subnet1 = vpc.private_subnets[1]

        vpc_private_subnet0 = StringParameter(self, "MLOpsVpcPrivateSubnet0",
                                              parameter_name="/mlops/vpc/private/subnet0/id",
                                              string_value=private_subnet0.subnet_id
                                              )

        vpc_private_subnet1 = StringParameter(self, "MLOpsVpcPrivateSubnet1",
                                              parameter_name="/mlops/vpc/private/subnet1/id",
                                              string_value=private_subnet1.subnet_id
                                              )

        isolated_subnet0 = vpc.isolated_subnets[0]
        isolated_subnet1 = vpc.isolated_subnets[1]

        vpc_isolated_subnet0 = StringParameter(self, "MLOpsVpcIsolatedSubnets",
                                               parameter_name="/mlops/vpc/isolated/subnet0/id",
                                               string_value=isolated_subnet0
                                               )
        vpc_isolated_subnet1 = StringParameter(self, "MLOpsVpcIsolatedSubnets",
                                               parameter_name="/mlops/vpc/isolated/subnet1/id",
                                               string_value=isolated_subnet1
                                               )
