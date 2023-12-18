from time import strftime, gmtime

import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup, logger
from experiments.image_generation.src.feature_store_utils import format_feature_defs

if __name__ == "__main__":
    # instantiate feature group
    sagemaker_session = sagemaker.Session()
    sagemaker_client = sagemaker_session.sagemaker_client
    region = sagemaker_session.boto_region_name
    role = sagemaker.get_execution_role()

    # This does not work on your local machine  because it doesn't have an IAM role
    # role = 'arn:aws:iam::562760952310:role/SagemakerMLOpsUserRole'

    output_bucket = sagemaker_session.default_bucket()
    feature_store_offline_s3_uri = f"s3://{output_bucket}/sd-offline-feature-store-s3-uri"

    feature_group_name = "sd-synth-plant-disease-images-feature-group-" + strftime("%d-%H-%M-%S", gmtime())
    feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=sagemaker_session)
    record_identifier_feature_name = "id"
    event_time_feature_name = "event_time"

    sd_synth_data_column_schemas = [
        {"name": "event_time", "type": "float"},
        {"name": "id", "type": "long"},
        {"name": "image", "type": "string"},
        {"name": "shape", "type": "string"},
        {"name": "class", "type": "string"}
    ]

    # create feature group config dictionary
    sd_fg_props = dict(
        FeatureGroupName=feature_group_name,
        FeatureDefinitions=format_feature_defs(sd_synth_data_column_schemas),
        RecordIdentifierFeatureName=record_identifier_feature_name,
        EventTimeFeatureName="event_time",
        OnlineStoreConfig={
            "EnableOnlineStore": False,
        },
        OfflineStoreConfig={
            "S3StorageConfig": {
                "S3Uri": feature_store_offline_s3_uri,
            },
            "DisableGlueTableCreation": False,
        },
        Description="Stable diffusion synthetic plant disease images feature group",
        Tags=[
            {"Key": "stage", "Value": "dev"},
        ],
    )

    try:
        response = sagemaker_client.create_feature_group(**sd_fg_props, RoleArn=role)
    except sagemaker_client.exceptions.ResourceInUse:
        logger.exception("The FeatureGroup exist already", exc_info=False)




