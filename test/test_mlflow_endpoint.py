import json
import logging
import os

import boto3
import cv2
import flask
import mlflow
import numpy as np
import requests
import torch
import torchvision.transforms as transforms
import yaml
from torch.nn import functional as F
import mlflow.pyfunc.scoring_server as pyfunc_scoring_server

IMAGE_RESIZE = 224


# https://github.com/mlflow/mlflow/issues/4142
# https://github.com/mlflow/mlflow/releases/tag/v1.14.0
# https://github.com/mlflow/mlflow/pull/3894/files#diff-3f50f710c7971efdf17ce59af95f1af515200cbd62e7c62dedb44107a51edcb9

def get_test_transform(image_size):
    test_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    return test_transform


def load_files(path):
    """
    Score images on the local path with MLflow model deployed at given uri and port.

    :param path: Path to a single image file or a directory of images.
    :return: data.
    """
    if os.path.isdir(path):
        filenames = [
            os.path.join(path, x) for x in os.listdir(path) if os.path.isfile(os.path.join(path, x))
        ]
    else:
        filenames = [path]

    return filenames


def test_api(url, payload):
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()  # if status !=200 raise exception
        logging.info("SUCCESS: THE API WORKS!")

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def check_status(app_name):
    sage_client = boto3.client('sagemaker', region_name=config['endpoint']['aws_region'])
    endpoint_description = sage_client.describe_endpoint(EndpointName=app_name)
    endpoint_status = endpoint_description['EndpointStatus']
    return endpoint_status


def query_endpoint(app_name, input_json):
    client = boto3.session.Session().client('sagemaker-runtime', config['endpoint']['aws_region'])

    response = client.invoke_endpoint(
        EndpointName = app_name,
        Body = input_json,
        ContentType = 'application/json'#'; format=pandas-split',
        )

    preds = response['Body'].read().decode('ascii')
    preds = json.loads(preds)
    print('Received response: {}'.format(preds))
    return preds


if __name__ == '__main__':
    # CONFIG
    with open("../cfg/model_deploy.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    app_name = config['endpoint']['name']

    # print("Application status is {}".format(check_status(app_name)))

    # rest_endpoint = config['endpoint']['http_uri']

    # # GET ENDPOINT NAME FROM CONFIG AND DEPLOYMENT ENVIRONMENT
    # logging.info("GET API NAME FROM CONFIG AND DEPLOYMENT ENVIRONMENT")
    # api_name = f"{config['model']['name']}-{config['model']['version']}-{os.environ['DEPLOYMENT_ENV']}"
    #
    # mlflow.set_tracking_uri(config['model']['tracking_uri'])
    #
    # logged_model = config['model']['model_uri']
    #
    # # Load model as a PyFuncModel.
    # loaded_model = mlflow.pyfunc.load_model(logged_model)

    # print(loaded_model)
    print(load_files("Apple___Cedar_apple_rust"))
    filenames = load_files("Apple___Cedar_apple_rust")
    transform = get_test_transform(IMAGE_RESIZE)
    for image_path in filenames:
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = transform(image)
        image = torch.unsqueeze(image, 0)
        image = image.detach().numpy()
        tfserving_input = {"instances": image}
        tfserving_input_as_json = json.dumps(tfserving_input,
                               cls=NumpyEncoder)
        data = flask.request.data.decode("utf-8")

        # pred = query_endpoint(app_name, tfserving_input_as_json)
        # print(pred)
    #
    #
    #     # result = pyfunc_scoring_server.parse_tf_serving_input(tfserving_input)
    #     #
    #     pred = test_api(rest_endpoint, tfserving_input_as_json)
    #
    #     # Softmax probabilities.
    #     predictions = F.softmax(torch.from_numpy(pred), dim=1)
    #     print(predictions)
    #
    #     # Predicted class number.
    #     output_class = np.argmax(predictions)
    #
    #     print(output_class)
