# https://konem.blog/2021/01/17/how-to-structure-your-application-architecture-using-aws-cdk/
from aws_cdk import App, Environment, CfnParameter, Aws

from domain.sagemaker_domain_stack import SagemakerDomainStack
from vpc.vpc_stack import VPCStack

app = App()
env_EU = Environment(account=f"{Aws.ACCOUNT_ID}", region=f"{Aws.REGION}")
vpc_stack = VPCStack(app, "VPCStack")
sagemaker_domain_stack = SagemakerDomainStack(app, "SagemakerDomainStack", env_EU)
app.synth()