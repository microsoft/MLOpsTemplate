import os
import argparse
import pandas as pd
from azureml.core import Workspace
import pandas as pd
import json
import os
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table


class Drift_Analysis():
    def __init__(self, tenant_id, client_id, client_secret, cluster_uri,db):
        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
        self.client = KustoClient(KCSB_DATA)
        self.db =db
    def query(self, query):
        response = self.client.execute(self.db, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe


def test_kusto_query(tenant_id,client_id,client_secret,cluster_uri,db ):
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query= """
    
    """
    response = client.execute(db, query)
    dataframe = dataframe_from_result_table(response.primary_results[0])
def main(args):
    # read in data
    ws = Workspace.from_config()
    kv = ws.get_default_keyvault()
    client_secret=kv.get_secret(args.client_id)
    dataset = ws.datasets[args.dataset]
    with dataset.mount() as mount_context:
    # list top level mounted files and folders in the dataset
        os.listdir(mount_context.mount_point)


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--tenant_id", type=str)
    parser.add_argument("--client_id", type=str)
    parser.add_argument("--dataset", type=str) #input file dataset name for the labeling process
    parser.add_argument("--ds_prefix", type=str)

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