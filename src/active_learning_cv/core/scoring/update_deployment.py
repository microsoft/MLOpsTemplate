#Update deployment property with secret values
import argparse
from strictyaml import load
from azureml.core import Workspace, Model
from azureml.core.authentication import ServicePrincipalAuthentication
import os
import json
def main(args):
    # read in data
    secret = os.environ.get("SP_SECRET")
    client_id = os.environ.get("SP_ID")
    f=open(args.param_file)
    params =json.load(f)
    subscription_id = params['subscription_id']
    resource_group = params['resource_group']
    workspace_name = params['workspace_name']
    tenant_id = params['tenant_id']

    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=client_id,service_principal_password=secret)
    ws = Workspace(subscription_id=subscription_id, resource_group=resource_group, workspace_name=workspace_name, auth=sp)
    model_name = params['model_name']
    scoring_table = params['scoring_table']
    cluster_uri = params['cluster_uri']
    database_name = params['database_name']

    with open(args.job_file, 'r') as yml_file:
        yml_content = yml_file.read()
        yml_obj =load(yml_content)
    with open(args.job_file, 'w') as yml_file:  
        current_version= Model(ws,model_name).version
        yml_obj["model"] =f"azureml:{model_name}:{current_version}"
        yml_obj["environment_variables"]["SP_ID"] =client_id
        yml_obj["environment_variables"]["SP_SECRET"] =secret
        yml_obj["environment_variables"]['TENANT_ID'] = tenant_id
        yml_obj["environment_variables"]['SUBSCRIPTION_ID'] = subscription_id
        yml_obj["environment_variables"]['CLUSTER_URI'] = cluster_uri
        yml_obj["environment_variables"]['DATABASE_NAME'] = database_name
        yml_obj["environment_variables"]['TABLE_NAME'] = scoring_table

        yml_file.write(yml_obj.as_yaml())


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--job_file", type=str)
    parser.add_argument("--param_file", type=str)

    # parse args
    args = parser.parse_args()

    # return args
    return args


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)