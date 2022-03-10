import argparse
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..')))
from scripts.authentication.service_principal import ws
from azureml.core.model import Model
from azureml.core import Dataset
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def getArgs(argv=None):
    parser = argparse.ArgumentParser(description="filepaths")
    parser.add_argument("--model_name", help='Model name', required=True)
    parser.add_argument("--model_path", help='Model path', required=True)
    return parser.parse_args(argv)

def main():
    """Main operational flow"""
    args = getArgs()
    logging.info(f'Model name is: {args.model_name}')
    logging.info(f'Model path is: {args.model_path}')

    #prepped_data = Dataset.get_by_name(workspace=ws,name='NYC-trainingset-Dec2020')

    # Get best model
    _ = Model.register(
            workspace=ws, 
            model_path=args.model_path, 
            model_name=args.model_name,
            #sample_input_dataset=prepped_data,
            description="Taxi fare",
            tags={'ml_problem':'regression', 'problem':'taxi fares'}
            )

if __name__ == "__main__":
    main()
