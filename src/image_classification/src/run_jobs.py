import os
import yaml
from sagemaker import LocalSession
from sagemaker.estimator import Estimator

# distributed training
# https://docs.aws.amazon.com/sagemaker/latest/dg/distributed-training.html

if __name__ == "__main__":
    # AWS SESSION
    sess = LocalSession()
    # sess.config = {'local': {'local_code': True}}
    region = sess.boto_region_name

    # This does not work on your local machine  because it doesn't have an IAM role
    # role = sagemaker.get_execution_role()

    # CONFIG
    with open("../../../cfg/image_classification.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # IAM ROLE
    role = config['training']['iam_role']

    # Set local_mode to True to run the training script on the machine that runs this python script
    local_mode = config['training']['local_mode']

    if local_mode:
        loc_train = os.path.join('file://', '..', 'input_2', 'plantvillage dataset', 'color')
        loc_test = os.path.join('file://', '..', 'input_2', 'test')
        output_path = os.path.join('file://', '..', 'outputs', config['training']['hyperparameters']['model'])
    else:
        prefix_train = "/pytorch-plant-disease-classification/input/plantvillage/raw/train/"
        prefix_test = "/pytorch-plant-disease-classification/input/plantvillage/raw/test/"
        prefix_output = "/pytorch-plant-disease-classification/models/"
        loc_train = "s3://" + sess.default_bucket() + prefix_train
        loc_test = "s3://" + sess.default_bucket() + prefix_test
        output_path = "s3://" + sess.default_bucket() + prefix_output + config['training']['hyperparameters']['model']

    est = Estimator(
        entry_point=config['training']['entry_point'],
        source_dir=config['training']['source_dir'],
        role=role,
        image_uri=config['training']['image_uri'],
        sagemaker_session=sess,
        instance_type=config['training']['instance_type'],
        instance_count=config['training']['instance_count'],
        output_path=output_path,
        hyperparameters={"epochs": config['training']['hyperparameters']['epochs'],
                         "learning-rate": config['training']['hyperparameters']['lr'],
                         "momentum": config['training']['hyperparameters']['momentum'],
                         "tracking_uri": config['training']['hyperparameters']['tracking_uri'],
                         "model": config['training']['hyperparameters']['model']}
    )

    # The keys of the channels dictionary are passed to the training image, and it creates the environment variable
    # SM_CHANNEL_<key name>
    channels = {"training": loc_train, "testing": loc_test}

    # run the training script locally
    est.fit(inputs=channels)
