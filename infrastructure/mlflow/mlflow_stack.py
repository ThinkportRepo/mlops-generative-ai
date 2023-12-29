from aws_cdk import CfnOutput, Stack, Fn, Aws
import aws_cdk.aws_iam as iam
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_s3 as s3
from aws_cdk.aws_ssm import StringParameter
from constructs import Construct

bucket_name = f"mlflow-artifacts-{Aws.ACCOUNT_ID}"
linux_ami = ec2.GenericLinuxImage({
    "eu-central-1": "ami-02da8ff11275b7907"
})
#
# mappings = {"__S3_ARTIFACT_BUCKET__": bucket_name}
#
# with open("user_data/user_data.sh") as f:
#     user_data = Fn.sub(f.read(), mappings)


class MLFlowStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # ==================================================
        # ================= S3 BUCKET ======================
        # ==================================================
        artifact_bucket = s3.Bucket(
            scope=self,
            id="mlflow-s3-artifact-store",
            bucket_name=bucket_name,
            public_read_access=False,
        )
        # ==================================================
        # ================= EC2 INSTANCE ===================
        # ==================================================
        # vpc_id = StringParameter.value_for_string_parameter(self, "/mlops/vpc/id")
        ec2_type = StringParameter.value_for_string_parameter(self, "/mlops/mlflow/ec2_type")
        key_name = StringParameter.value_for_string_parameter(self, "/mlops/mlflow/key_name")

        # The code that defines your stack goes here
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id="vpc-0bd52673debc4ba1c")
        # Instance Role and SSM Managed Policy
        ec2_role = iam.Role(self, "MLFlowTrackinServerRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        ec2_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        ec2_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))

        host = ec2.Instance(self, "mlflow-tracking-server",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_type),
                            instance_name="mlflow-tracking-server",
                            machine_image=linux_ami,
                            vpc=vpc,
                            key_name=key_name,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PUBLIC),
                            role=ec2_role
                            # user_data=ec2.UserData.custom(user_data)
                            )
        # ec2.Instance has no property of BlockDeviceMappings, add via lower layer cdk api:
        host.instance.add_property_override("BlockDeviceMappings", [{
            "DeviceName": "/dev/xvda",
            "Ebs": {
                "VolumeSize": "10",
                "VolumeType": "io1",
                "Iops": "150",
                "DeleteOnTermination": "false"
            }
        }])  # by default VolumeType is gp2, VolumeSize 8GB

        host.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22), "Allow ssh from internet")
        host.connections.allow_from_any_ipv4(
            ec2.Port.tcp(5000), "Allow http from internet")
        host.node.add_dependency(artifact_bucket)

        CfnOutput(self, "Output",
                  value=host.instance_public_ip)
