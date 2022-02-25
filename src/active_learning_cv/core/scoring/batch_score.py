
from PIL import Image
import os
import tempfile
import logging

# from azureml.contrib.services.aml_request import rawhttp
from azureml.automl.core.shared import logging_utilities
# from azureml.contrib.services.aml_response import AMLResponse
from azureml.core.model import Model

from azureml.automl.dnn.vision.common.utils import _set_logging_parameters
from azureml.automl.dnn.vision.common.model_export_utils import load_model, run_inference
from azureml.automl.dnn.vision.common.logging_utils import get_logger

from azureml.automl.dnn.vision.classification.inference.score import _score_with_model
TASK_TYPE = 'image-classification'
logger = get_logger('azureml.automl.core.scoring_script_images')
def init():
    global model

    # Set up logging
    _set_logging_parameters(TASK_TYPE, {})

    model_path = Model.get_model_path(model_name='AutoMLf3f0b65590')

    try:
        logger.info("Loading model from path: {}.".format(model_path))
        model_settings = {"valid_resize_size": 256, "valid_crop_size": 224, "train_crop_size": 224}
        model = load_model(TASK_TYPE, model_path, **model_settings)
        logger.info("Loading successful.")
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise


def run(mini_batch):
    print(f"run method start: {__file__}, run({mini_batch})")
    resultList = []

    for image in mini_batch:
        # prepare each image
        data = open(image, 'rb').read()
        result = run_inference(model, data, _score_with_model)
        print(result)

        resultList.append("{}: {}".format(os.path.basename(image), result))

    return resultList
