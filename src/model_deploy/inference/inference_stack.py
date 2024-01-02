import yaml
import sagemaker
from constructs import Construct
from aws_cdk import (
    aws_sagemaker as sagemaker_,
    Stack
)


class InferenceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ==========================
        # ======== CONFIG  =========
        # ==========================
        # IAM ROLE FOR ENDPOINT
        iam_role = sagemaker.get_execution_role()

        # READ CONFIG
        with open("../../cfg/model_deploy.yaml") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        sagemaker_model_name = f"{config['model']['name']}-{config['model']['version']}"
        # ===========================
        # ===== SAGEMAKER MODEL =====
        # ===========================
        container = sagemaker_.CfnModel.ContainerDefinitionProperty(
            image=config["endpoint"]["image_uri"],
            model_data_url=config["model"]["model_uri"],
            environment={
                "MLFLOW_DEPLOYMENT_FLAVOR_NAME": "python_function",
                "SERVING_ENVIRONMENT": "SageMaker",
            }
        )

        sagemaker_model = sagemaker_.CfnModel(
            scope=self,
            id="Model",
            execution_role_arn=iam_role,
            containers=[container],
            model_name=sagemaker_model_name,
        )

        # =====================================
        # ===== SAGEMAKER ENDPOINT CONFIG =====
        # =====================================
        product_variant = sagemaker_.CfnEndpointConfig.ProductionVariantProperty(
            model_name=sagemaker_model.attr_model_name,
            variant_name="variant-1",
            instance_type=config["endpoint"]["instance_type"],
            initial_instance_count=config["endpoint"]["instance_count"],
            initial_variant_weight=1.0,
        )

        sagemaker_endpoint_config = sagemaker_.CfnEndpointConfig(
            scope=self,
            id="EndpointConfig",
            production_variants=[product_variant],
            endpoint_config_name=sagemaker_model.attr_model_name,
        )

        # ==============================
        # ===== SAGEMAKER ENDPOINT =====
        # ==============================
        sagemaker_endpoint = sagemaker_.CfnEndpoint(
            scope=self,
            id="Endpoint",
            endpoint_config_name=sagemaker_endpoint_config.attr_endpoint_config_name,
            endpoint_name=sagemaker_model.attr_model_name,
        )
