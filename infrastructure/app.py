# https://konem.blog/2021/01/17/how-to-structure-your-application-architecture-using-aws-cdk/
import os
from aws_cdk import App, Environment, CfnParameter, Aws, Tags
from domain.sagemaker_domain_stack import SagemakerDomainStack
from ssm.ssm_stack import SSMStack
from vpc.vpc_stack import VPCStack

app = App()
env_default = Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
vpc_stack = VPCStack(app, "VPCStack", env=env_default)
ssm_stack = SSMStack(app, "SSMStack", env=env_default, vpc=vpc_stack.vpc)
sagemaker_domain_stack = SagemakerDomainStack(app, "SagemakerDomainStack", env=env_default)

Tags.of(app).add("project", "mlops")
Tags.of(app).add("owner", "Timea")
Tags.of(app).add("ttl", "31.12.2023")
app.synth()
