
import os
import tempfile
import logging
from azureml.core.model import Model
import pickle
import pandas as pd
from azureml.core import Run
import os
import mlflow
import argparse,os,datetime

def init():
    global model,predictions_data_folder
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions_data_folder", type=str)
    parser.add_argument("--model_name",default='nyc_fare_prediction',type=str, help="Name of the model in workspace")
    args, unknown = parser.parse_known_args()
    predictions_data_folder = args.predictions_data_folder
    print("predictions_data_folder",predictions_data_folder)
    current_run = Run.get_context()
    ws = current_run.experiment.workspace
    model = Model(ws,args.model_name)
    model.download(exist_ok=True)
    model = mlflow.sklearn.load_model(args.model_name)

def run(mini_batch):

    
    print(f'run method start: {__file__}, run({mini_batch})')
    i =0
    for file in mini_batch:
        # prepare each image
        data = pd.read_parquet(file)
        print("data shape ", data.shape)
        predictions = model.predict(data)
        data["prediction"] =predictions
        today = datetime.datetime.today()
        year = today.year
        month = today.month
        day = today.day
        folder = "{:02d}-{:02d}-{:4d}".format(month,day,year) 
        os.makedirs(predictions_data_folder+"/"+folder, exist_ok=True)
        data.to_csv(predictions_data_folder+"/"+folder+"/prediction.csv")
        i+=1


    return [1]*i
