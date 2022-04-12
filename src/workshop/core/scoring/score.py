import json
import numpy as np
import pandas as pd
import os
from azureml.core.model import Model
import mlflow
# Called when the service is loaded
def init():
    global model
    # Get the path to the deployed model file and load it
    model_dir =os.getenv('AZUREML_MODEL_DIR')
    model_file = os.listdir(model_dir)[0]
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), model_file)
    model = mlflow.sklearn.load_model(model_path)
# Called when a request is received
def run(raw_data):
    try:
        # Get the input data 
        data=pd.DataFrame(json.loads(raw_data)['data'])
        # Get a prediction from the model
        predictions = model.predict(data)
        return json.dumps(predictions.tolist())
    except Exception as e:
        error= str(e)
        return json.dumps(error)