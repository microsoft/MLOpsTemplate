import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from core.monitoring.data_collector import Online_Collector
from azureml.core.authentication import ServicePrincipalAuthentication

import pandas as pd
from azureml.core import Workspace

def init_data(tenant_id, client_id,client_secret,cluster_uri,database_name,table_name, datastore_name, file_dataset_name, base_path):

    sample_data = pd.DataFrame({"file_path":['azureml://datastores/mltraining/paths/tmp/tmpev5bi0hz'],"label":['livingroom']})
    collector = Online_Collector(tenant_id, client_id,client_secret,cluster_uri,database_name,table_name, sample_data)
    dataset = ws.datasets[file_dataset_name]
    paths = dataset.to_path()
    file_paths=[]
    labels =[]
    for path in paths:
        file_paths.append(f'azureml://datastores/{datastore_name}/paths/{base_path+path}')
        labels.append(path.split("/")[-2])
    all_data = pd.DataFrame({"file_path":file_paths, "label":labels})
    collector.stream_collect(all_data)





# run script
if __name__ == "__main__":
    f=open("src/active_learning_cv/simulation/params.json")

    secret = os.environ.get("SP_SECRET")
    client_id = os.environ.get("SP_ID")
    tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=client_id,service_principal_password=secret)
    ws = Workspace.from_config(path="src/active_learning_cv/core", auth=sp)    
    kv=ws.get_default_keyvault()

    params =json.load(f)
    database_name=params["database_name"]
    tenant_id = params["tenant_id"]
    client_id = params["client_id"]
    client_secret = kv.get_secret(client_id)
    cluster_uri = params["cluster_uri"]
    base_path =params["base_path"]
    all_data_dataset=params["all_data_dataset"]
    datastore_name =params["datastore_name"]
    all_data_table_name= params["all_data_table_name"]
    client_secret = kv.get_secret(client_id)
    init_data(tenant_id, client_id,client_secret,cluster_uri,database_name,all_data_table_name, datastore_name, all_data_dataset, base_path)

