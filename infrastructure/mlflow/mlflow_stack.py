# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import logging

from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_rds as rds,
    aws_iam as iam,
    aws_secretsmanager as sm,
    Stack,
    Aws,
    RemovalPolicy
)
from constructs import Construct
from aws_cdk.aws_ec2 import Vpc


class MLflowStack(Stack):
    def __init__(self, scope: Construct, id: str, *, vpc=Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # ==============================
        # ======= CFN PARAMETERS =======
        # ==============================
        db_name = "mlflowdb"
        port = 3306
        username = "master"
        bucket_name = f"mlflow-artifacts-{Aws.ACCOUNT_ID}"
        cluster_name = "mlflow"
        service_name = "mlflow"

        # ==================================================
        # ================== SECRET ========================
        # ==================================================
        db_password_secret = sm.Secret(
            scope=self,
            id="DBSECRET",
            secret_name="dbPassword",
            generate_secret_string=sm.SecretStringGenerator(
                password_length=20, exclude_punctuation=True
            ),
        )

        # ==================================================
        # ================= S3 BUCKET ======================
        # ==================================================
        artifact_bucket = s3.Bucket(
            scope=self,
            id="ARTIFACTBUCKET",
            bucket_name=bucket_name,
            public_read_access=False,
        )
        # # ==================================================
        # # ================== DATABASE  =====================
        # # ==================================================
        # Creates a security group for AWS RDS
        sg_rds = ec2.SecurityGroup(
            scope=self, id="SGRDS", vpc=vpc, security_group_name="sg_rds"
        )
        # Adds an ingress rule which allows resources in the VPC's CIDR to access the database.
        sg_rds.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/24"), connection=ec2.Port.tcp(port)
        )

        database = rds.DatabaseInstance(
            scope=self,
            id="MYSQL",
            database_name=db_name,
            port=port,
            credentials=rds.Credentials.from_username(
                username=username, password=db_password_secret.secret_value
            ),
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_8_0_32
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL
            ),
            vpc=vpc,
            security_groups=[sg_rds],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            removal_policy=RemovalPolicy.SNAPSHOT,
            deletion_protection=True,
        )


