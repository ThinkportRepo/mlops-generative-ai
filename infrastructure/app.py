# https://konem.blog/2021/01/17/how-to-structure-your-application-architecture-using-aws-cdk/
import logging
import os

from aws_cdk import App, Environment, CfnParameter, Aws

from domain.sagemaker_domain_stack import SagemakerDomainStack
from vpc.vpc_stack import VPCStack

app = App()
env_default = Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
vpc_stack = VPCStack(app, "VPCStack", env=env_default)
sagemaker_domain_stack = SagemakerDomainStack(app, "SagemakerDomainStack", env=env_default)
app.synth()