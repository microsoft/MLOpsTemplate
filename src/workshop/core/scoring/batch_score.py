
import os
import tempfile
import logging
from azureml.core.model import Model
import pickle
import pandas as pd
from azureml.core import Run
import os
import mlflow

def init():
    global model
    model_dir =os.getenv('AZUREML_MODEL_DIR')
    model_file = os.listdir(model_dir)[0]
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), model_file)
    model = mlflow.sklearn.load_model(model_path)

def run(mini_batch):
    print(f"run method start: {__file__}, run({mini_batch})")
    resultList = []

    
    # Set up logging

    for batch in mini_batch:
        # prepare each image
        data = pd.read_json(batch)
        predictions = model.predict(data)
        data["prediction"] =predictions
        resultList.append(data)
    result = pd.concat(resultList)

    return result
