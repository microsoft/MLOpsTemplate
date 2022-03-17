import json
import sys
import os
import argparse
from strictyaml import load

sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from core.monitoring.data_collector import Online_Collector
from azureml.core.authentication import ServicePrincipalAuthentication
import time
import pandas as pd
from azureml.core import Workspace
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
def init_data(tenant_id, client_id,client_secret,cluster_uri,database_name,all_data_table_name, datastore_name, file_dataset_name, base_path):

    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query= f"""
    {all_data_table_name}|limit 1
    """
    try:
        response = client.execute(database_name, query)
    except:
        print("tables not created, go on creating tables")
        #setup all_examples_table
        sample_data_all_table = pd.DataFrame({"file_path":['azureml://datastores/mltraining/paths/tmp/tmpev5bi0hz'],"label":['livingroom']})
        collector = Online_Collector(tenant_id, client_id,client_secret,cluster_uri,database_name,all_data_table_name, sample_data_all_table)
        dataset = ws.datasets[file_dataset_name]
        paths = dataset.to_path()
        file_paths=[]
        labels =[]
        for path in paths:
            file_paths.append(f'azureml://datastores/{datastore_name}/paths/{base_path+path}')
            labels.append(path.split("/")[-2])
        all_data = pd.DataFrame({"file_path":file_paths, "label":labels})
        t=0
        while(t<10):
            try:
                collector.stream_collect(all_data)
                break
            except:
                #tables are not ready, retry
                time.sleep(20)
            t+=1

def update_aml_yml(train_yml, param_file):
    src/active_learning_cv/simulation/params_random.json
    param_file = "/".join(param_file.split("/")[-2:])
    #Update endpoint yml file
    with open(train_yml, 'r') as yml_file:
        yml_content = yml_file.read()
        train_yml_obj =load(yml_content)
    with open(train_yml, 'w') as yml_file:  
        train_yml_obj['param_file'] = param_file
        yml_file.write(train_yml_obj.as_yaml())

def main(args):
    f=open(args.param_file)
    params =json.load(f)
    # if args.strategy: #straetgy is provided from the command so it will be used to overwrite the values in params json file
    #     params.strategy = strategy
    #     if args.strategy == 'SMALLEST_MARGIN_UNCERTAINTY':
    #         params.model_name = "ActiveLearning_CV_SMU"
    #         params.train_dataset = "active_learning_cv_smu"
    #     if args.strategy == 'ENTROPHY_SAMPLING':
    #         params.model_name = "ActiveLearning_CV_SMU"
    #         params.train_dataset = "active_learning_cv_smu"
    #     if args.strategy == 'SMALLEST_MARGIN_UNCERTAINTY':
    #         params.model_name = "ActiveLearning_CV_SMU"
    #         params.train_dataset = "active_learning_cv_smu"

    secret = os.environ.get("SP_SECRET")
    client_id = os.environ.get("SP_ID")
    tenant_id = params["tenant_id"]
    workspace_name = params['workspace_name']
    subscription_id = params['subscription_id']
    resource_group = params['resource_group']
    update_aml_yml("src/active_learning_cv/core/training/cv_automl_train.yml", args.param_file):


    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=client_id,service_principal_password=secret)
    ws = Workspace.get(workspace_name, subscription_id=subscription_id, resource_group=resource_group, auth=sp)    
    kv=ws.get_default_keyvault()
    database_name=params["database_name"]
    cluster_uri = params["cluster_uri"]
    base_path =params["base_path"]
    all_data_dataset=params["all_data_dataset"]
    datastore_name =params["datastore_name"]
    all_data_table_name= params["all_data_table_name"]
    init_data(tenant_id, client_id,secret,cluster_uri,database_name,all_data_table_name, datastore_name, all_data_dataset, base_path)


# run script

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--param_file", type=str)
    parser.add_argument("--strategy", type=str)

    # add arguments

    # parse args
    args = parser.parse_args()

    # return args
    return args

if __name__ == "__main__":
    # parse args
    args= parse_args()
    main(args)
