import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from azureml.core.authentication import ServicePrincipalAuthentication
import argparse

from azureml.core import Workspace
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import requests
import json

def sample_score(tenant_id,client_id,client_secret,cluster_uri,db,scoring_uri,key,all_data_table_name,scoring_table,model_name, limit=100):
    query=f"""
    let exclude_list = {scoring_table}|where model_name == '{model_name}'| project file_path;
    {all_data_table_name}
    | where file_path !in (exclude_list) | sample 100000
    """
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    response = client.execute(db, query)
    result = dataframe_from_result_table(response.primary_results[0])
    print("result size ", result.shape)
    if result.shape[0]> limit:
        result = result.sample(limit)
    headers = {'Content-Type': 'application/json'}
    headers["Authorization"] = f"Bearer {key}"
    for _, row in result.iterrows():
        data = json.dumps({"data":{"datastore":row['file_path'].split("/")[3], "img_path":"/".join(row['file_path'].split("/")[5:])}})
        # Make the request and display the response
        requests.post(scoring_uri, data, headers=headers)
        
    return result



# run script
def main(args):
    secret = os.environ.get("SP_SECRET")
    client_id = os.environ.get("SP_ID")
    f=open(args.param_file)
    params =json.load(f)
    workspace_name = params['workspace_name']
    subscription_id = params['subscription_id']
    resource_group = params['resource_group']
    tenant_id = params["tenant_id"]
    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=client_id,service_principal_password=secret)
    ws = Workspace.get(workspace_name, subscription_id=subscription_id, resource_group=resource_group, auth=sp)    
    all_data_table_name=params["all_data_table_name"]
    scoring_table= params["scoring_table"]

    kv=ws.get_default_keyvault()

    database_name=params["database_name"]
    tenant_id = params["tenant_id"]
    client_id = params["client_id"]
    client_secret = kv.get_secret(client_id)

    # scoring_uri=params["scoring_uri"]
    # scoring_key_name= params["scoring_key_name"]
    # scoring_key = kv.get_secret(scoring_key_name)

    scoring_key = os.environ.get("SCORING_KEY")
    scoring_uri = os.environ.get("SCORING_URI")
    print("scoring uri ",scoring_uri)

    cluster_uri = params["cluster_uri"]
    model_name = params["model_name"]
    examples = sample_score(tenant_id,client_id,client_secret,cluster_uri,database_name,scoring_uri, scoring_key, all_data_table_name,scoring_table,model_name, limit=500)

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--param_file", type=str)

    # add arguments

    # parse args
    args = parser.parse_args()

    # return args
    return args

if __name__ == "__main__":
    # parse args
    args= parse_args()
    main(args)
