import boto3
from sagemaker import image_uris, script_uris, model_uris, Model
from sagemaker.estimator import Estimator
from sagemaker.transformer import Transformer
from sagemaker.utils import name_from_base
from sagemaker.workflow.model_step import ModelStep
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.pipeline_context import LocalPipelineSession
from sagemaker.workflow.retry import StepRetryPolicy, StepExceptionTypeEnum
from sagemaker.workflow.steps import TransformStep, TrainingStep
from sagemaker import hyperparameters


if __name__ == "__main__":
    session = LocalPipelineSession()
    aws_region = session.boto_region_name

    # If uploading to a different folder, change this variable.
    local_training_dataset_folder = "training_images"

    account_id = boto3.client("sts").get_caller_identity().get("Account")
    training_bucket = f"stable-diffusion-jumpstart-{aws_region}-{account_id}"

    s3 = boto3.client("s3")
    s3.download_file(
        f"jumpstart-cache-prod-{aws_region}",
        "ai_services_assets/custom_labels/cl_jumpstart_ic_notebook_utils.py",
        "feature_store_utils.py",
    )

    # create_bucket_if_not_exists(training_bucket)
    train_s3_path = f"s3://{training_bucket}/custom_cedar_apple_rust_stable_diffusion_dataset/"

    output_bucket = session.default_bucket()
    output_prefix = "jumpstart-example-sd-training"

    # needed for storing model artefacts
    s3_output_location = f"s3://{output_bucket}/{output_prefix}/model"
    s3_input_data_path = f"s3://{output_bucket}/{output_prefix}/batch_input/"
    s3_output_data_path = f"s3://{output_bucket}/{output_prefix}/batch_output/"

    # https://repost.aws/questions/QUkP-cRiP3QiCAIqnwyirz1A/how-to-get-batch-transform-with-jsonl-data
    # https://sagemaker-examples.readthedocs.io/en/latest/introduction_to_amazon_algorithms/jumpstart-foundation-models/text2text-generation-Batch-Transform.html
    prompt_file_name = "../prompts/input/cedar_apple_rust.json"
    s3.upload_file(prompt_file_name, output_bucket, f"{output_prefix}/batch_input/{prompt_file_name}")

    # This does not work on your local machine  because it doesn't have an IAM role
    # role = sagemaker.get_execution_role()
    aws_role = 'arn:aws:iam::562760952310:role/SagemakerMLOpsUserRole'

    # Set local_mode to True to run the training script on the machine that runs this python script
    local_mode = True

    if local_mode:
        instance_type = "local_gpu"
    else:
        instance_type = "ml.c4.xlarge"

    train_model_id, train_model_version, train_scope = (
        "model-txt2img-stabilityai-stable-diffusion-v2-1-base",
        "*",
        "training",
    )

    # Tested with ml.g4dn.2xlarge (16GB GPU memory) and ml.g5.2xlarge (24GB GPU memory) instances. Other instances may work as well.
    # If ml.g5.2xlarge instance type is available, please change the following instance type to speed up training.
    training_instance_type = "ml.g5.2xlarge"

    # Retrieve the docker image
    train_image_uri = image_uris.retrieve(
        region=aws_region,
        framework=None,  # automatically inferred from model_id
        model_id=train_model_id,
        model_version=train_model_version,
        image_scope=train_scope,
        instance_type=instance_type,
    )

    # Retrieve the training script. This contains all the necessary files including data processing, model training etc.
    train_source_uri = script_uris.retrieve(
        model_id=train_model_id, model_version=train_model_version, script_scope=train_scope
    )
    # Retrieve the pre-trained model tarball to further fine-tune
    train_model_uri = model_uris.retrieve(
        model_id=train_model_id, model_version=train_model_version, model_scope=train_scope
    )

    # Retrieve the default hyper-parameters for fine-tuning the model
    hyperparameters = hyperparameters.retrieve_default(
        model_id=train_model_id, model_version=train_model_version
    )

    # [Optional] Override default hyperparameters with custom values. This controls the duration of the training and the quality of the output.
    # If max_steps is too small, training will be fast but the the model will not be able to generate custom images for your usecase.
    # If max_steps is too large, training will be very slow.
    hyperparameters["max_steps"] = "200"

    training_job_name = name_from_base(f"jumpstart-example-{train_model_id}-fine-tune")

    # Create SageMaker Estimator instance
    sd_estimator = Estimator(
        role=aws_role,
        image_uri=train_image_uri,
        source_dir=train_source_uri,
        model_uri=train_model_uri,
        entry_point="transfer_learning.py",  # Entry-point file in source_dir and present in train_source_uri.
        instance_count=1,
        instance_type=training_instance_type,
        max_run=360000,
        hyperparameters=hyperparameters,
        output_path=s3_output_location,
        base_job_name=training_job_name,
        sagemaker_session=session
    )
    train_step_args = sd_estimator.fit({"training": train_s3_path})

    # Define training step
    train_step = TrainingStep(name='sd-fine-tune-training', step_args=train_step_args)

    # Retrieve the inference docker container uri
    inference_image_uri = image_uris.retrieve(
        region=aws_region,
        framework=None,  # automatically inferred from model_id
        image_scope="inference",
        model_id=train_model_id,
        model_version=train_model_version,
        instance_type=instance_type,
    )

    model = Model(
        image_uri=inference_image_uri,
        model_data="s3://sagemaker-eu-central-1-562760952310/jumpstart-example-sd-training/output/pipelines-tvxb7eab3kg5-sd-fine-tune-trainin-VRZBXL2HZN/output/model.tar.gz",
        sagemaker_session=session,
        role=aws_role
    )

    # Define create model step
    model_step_args = model.create(instance_type=instance_type)
    model_step = ModelStep(
        name='sd-fine-tuned-model',
        step_args=model_step_args
    )

    transformer = Transformer(
        model_name=model_step.properties.ModelName,
        instance_type=instance_type,
        instance_count=1,
        sagemaker_session=session,
        output_path=s3_output_data_path,
        strategy='SingleRecord',
        accept="application/json;jpeg"
    )

    transform_args = transformer.transform(
        s3_input_data_path, content_type="application/json", split_type="Line"
    )

    # Define transform step
    transform_step = TransformStep(name='stable_diffusion_txt2image_transform', step_args=transform_args, retry_policies=[
        StepRetryPolicy(
            exception_types=[
                StepExceptionTypeEnum.SERVICE_FAULT,
                StepExceptionTypeEnum.THROTTLING
            ],
            max_attempts=1
        )
    ])

    # Define the pipeline
    pipeline = Pipeline(name='sd-feature-ingest-pipeline-v2',
                        steps=[model_step, transform_step],
                        sagemaker_session=session)

    # Create the pipeline
    pipeline.upsert(role_arn=aws_role, description='local pipeline for synthetic data generation with stable diffusion')

    # Start a pipeline execution
    execution = pipeline.start()


