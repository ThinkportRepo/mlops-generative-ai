import os
from aws_cdk import App, Environment, Tags
from inference.inference_stack import InferenceStack

app = App()
env_default = Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
InferenceStack(app, "InferenceStack", env=env_default)
Tags.of(app).add("project", "mlops")
Tags.of(app).add("owner", "Timea")
Tags.of(app).add("ttl", "31.12.2024")
app.synth()