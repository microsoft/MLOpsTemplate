from sklearn.model_selection import train_test_split
import json
import pandas as pd
from azureml.core import Dataset, Run
from azureml.data import DataType

#  """
#  This class init accepts a AML dataset
 
#  """
class Active_Learning_Train:

    def __init__(self, model_name, *args, **kwargs):
        if "ws" in kwargs:
            self.ws = kwargs['ws']
            self.compute_target =  self.ws.compute_targets[kwargs['compute_cluster']]
            self.datastore =self.ws.datastores[kwargs['datastore_name']]
            self.ds_prefix=kwargs['ds_prefix']
            self.target_path= kwargs['target_path']
            self.experiment_name = kwargs['experiment_name']
        self.model_name = model_name

    def train(self, *arg, **kwargs):
        pass
    def _retrieve_dataset(self, ws,ds_prefix, get_net_new=False,test_size=0.2):
        #get_net_new is the indicator to get net new label dataset. Otherwise, entire dataset is used.
        datasets = [dataset[0] for dataset in ws.datasets.items()]
        label_datasets = []
        for dataset in datasets:
            if ds_prefix == "_".join(dataset.split("_")[:-2]):
                label_datasets.append(dataset)
        label_datasets.sort(reverse=True)
        current_dataset =ws.datasets[label_datasets[0]]
        current_dataset_name=current_dataset.name
        current_dataset = current_dataset.to_pandas_dataframe().set_index("image_url")
        if (len(label_datasets)>1) and get_net_new:
            last_dataset =ws.datasets[label_datasets[1]].to_pandas_dataframe().set_index("image_url")
            new_dataset =pd.concat([current_dataset,last_dataset]).drop_duplicates(keep=False)
        else:
            new_dataset= current_dataset
        train_dataset, val_dataset= train_test_split(new_dataset, test_size=test_size, stratify=new_dataset['label'])
        return train_dataset, val_dataset,current_dataset_name
    def _create_aml_label_dataset(self, datastore, target_path, input_ds, dataset_name, prefix, register=True):
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
        base_dataset_name ="_".join(dataset_name.split("_")[:-2])
        if register:
            dataset = dataset.register(
                workspace=datastore.workspace, name=base_dataset_name,create_new_version=True, description
                =dataset_name
            )
            print("register  ", base_dataset_name)
        return dataset
    def train_validation_split(self,ws,datastore, ds_prefix,target_path):
        train_dataset, val_dataset, current_dataset_name =self._retrieve_dataset(ws,ds_prefix, test_size=0.2)
        train_ds = self._create_aml_label_dataset(datastore = datastore , target_path=target_path, input_ds = train_dataset,dataset_name =current_dataset_name, prefix="train")
        val_ds = self._create_aml_label_dataset(datastore = datastore, target_path= target_path, input_ds = val_dataset,dataset_name =current_dataset_name, prefix="val")
        return train_ds, val_ds
