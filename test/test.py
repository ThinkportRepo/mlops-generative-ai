from mlflow.deployments import get_deploy_client
import botocore
import sagemaker, boto3, json
from sagemaker import get_execution_role
import os

region = boto3.Session().region_name
# Use ARN from the role we created in AWS with the full permission to Sagemaker
arn = get_execution_role()
# Create your name of the future application
app_name = 'mobilenetv3-large-1-dev'
# you may find model uri in "mlflow ui" recorded as "logged_model"
model_uri = f'runs:/d9a0583b847c4fa1aeed92362ea83b7d/9-100.0'
sess = sagemaker.Session()
BUCKET = sess.default_bucket()

# https://github.com/aws/sagemaker-pytorch-inference-toolkit/issues/83
if __name__ == '__main__':
    image_url = "562760952310.dkr.ecr.eu-central-1.amazonaws.com/mlflow-pyfunc:2.9.2"

    config = dict(
        execution_role_arn=arn,
        bucket_name=BUCKET,
        image_url=image_url,
        region_name=region,
        archive=False,
        instance_type="ml.p2.xlarge",
        instance_count=1,
        timeout_seconds=3600,
        variant_name="variant-1"
    )

    client = get_deploy_client("sagemaker")

    client.create_deployment(
        # app name displayed in Sagemaker
        app_name,
        model_uri=model_uri,
        flavor="python_function",
        config=config,
    )