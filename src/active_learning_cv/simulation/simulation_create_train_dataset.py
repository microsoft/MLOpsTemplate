import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
import argparse
from azureml.core import Workspace
import pandas as pd
import os
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import json
from azureml.core import Dataset
from azureml.data import DataType
from sklearn.model_selection import train_test_split
def least_confidence_examples(tenant_id,client_id,client_secret,cluster_uri,db, scoring_table,all_data_dataset, limit=200, prob_limit=25):
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query= f"""
    let upper_prob= toscalar({scoring_table}| summarize percentile(prob,{prob_limit}));
    {scoring_table}|where prob < upper_prob | sort by prob asc| limit {limit}
    | join {all_data_dataset} on file_path | project file_path, label, prediction, prob, probs
    """
    response = client.execute(db, query)
    return dataframe_from_result_table(response.primary_results[0])
    

def create_aml_label_dataset(datastore, target_path, input_ds, dataset_name):
    # sample json line dictionary
    json_line_sample = {
        "image_url": "AmlDatastore://"
        + "some_ds"
        + "/",
        "label": "",
    }
    new_version = ws.datasets[dataset_name].version+1
    annotations_file =dataset_name+f"_v_{new_version}"+".jsonl"


    with open(annotations_file, "w") as train_f:
        for _, row in input_ds.iterrows():
            file_path ="/".join(row["file_path"].split("/")[5:])
            json_line = dict(json_line_sample)
            json_line["image_url"] = "AmlDatastore://"+datastore.name+"/"+file_path
            json_line["label"] = row['label']
            train_f.write(json.dumps(json_line) + "\n")
    datastore.upload_files(files=[annotations_file], target_path=target_path,overwrite=True)


    dataset = Dataset.Tabular.from_json_lines_files(
        path=datastore.path(f"{target_path}/{annotations_file}"),
        set_column_types={"image_url": DataType.to_stream(datastore.workspace)},
    )
    #the goal is to use the same name but with new version, each version refer to the label dataset name 
    dataset = dataset.register(
        workspace=datastore.workspace, name=dataset_name,create_new_version=True, description
        =dataset_name
    )
    print("register  ", dataset_name)

# run script
if __name__ == "__main__":
    # parse args
    ws = Workspace.from_config()

    kv=ws.get_default_keyvault()
    f=open("src/active_learning_cv/simulation/params.json")
    params =json.load(f)
    database_name=params["database_name"]
    tenant_id = params["tenant_id"]
    client_id = params["client_id"]
    client_secret = kv.get_secret(client_id)
    cluster_uri = params["cluster_uri"]
    base_path =params["base_path"]
    all_data_table_name=params["all_data_table_name"]
    datastore_name =params["datastore_name"]
    scoring_table= params["scoring_table"]
    jsonl_target_path= params["jsonl_target_path"]

    train_dataset_name= params["train_dataset"]
    val_dataset_name= params["val_dataset"]


    client_secret = kv.get_secret(client_id)
    examples = least_confidence_examples(tenant_id,client_id,client_secret,cluster_uri,database_name, scoring_table,all_data_table_name, limit=200, prob_limit=25)
    print("dataset size ", examples.shape)
    train_dataset, val_dataset= train_test_split(examples, test_size=0.2)
    datastore = ws.datastores[datastore_name]

    create_aml_label_dataset(datastore, jsonl_target_path,  train_dataset,train_dataset_name)
    create_aml_label_dataset(datastore, jsonl_target_path,  val_dataset,val_dataset_name)

    # run main function
    # main(args)