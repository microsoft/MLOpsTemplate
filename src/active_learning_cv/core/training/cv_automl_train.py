import os
import argparse

import pandas as pd
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core import Workspace
from azureml.automl.core.shared.constants import ImageTask
from azureml.train.automl import AutoMLImageConfig
from azureml.train.hyperdrive import GridParameterSampling, choice
from azureml.core import Experiment, Run, Model
from strictyaml import load




# define functions
def main(args):
    # read in data
    run = Run.get_context()
    ws = run.experiment.workspace
    compute_target = ws.compute_targets[args.compute_cluster]
    training_dataset = ws.datasets[args.training_dataset]
    validation_dataset = ws.datasets[args.validation_dataset]
    try:
        last_model = Model(ws,args.model_name)
        last_run_id = last_model.run_id
        print("last run exists, pull the last run_id ", last_run_id)
    except:
        print("model does not exist, new run")
        last_run_id = None
    if last_run_id:
        image_config_vit = AutoMLImageConfig(
            task=ImageTask.IMAGE_CLASSIFICATION,
            compute_target=compute_target,
            training_data=training_dataset,
            validation_data=validation_dataset,
            checkpoint_run_id= last_run_id,
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
    experiment_name = args.experiment_name
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