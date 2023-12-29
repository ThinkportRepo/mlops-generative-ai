# https://konem.blog/2021/01/17/how-to-structure-your-application-architecture-using-aws-cdk/
import os
from aws_cdk import App, Environment, Tags
from domain.sagemaker_domain_stack import SagemakerDomainStack
from infrastructure.mlflow.mlflow_stack import MLFlowStack
from ssm.ssm_stack import SSMStack
from vpc.vpc_stack import VPCStack

app = App()
env_default = Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])

vpc_stack = VPCStack(app, "VPCStack", termination_protection=True, env=env_default)
ssm_stack = SSMStack(app, "SSMStack", termination_protection=True, env=env_default, vpc=vpc_stack.vpc)
mlflow_stack = MLFlowStack(app, "MLflowStack", termination_protection=True, env=env_default)
sagemaker_domain_stack = SagemakerDomainStack(app, "SagemakerDomainStack", termination_protection=True, env=env_default)

ssm_stack.add_dependency(vpc_stack)
mlflow_stack.add_dependency(vpc_stack)
mlflow_stack.add_dependency(ssm_stack)
sagemaker_domain_stack.add_dependency(vpc_stack)
sagemaker_domain_stack.add_dependency(ssm_stack)

Tags.of(app).add("project", "mlops")
Tags.of(app).add("owner", "Timea")
Tags.of(app).add("ttl", "31.12.2024")
app.synth()
