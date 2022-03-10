"""Feature engineering work for taxi fare data"""
import logging
import argparse
import datetime as dt
import pandas as pd
from datetime import datetime
from azureml.core import Dataset
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..')))
from scripts.authentication.service_principal import ws
from azureml.opendatasets import NycTlcGreen
from dateutil import parser
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def getArgs(argv=None):
    parser = argparse.ArgumentParser(description="filepaths")
    parser.add_argument("--start_date_arg", help='Input filepath', required=True)
    parser.add_argument("--end_date_arg", help='Input filename', required=True)
    parser.add_argument("--input_filepath", help='Input filepath', required=True)
    parser.add_argument("--input_filename", help='Input filename', required=True)
    parser.add_argument("--training_data_filepath", help='Training data output', required=True)
    parser.add_argument("--training_data_filename", help='Training data output', required=True)
    return parser.parse_args(argv)

def data_transformations(source=None):
    """Get taxi fare data for the specified period"""
    df = pd.read_csv(source)

    # Remove un-needed columns
    columns_to_remove = ["lpepDropoffDatetime", "puLocationId", "doLocationId", "extra", "mtaTax",
                         "improvementSurcharge", "tollsAmount", "ehailFee", "tripType", "rateCodeID",
                         "storeAndFwdFlag", "paymentType", "fareAmount", "tipAmount"]
    for col in columns_to_remove:
        df.pop(col)

    # Remove edge cases
    df = df.query("pickupLatitude>=40.53 and pickupLatitude<=40.88")
    df = df.query("pickupLongitude>=-74.09 and pickupLongitude<=-73.72")
    df = df.query("tripDistance>=0.25 and tripDistance<31")
    df = df.query("passengerCount>0 and totalAmount>0")

    columns_to_remove_for_training = ["pickupLongitude", "pickupLatitude", "dropoffLongitude", "dropoffLatitude"]
    for col in columns_to_remove_for_training:
        df.pop(col)
    return df

def pd_dataframe_register(
        df=None,
        def_blob_store=None,
        name=None,
        desc=None):
    """Register pandas dataframe"""
    full_dataset = Dataset.Tabular.register_pandas_dataframe(
            dataframe=df,
            target=def_blob_store,
            name=name,
            description=desc
            )

def register_datasets(df=None,full_dataset_name=None):
    """Register the full dataset, including the training/test set"""
    def_blob_store = ws.get_default_datastore()
    pd_dataframe_register(df=df, def_blob_store=def_blob_store, name=full_dataset_name)

if __name__ == "__main__":
    args = getArgs()
    df = data_transformations(source=args.input_filepath + '/' + args.input_filename)

    # Split into train/test split
    test_data = df.sample(frac=0.2)
    train_data = df.drop(test_data.index)

    # Register all datasets
    datasets = [(df, 'full dataset'), (train_data, 'train dataset'), (test_data, 'test dataset')]
    for i in datasets:
        register_datasets(df = i[0],full_dataset_name=f'Processed {i[1]} from {args.start_date_arg} to {args.end_date_arg}')

    # Pass out the training features, and y-variables
    train_data.to_csv(args.training_data_filepath + '/' + args.training_data_filename, index=False, encoding='utf-8')
