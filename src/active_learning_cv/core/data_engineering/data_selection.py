import os
import argparse
from azureml.core import Workspace
import pandas as pd
import os
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import shutil
from azureml.core import Run
def least_confidence_examples(tenant_id,client_id,client_secret,cluster_uri,db, limit=100):
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query= f"""
    let upper_prob= toscalar(image_logging| summarize percentile(prob,20));
    image_logging|where prob < upper_prob | sort by prob asc| limit {limit}
    """
    response = client.execute(db, query)
    return dataframe_from_result_table(response.primary_results[0])
    

def main(args):
    # read in data
    run = Run.get_context()
    ws = run.experiment.workspace
    kv = ws.get_default_keyvault()
    client_secret=kv.get_secret(args.client_id)
    examples = least_confidence_examples(args.tenant_id,args.client_id,client_secret,args.cluster_uri,args.db, limit=10)
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