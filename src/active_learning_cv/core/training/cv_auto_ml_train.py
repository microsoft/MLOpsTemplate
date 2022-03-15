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
from train_template import Active_Learning_Train


class CV_Auto_ML_Train(Active_Learning_Train):

    def train(self, simulation):
        training_dataset,validation_dataset= self.train_validation_split(self.ws,self.datastore, self.ds_prefix,self.target_path, simulation)
        try:
            last_model = Model(self.ws,self.model_name)
            last_run_id = last_model.run_id
            print("last run exists, pull the last run_id ", last_run_id)
        except:
            print("model does not exist, new run")
            last_run_id = None
        if last_run_id:
            image_config_vit = AutoMLImageConfig(
                task=ImageTask.IMAGE_CLASSIFICATION,
                compute_target=self.compute_target,
                training_data=training_dataset,
                validation_data=validation_dataset,
                checkpoint_run_id= last_run_id,
                hyperparameter_sampling=GridParameterSampling({"model_name": choice("vitb16r224"),"learning_rate":choice(0.0001)}),
                iterations=1            
            )
        else:
            image_config_vit = AutoMLImageConfig(
                task=ImageTask.IMAGE_CLASSIFICATION,
                compute_target=self.compute_target,
                training_data=training_dataset,
                validation_data=validation_dataset,
                hyperparameter_sampling=GridParameterSampling({"model_name": choice("vitb16r224"),"learning_rate":choice(0.0001)}),
                iterations=1,
            )
        experiment_name = self.experiment_name
        experiment = Experiment(self.ws, name=experiment_name)
        automl_image_run = experiment.submit(image_config_vit)
        automl_image_run.wait_for_completion()
        best_child_run = automl_image_run.get_best_child()
        model = best_child_run.register_model(
            model_name=self.model_name, model_path="outputs/model.pt"
        )

        return model.version
        
