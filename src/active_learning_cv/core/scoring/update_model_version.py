import argparse
from strictyaml import load
from azureml.core import Workspace, Model
from azureml.core.authentication import ServicePrincipalAuthentication
import os
def main(args):
    # read in data
    secret = os.environ.get("SP_SECRET")
    client_id = os.environ.get("SP_ID")
    tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"

    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=client_id,service_principal_password=secret)
    ws = Workspace.from_config(auth=sp)  
    current_version= Model(ws,args.model_name).version
    with open(args.job_file, 'r') as yml_file:
        yml_content = yml_file.read()
        yml_obj =load(yml_content)
    with open(args.job_file, 'w') as yml_file:
        yml_obj["model"] =f"azureml:{args.model_name}:{current_version}"
        yml_file.write(yml_obj.as_yaml())


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--job_file", type=str)
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--client_id", type=str)

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