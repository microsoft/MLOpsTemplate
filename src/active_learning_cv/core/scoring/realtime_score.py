# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import tempfile
import logging
import time
import datetime
import json
import pandas as pd
import numpy as np
from azureml.contrib.services.aml_request import rawhttp
from azureml.automl.core.shared import logging_utilities
from azureml.contrib.services.aml_response import AMLResponse
from azureml.core.model import Model

from azureml.automl.dnn.vision.common.utils import _set_logging_parameters
from azureml.automl.dnn.vision.common.model_export_utils import load_model, run_inference
from azureml.automl.dnn.vision.common.logging_utils import get_logger

from azureml.automl.dnn.vision.classification.inference.score import _score_with_model
from data_collector import Online_Collector, Batch_Collector
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Workspace
TASK_TYPE = 'image-classification'
logger = get_logger('azureml.automl.core.scoring_script_images')


def init():
    global model
    global collector, ws,batch_collector,table_name
    tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
    subscription_id = "0e9bace8-7a81-4922-83b5-d995ff706507"

    #Application ID
    client_id = "af883abf-89dd-4889-bdb3-1ee84f68465e"
    #Client Secret
    client_secret = "XSy7Q~3~uj_ZIlVrQcG98dnAOAK.mikuBsm55"

    cluster_uri = "https://adx02.westus2.kusto.windows.net" #URL of the ADX Cluster
    database_name = "db01"
    table_name= "image_logging"
    ts =datetime.datetime.now()
    sample_data = pd.DataFrame({"file_path":['azureml://datastores/mltraining/paths/tmp/tmpev5bi0hz'], "prob":[0.33], "label":['livingroom'], "timestamp":[ts]})
    collector = Online_Collector(tenant_id, client_id,client_secret,cluster_uri,database_name,table_name, sample_data)

    sp = ServicePrincipalAuthentication(tenant_id=tenant_id, # tenantID
                                    service_principal_id=client_id, # clientId
                                    service_principal_password=client_secret) # clientSecret

    ws = Workspace.get(name="ws01ent",
                   auth=sp,
                   subscription_id=subscription_id,
                   resource_group="azureml")
    datastore = ws.datastores['mltraining']
    batch_collector = Batch_Collector(datastore,table_name)
    # Set up logging
    _set_logging_parameters(TASK_TYPE, {})

    # print(" os.getenv( AZUREML_MODEL_DIR ) " , os.getenv("AZUREML_MODEL_DIR"))
    # print(" os.list( AZUREML_MODEL_DIR ) " , os.listdir(os.getenv("AZUREML_MODEL_DIR")))

    model_path= os.path.join(os.getenv("AZUREML_MODEL_DIR"),"model.pt")

    # model_path = Model.get_model_path(model_name='AutoMLf3f0b65590')

    try:
        logger.info("Loading model from path: {}.".format(model_path))
        model_settings = {"valid_resize_size": 256, "valid_crop_size": 224, "train_crop_size": 224}
        model = load_model(TASK_TYPE, model_path, **model_settings)
        logger.info("Loading successful.")
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise


@rawhttp
def run(request):
    logger.info("Request: [{0}]".format(request))
    if request.method == 'GET':
        response_body = str.encode(request.full_path)
        return AMLResponse(response_body, 200)
    elif request.method == 'POST':
        request_body = request.get_data()
        logger.info("Running inference.")
        result = run_inference(model, request_body, _score_with_model)    
        result_for_logging= json.loads(result)
        label_index = np.argmax(result_for_logging["probs"])
        label = result_for_logging["labels"][label_index]
        conf_score = result_for_logging["probs"][label_index]
        file_name = result_for_logging['filename'].split("/")[-1]+".jpg"
        file_path =f"azureml://datastores/{batch_collector.datastore.name}/paths/{table_name}/{file_name}"
        ts =datetime.datetime.now()
        output = pd.DataFrame({"file_path":[file_path], "prob":[conf_score], "label": [label], "timestamp":[ts]})
        collector.stream_collect(output)
        with open(file_name,'wb') as f:
            f.write(request_body)
        batch_collector.collect(file_name)
        logger.info("Finished inferencing.")
        return AMLResponse(result, 200)
    else:
        return AMLResponse("bad request", 500)