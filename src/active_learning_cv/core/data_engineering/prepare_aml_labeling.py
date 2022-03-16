import os
import argparse
from azureml.core import Workspace
import pandas as pd
import os
import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import shutil
from azureml.core import Run
from data_selection import *


def main(args):
    # read in data


    tenant_id = args["tenant_id"]
    run = Run.get_context()
    ws = run.experiment.workspace 
    client_id = args["client_id"]
    kv=ws.get_default_keyvault()
    client_secret= kv.get_secret(client_id)
    database_name=args["database_name"]
    cluster_uri = args["cluster_uri"]
    datastore_name =args["datastore_name"]
    scoring_table= args["scoring_table"]
    examples_limit = args["examples_limit"]
    prob_limit = args["prob_limit"]
    model_name= args["model_name"]
    if args.strategy == "SMALLEST_MARGIN_UNCERTAINTY":
        examples = smallest_margin_uncertainty(tenant_id,client_id,client_secret,cluster_uri,database_name, scoring_table, model_name, limit=examples_limit, prob_limit=prob_limit)
    elif args.strategy == "ENTROPHY_SAMPLING":
        examples = entrophy_sampling(tenant_id,client_id,client_secret,cluster_uri,database_name, scoring_table,model_name, limit=examples_limit, prob_limit=prob_limit)
    else:
        examples = least_confidence(tenant_id,client_id,client_secret,cluster_uri,database_name, scoring_table, model_name, limit=examples_limit, prob_limit=prob_limit)

    source="./download_img"
    os.makedirs(source, exist_ok=True)
    local_files_list =[]
    for _,row in examples.iterrows():
        file_path = row['file_path']
        datastore_name = file_path.split("/")[3]
        file_path = "/".join(file_path.split("/")[5:])
        local_files_list.append(os.path.join(source,file_path))
        ws.datastores[datastore_name].download(source,prefix= file_path)
    datastore = ws.datastores[args.datastore]
    datastore.upload_files(files = local_files_list, target_path= args.path, overwrite=True)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--tenant_id", type=str)
    parser.add_argument("--client_id", type=str)
    parser.add_argument("--cluster_uri", type=str)
    parser.add_argument("--database_name", type=str)
    parser.add_argument("--database_name", type=str)
    parser.add_argument("--datastore_name", type=str) 
    parser.add_argument("--scoring_table", type=str) 
    parser.add_argument("--cluster_uri", type=str)
    parser.add_argument("--strategy", default ="LEAST_CONFIDENCE", type=str)
    parser.add_argument("--examples_limit", default =100, type=int)
    parser.add_argument("--prob_limit", default =0.25, type=float)

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
