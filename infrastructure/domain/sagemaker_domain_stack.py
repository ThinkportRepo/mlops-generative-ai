from aws_cdk import Stack, Fn, Environment, CfnParameter
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy
from aws_cdk.aws_sagemaker import CfnDomain, CfnUserProfile
from aws_cdk.aws_ssm import StringParameter
from constructs import Construct


class SagemakerDomainStack(Stack):

    def __init__(self, scope: Construct, id: str, *, vpc=Vpc,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        role_sagemaker_studio_domain = Role(self, 'RoleForSagemakerMLOpsUsers',
                                            assumed_by=ServicePrincipal('sagemaker.amazonaws.com'),
                                            role_name="SagemakerMLOpsUserRole",
                                            managed_policies=[
                                                ManagedPolicy.from_managed_policy_arn(self,
                                                                                      id="SageMakerFullAccess",
                                                                                      managed_policy_arn="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess")
                                            ])
        sagemaker_domain_name = "SagemakerMLOpsDomain"

        vpc_id = StringParameter.value_for_string_parameter(self, "/mlops/vpc/id")
        public_subnet_ids = [StringParameter.value_for_string_parameter(self, "/mlops/vpc/public/subnet/id")]
        mlops_sagemaker_domain = CfnDomain(self, "MyCfnDomain",
                                           auth_mode="authMode",
                                           domain_name=sagemaker_domain_name,
                                           vpc_id=vpc_id,
                                           subnet_ids=public_subnet_ids,
                                           default_user_settings=CfnDomain.UserSettingsProperty(
                                               execution_role=role_sagemaker_studio_domain.role_name
                                           )
                                           )
        mlops_sagemaker_user_profile = CfnUserProfile(self, "MyCfnUserProfile",
                                                      domain_id=mlops_sagemaker_domain.attr_domain_id,
                                                      user_profile_name="mlops-user"
                                                      )
