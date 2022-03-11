#Update deployment property with secret values
import argparse
from strictyaml import load
from azureml.core import Workspace, Model
from azureml.core.authentication import ServicePrincipalAuthentication
import os
def main(args):
    # read in data
    secret = os.environ.get("SP_SECRET")
    client_id = os.environ.get("SP_ID")
    tenant_id = os.environ.get("TENANT_ID")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=client_id,service_principal_password=secret)
    ws = Workspace.from_config(path="src/active_learning_cv/core", auth=sp)  
    with open(args.job_file, 'r') as yml_file:
        yml_content = yml_file.read()
        yml_obj =load(yml_content)
    with open(args.job_file, 'w') as yml_file:  
        current_version= Model(ws,args.model_name).version
        yml_obj["model"] =f"azureml:{args.model_name}:{current_version}"
        yml_obj["environment_variables"]["SP_ID"] =client_id
        yml_obj["environment_variables"]["SP_SECRET"] =secret
        yml_obj["environment_variables"]['TENANT_ID'] = tenant_id
        yml_obj["environment_variables"]['SUBSCRIPTION_ID'] = subscription_id
        yml_file.write(yml_obj.as_yaml())


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--job_file", type=str)
    parser.add_argument("--model_name", type=str)

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