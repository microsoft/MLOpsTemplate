#import datetime, time
import os
from dotenv import load_dotenv
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication

# Load env variables, and ensure it accounts for various file paths
path_list = ['./variables.env', './../../variables.env', './sample.env']
for i in path_list:
    if os.path.isfile(i) is True:
        env_var = load_dotenv(i) # this equates to True irrespective if a file is found
        break

auth_dict = {
        "client_id":os.environ['CLIENT_ID'],
        "client_key":os.environ['CLIENT_SECRET'],
        "tenant_id":os.environ['TENANT_ID'],
        "sub_id": os.environ['SUB_ID'],
        "resource_group":os.environ['RESOURCE_GROUP'],
        "workspace_name":os.environ['WORKSPACE_NAME']
        }

# Get service principal
svc_pr = ServicePrincipalAuthentication(
        tenant_id=auth_dict['tenant_id'],
        service_principal_id=auth_dict['client_id'],
        service_principal_password=auth_dict['client_key'])

# Get the wrkspace config
ws =  Workspace(
        subscription_id=auth_dict['sub_id'],
        resource_group=auth_dict['resource_group'],
        workspace_name=auth_dict['workspace_name'],
        auth=svc_pr
        )
