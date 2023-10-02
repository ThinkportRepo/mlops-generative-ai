# https://konem.blog/2021/01/17/how-to-structure-your-application-architecture-using-aws-cdk/
from aws_cdk import App

from domain.sagemaker_domain_stack import SagemakerDomainStack
from vpc.vpc_stack import VPCStack

app = App()
vpc_stack = VPCStack(app, "VPCStack")
sagemaker_domain_stack = SagemakerDomainStack(app, "SagemakerDomainStack")
app.synth()