import os
import argparse
import pandas as pd
from azureml.core import Workspace
import pandas as pd
from sklearn.model_selection import train_test_split
import json
import os
from azureml.core import Dataset
from azureml.data import DataType
# define functions
def get_net_new_dataset(ws,ds_prefix ):
    datasets = [dataset[0] for dataset in ws.datasets.items()]
    label_datasets = []
    for dataset in datasets:
        if ds_prefix in dataset:
            label_datasets.append(dataset)
    label_datasets.sort(reverse=True)
    if len(label_datasets)>1:
        current_dataset =ws.datasets[label_datasets[0]]
        current_dataset_name=current_dataset.name
        current_dataset = current_dataset.to_pandas_dataframe().set_index("image_url")
        last_dataset =ws.datasets[label_datasets[1]].to_pandas_dataframe().set_index("image_url")
        new_dataset =pd.concat([current_dataset,last_dataset]).drop_duplicates(keep=False)
    else:
        new_dataset= label_datasets[0]
    train_dataset, val_dataset= train_test_split(new_dataset, test_size=0.2, stratify=new_dataset['label'])
    return train_dataset, val_dataset,current_dataset_name
def create_aml_label_dataset(datastore, target_path, input_ds, dataset_name, prefix):
    dataset_name = prefix+"_"+dataset_name
    annotations_file =dataset_name+".jsonl"
# sample json line dictionary
    json_line_sample = {
        "image_url": "AmlDatastore://"
        + "some_ds"
        + "/",
        "label": "",
    }

    with open(annotations_file, "w") as train_f:
        for index, row in input_ds.iterrows():
            json_line = dict(json_line_sample)
            json_line["image_url"] = "AmlDatastore://"+str(index)
            json_line["label"] = row['label']
            train_f.write(json.dumps(json_line) + "\n")
    datastore.upload_files(files=[annotations_file], target_path=target_path,overwrite=True)


    dataset = Dataset.Tabular.from_json_lines_files(
        path=datastore.path(f"{target_path}/{annotations_file}"),
        set_column_types={"image_url": DataType.to_stream(datastore.workspace)},
    )
    #the goal is to use the same name but with new version, each version refer to the label dataset name 
    original_dataset_name ="_".join(dataset_name.split("_")[:-2])
    dataset = dataset.register(
        workspace=datastore.workspace, name=original_dataset_name,create_new_version=True, description
        =dataset_name
    )
def main(args):
    # read in data
    ws = Workspace.from_config()
    train_dataset, val_dataset, current_dataset_name =get_net_new_dataset(ws,args.ds_prefix)
    datastore =ws.datastores[args.datastore]
    create_aml_label_dataset(datastore = datastore , target_path=args.target_path, input_ds = train_dataset,dataset_name =current_dataset_name, prefix="train")
    create_aml_label_dataset(datastore = datastore, target_path= args.target_path, input_ds = val_dataset,dataset_name =current_dataset_name, prefix="val")

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--target_path", type=str)
    parser.add_argument("--datastore", type=str)
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