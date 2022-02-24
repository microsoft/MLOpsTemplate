import os
import argparse

import pandas as pd
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core import Workspace
from azureml.automl.core.shared.constants import ImageTask
from azureml.train.automl import AutoMLImageConfig
from azureml.train.hyperdrive import GridParameterSampling, choice
from azureml.core import Experiment



# define functions
def main(args):
    # read in data
    ws = Workspace.from_config()
    compute_target = ws.compute_targets[args.compute_cluster]
    training_dataset = ws.datasets[args.training_dataset]
    validation_dataset = ws.datasets[args.validation_dataset]

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
    model_name = best_child_run.properties["model_name"]
    model = best_child_run.register_model(
        model_name=model_name, model_path="outputs/model.pt"
    )

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--compute_cluster", type=str)
    parser.add_argument("--training_dataset", type=str)
    parser.add_argument("--validation_dataset", type=str)
    parser.add_argument("--experiment_name", type=str)
    # parser.add_argument("--model_name", type=str)

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