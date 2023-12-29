#!/bin/bash
S3_ARTIFACT_BUCKET="${__S3_ARTIFACT_BUCKET__}"


cd /home/ec2-user
pwd
#Update package information on your Amazon Linux instance
yum update -y
# Install virtualenv for isolated Python environments
pip3 install pipenv virtualenv
# Install MLflow and required dependencies using Pipenv
pipenv install mlflow awscli boto3 setuptools
# Activate the virtual environment
pipenv shell
# Start MLflow server with a specified S3 bucket for artifact storage
mlflow server -h 0.0.0.0 --backend-store-uri sqlite:///mlflow.db --default-artifact-root "${!S3_ARTIFACT_BUCKET}"
