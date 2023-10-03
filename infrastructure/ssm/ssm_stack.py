from aws_cdk import Stack
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ssm import StringParameter
from constructs import Construct


class SSMStack(Stack):
    def __init__(self, scope: Construct, id: str, *, vpc=Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc_id_param = StringParameter(self, "MLOpsVpcId",
                                       parameter_name="/mlops/vpc/id",
                                       string_value=vpc.vpc_id
                                       )


