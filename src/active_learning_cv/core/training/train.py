import os
import argparse
import json
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
    f=open(args.param_file)
    params =json.load(f)
    datastore_name = params["datastore_name"]
    ds_prefix = params["train_dataset"]
    target_path = params["jsonl_target_path"]
    model_name = params["model_name"]
    init_run_id = params["init_run_id"]
    if len(init_run_id) <10:
        init_run_id= None
    mod = importlib.import_module(args.train_module)
    TRAIN =getattr(mod,args.class_name)
    train_object =TRAIN(ws = ws,datastore_name= datastore_name, compute_cluster= args.compute_cluster,ds_prefix= ds_prefix,experiment_name=args.experiment_name, target_path= target_path,model_name= model_name)
    simulation = (args.simulation!="false")
    train_object.train(simulation,init_run_id)
 

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--train_module",default="cv_auto_ml_train", type=str)
    parser.add_argument("--class_name",default="CV_Auto_ML_Train", type=str)
    parser.add_argument("--compute_cluster", type=str)
    parser.add_argument("--experiment_name", type=str)
    parser.add_argument("--param_file", type=str)
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