import argparse
import os

import sagemaker
from sagemaker import LocalSession
from sagemaker.pytorch import PyTorch

# Construct the argument parser.
parser = argparse.ArgumentParser()

# hyperparameters sent by the client are passed as command-line arguments to the script.
parser.add_argument(
    '-e', '--epochs',
    type=int,
    default=10,
    help='Number of epochs to train our network for'
)
parser.add_argument(
    '-lr', '--learning-rate',
    type=float,
    dest='learning_rate',
    default=0.001,
    help='Learning rate for training the model'
)

parser.add_argument(
    '-m', '--model',
    type=str,
    default='mobilnetv3large',
    help='model name',
    choices=['mobilenetv3_large', 'shufflenetv2_x1_5', 'efficientnetb0']
)

args = vars(parser.parse_args())

if __name__ == "__main__":

    # Use the AWS region configured with the AWS CLI
    sess = LocalSession()
    sess.config = {'local': {'local_code': True}}
    region = sess.boto_region_name

    # This does not work on your local machine  because it doesn't have an IAM role
    # role = sagemaker.get_execution_role()
    role = 'arn:aws:iam::562760952310:role/SagemakerMLOpsUserRole'

    # Set local_mode to True to run the training script on the machine that runs this notebook
    local_mode = True

    if local_mode:
        instance_type = "local_gpu"
    else:
        instance_type = "ml.c4.xlarge"

    output_path = os.path.join('file://', '..', 'outputs', args['model'])
    est = PyTorch(
        entry_point="train.py",
        role=role,
        sagemaker_session=sess,
        framework_version="2.1.0",
        py_version="py310",
        instance_type=instance_type,
        instance_count=1,
        volume_size=250,
        output_path=output_path,
        hyperparameters={"epochs": args['epochs'], "learning-rate": args['learning_rate']}
    )

    loc_train = os.path.join('file://', '..', 'input', 'plantvillage dataset', 'color')
    loc_test = os.path.join('file://', '..', 'input', 'test')
    # The keys of the channels dictionary are passed to the training image, and it creates the environment variable
    # SM_CHANNEL_<key name>
    channels = {"training": loc_train, "testing": loc_test}

    # run the training script locally
    est.fit(inputs=channels)
