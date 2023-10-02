from aws_cdk import Stack, Fn, Environment, CfnParameter
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy
from aws_cdk.aws_sagemaker import CfnDomain, CfnUserProfile
from constructs import Construct


class SagemakerDomainStack(Stack):

    def __init__(self, scope: Construct, id: str,
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

        # ==============================
        # ======= CFN PARAMETERS =======
        # ==============================
        account_param = CfnParameter(scope=self, id="account_id", type="String")
        region_param = CfnParameter(scope=self, id="aws_region", type="String")

        vpc_id = Fn.import_value("VPCId")
        vpc = Vpc.from_lookup(self, "VPC",
                              vpc_id=self.node.try_get_context(vpc_id),
                              owner_account_id=account_param.value_as_string,
                              region=region_param.value_as_string
                              )
        public_subnet_ids = [public_subnet.subnet_id for public_subnet in vpc.public_subnets]

        mlops_sagemaker_domain = CfnDomain(self,
                                           domain_name=sagemaker_domain_name,
                                           vpc_id=vpc_id,
                                           subnet_ids=public_subnet_ids,
                                           default_user_settings=CfnDomain.UserSettingsProperty(
                                               execution_role=role_sagemaker_studio_domain.role_name
                                           )
                                           )
        mlops_sagemaker_user_profile = CfnUserProfile(self,
                                                      domain_id=mlops_sagemaker_domain.attr_domain_id,
                                                      user_profile_name="mlops-user"
                                                      )
