import os

from sagemaker.dataset_definition import DatasetDefinition, AthenaDatasetDefinition
from sagemaker.processing import ProcessingInput

from experiments.image_classification.src.datasets import get_datasets, get_data_loaders

if __name__ == '__main__':
    loc_train = os.path.join('..', '..', 'input', 'plantvillage dataset', 'color')
    # Load the training and validation datasets.
    dataset_train, dataset_valid, dataset_classes = get_datasets(loc_train)
    print(f"[INFO]: Number of training images: {len(dataset_train)}")
    print(f"[INFO]: Number of validation images: {len(dataset_valid)}")
    print(f"[INFO]: Classes: {dataset_classes}")
    # Load the training and validation data loaders.
    train_loader, valid_loader = get_data_loaders(dataset_train, dataset_valid)


    data_sources = [
        ProcessingInput(
            input_name="athena_dataset",
            dataset_definition=DatasetDefinition(
                local_path=athena_data_path,
                data_distribution_type="FullyReplicated",
                athena_dataset_definition=AthenaDatasetDefinition(
                    **generate_query(kwargs, sagemaker_session=sagemaker_session),
                    output_s3_uri=Join(
                        on="/",
                        values=[
                            "s3:/",
                            default_bucket,
                            prefix,
                            ExecutionVariables.PIPELINE_EXECUTION_ID,
                            "raw_dataset",
                        ],
                    ),
                    output_format="PARQUET",
                ),
            ),
        )
    ]
