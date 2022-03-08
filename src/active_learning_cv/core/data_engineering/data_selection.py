import os
import argparse
from azureml.core import Workspace
import pandas as pd
import os
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import shutil
from azureml.core import Run

def least_confidence_examples(tenant_id,client_id,client_secret,cluster_uri,db, scoring_table, limit=200, prob_limit=25):
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query= f"""
    let upper_prob= toscalar({scoring_table}| summarize percentile(prob,{prob_limit}));
    let latest_model_version = toscalar({scoring_table}| summarize last_model_version = max(model_version));
    {scoring_table}|where prob < upper_prob and model_version == latest_model_version| project file_path, label, prediction, prob, probs | sort by prob asc| limit {limit}
    """
    response = client.execute(db, query)

    return dataframe_from_result_table(response.primary_results[0])

def main(args):
    # read in data
    client_secret = os.environ.get("SP_SECRET")
    client_id = os.environ.get("SP_ID")
    f=open("src/active_learning_cv/core/data_engineering/params.json")
    params =json.load(f)
    tenant_id = params["tenant_id"]
    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, service_principal_id=client_id,service_principal_password=secret)
    ws = Workspace.from_config(path="src/active_learning_cv/core", auth=sp)    
    database_name=params["database_name"]
    cluster_uri = params["cluster_uri"]
    datastore_name =params["datastore_name"]
    scoring_table= params["scoring_table"]
    examples = least_confidence_examples(tenant_id,client_id,client_secret,cluster_uri,database_name, scoring_table, limit=100, prob_limit=25)
    source="./download_img"
    os.makedirs(source, exist_ok=True)
    local_files_list =[]
    for _,row in examples.iterrows():
        file_path = row['file_path']
        datastore_name = file_path.split("/")[3]
        file_path = "/".join(file_path.split("/")[5:])
        # file_name = file_path.split("/")[-1]
        local_files_list.append(os.path.join(source,file_path))
        ws.datastores[datastore_name].download(source,prefix= file_path)
    print("os list ", os.listdir(source))
    datastore = ws.datastores[args.datastore]
    datastore.upload_files(files = local_files_list, target_path= args.path, overwrite=True)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--tenant_id", type=str)
    parser.add_argument("--client_id", type=str)
    parser.add_argument("--datastore", type=str) #input file dataset name for the labeling process
    parser.add_argument("--path", type=str) #input file dataset name for the labeling process

    parser.add_argument("--cluster_uri", type=str)
    parser.add_argument("--db", type=str)

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