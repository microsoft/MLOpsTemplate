import os
import argparse

import pandas as pd
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core import Workspace
from azureml.automl.core.shared.constants import ImageTask
from azureml.train.automl import AutoMLImageConfig
from azureml.train.hyperdrive import GridParameterSampling, choice
from azureml.core import Experiment, Run, Model, Dataset
from azureml.train.automl.run import AutoMLRun

from strictyaml import load




# define functions
def main(args):
    # read in data
    run = Run.get_context()
    ws = run.experiment.workspace
    experiment_name = args.experiment_name
    compute_target = ws.compute_targets[args.compute_cluster]
    training_dataset = ws.datasets[args.training_dataset]
    validation_dataset = ws.datasets[args.validation_dataset]
    ds =ws.datastores[args.datastore]
    os.makedirs("checkpoints", exist_ok=True)
    try:
        last_model = Model(ws,args.model_name)
        last_run_id = last_model.run_id
        print("last run exists, pull the last run_id ", last_run_id)
        target_checkpoint_run = AutoMLRun(experiment_name,last_run_id)
        model_name = "outputs/model.pt"
        model_local = "checkpoints/model_yolo.pt"
        target_checkpoint_run.download_file(name=model_name, output_file_path=model_local)

        # upload the checkpoint to the blob store
        ds.upload(src_dir="checkpoints", target_path='checkpoints')

        # create a FileDatset for the checkpoint and register it with your workspace
        ds_path = ds.path('checkpoints/model_yolo.pt')
        checkpoint_yolo = Dataset.File.from_files(path=ds_path)
        checkpoint_yolo = checkpoint_yolo.register(workspace=ws, name='yolo_checkpoint')


    except:
        print("model does not exist, new run")
        last_run_id = None
    if last_run_id:
        image_config_vit = AutoMLImageConfig(
            task=ImageTask.IMAGE_CLASSIFICATION,
            compute_target=compute_target,
            training_data=training_dataset,
            validation_data=validation_dataset,
            checkpoint_dataset_id= checkpoint_yolo.id,
            checkpoint_filename='model_yolo.pt',
            hyperparameter_sampling=GridParameterSampling({"model_name": choice("vitb16r224")}),
            iterations=1,
        )
    else:
        image_config_vit = AutoMLImageConfig(
            task=ImageTask.IMAGE_CLASSIFICATION,
            compute_target=compute_target,
            training_data=training_dataset,
            validation_data=validation_dataset,
            hyperparameter_sampling=GridParameterSampling({"model_name": choice("vitb16r224")}),
            iterations=1,
        )
   
    experiment = Experiment(ws, name=experiment_name)
    automl_image_run = experiment.submit(image_config_vit)
    automl_image_run.wait_for_completion()
    best_child_run = automl_image_run.get_best_child()
    model = best_child_run.register_model(
        model_name=args.model_name, model_path="outputs/model.pt"
    )

    return model.version

 

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--compute_cluster", type=str)
    parser.add_argument("--training_dataset", type=str)
    parser.add_argument("--validation_dataset", type=str)
    parser.add_argument("--experiment_name", type=str)
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--datastore",default="mltraining", type=str)

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