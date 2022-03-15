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
import importlib




# define functions
def main(args):
    # read in data
    run = Run.get_context()
    ws = run.experiment.workspace

    mod = importlib.import_module(args.train_module)
    TRAIN =getattr(mod,args.class_name)
    train_object =TRAIN(ws = ws,datastore_name= args.datastore_name, compute_cluster= args.compute_cluster,ds_prefix= args.ds_prefix,experiment_name=args.experiment_name, target_path= args.target_path,model_name= args.model_name)
    simulation = (args.simulation!="false")
    print("simulation ",simulation)
    train_object.train(simulation)
 

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--train_module",default="cv_auto_ml_train", type=str)
    parser.add_argument("--class_name",default="CV_Auto_ML_Train", type=str)
    parser.add_argument("--compute_cluster", type=str)
    parser.add_argument("--datastore_name", type=str)
    parser.add_argument("--ds_prefix", type=str)
    parser.add_argument("--experiment_name", type=str)
    parser.add_argument("--target_path", type=str)
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--simulation", default="false", type=str)

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