import os

import boto3
from sagemaker import LocalSession, image_uris, model_uris, script_uris, hyperparameters
from sagemaker.estimator import Estimator
from sagemaker.huggingface import HuggingFace
from sagemaker.pytorch import PyTorch
from sagemaker.utils import name_from_base



if __name__ == "__main__":
    ENV_INPUT = {"PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512"}
    # Use the AWS region configured with the AWS CLI
    sess = LocalSession()
    sess.config = {'local': {'local_code': True}}
    region = sess.boto_region_name

    # This does not work on your local machine  because it doesn't have an IAM role
    # role = sagemaker.get_execution_role()
    role = 'arn:aws:iam::562760952310:role/SagemakerMLOpsUserRole'

    # Set local_mode to True to run the training script on the machine that runs this python script
    local_mode = True

    if local_mode:
        instance_type = "local_gpu"
    else:
        instance_type = "ml.c4.xlarge"

    loc_train = os.path.join('file://', '..', 'training_images')

    channels = {"training": loc_train}

    account_id = boto3.client("sts").get_caller_identity().get("Account")

    train_model_id, train_model_version, train_scope = (
        "model-txt2img-stabilityai-stable-diffusion-v2-1-base",
        "*",
        "training",
    )

    # Retrieve the docker image
    train_image_uri = image_uris.retrieve(
        region=region,
        framework=None,  # automatically inferred from model_id
        model_id=train_model_id,
        model_version=train_model_version,
        image_scope=train_scope,
        instance_type=instance_type
    )

    # Retrieve the training script. This contains all the necessary files including data processing, model training etc.
    train_source_uri = script_uris.retrieve(
        model_id=train_model_id, model_version=train_model_version, script_scope=train_scope
    )

    # Retrieve the pre-trained model tarball to further fine-tune
    train_model_uri = model_uris.retrieve(
        model_id=train_model_id, model_version=train_model_version, model_scope=train_scope
    )

    # Retrieve the default hyperparameters for fine-tuning the model
    hyperparameters = hyperparameters.retrieve_default(
        model_id=train_model_id, model_version=train_model_version
    )

    # [Optional] Override default hyperparameters with custom values. This controls the duration of the training and the quality of the output.
    # If max_steps is too small, training will be fast but the the model will not be able to generate custom images for your usecase.
    # If max_steps is too large, training will be very slow.
    hyperparameters["max_steps"] = "200"

    training_job_name = name_from_base(f"jumpstart-example-{train_model_id}-transfer-learning")
    output_path = os.path.join('file://', '..', 'outputs', "stable-diffusion-v2-1-base")

    # Create SageMaker Estimator instance
    sd_estimator = Estimator(
        role=role,
        image_uri=train_image_uri,
        source_dir=train_source_uri,
        model_uri=train_model_uri,
        entry_point="transfer_learning.py",  # Entry-point file in source_dir and present in train_source_uri.
        instance_count=1,
        instance_type=instance_type,
        max_run=360000,
        hyperparameters=hyperparameters,
        output_path=output_path,
        base_job_name=training_job_name,
        environment=ENV_INPUT, container_arguments=['-e', "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512"]
    )

    sd_estimator.fit(inputs=channels, logs='All')
