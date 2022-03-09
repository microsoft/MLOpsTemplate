"""Retrieve taxi fare data"""
import logging
import argparse
import datetime as dt
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
    parser.add_argument("--start_date_arg", help='Start date for pulling taxi fare data', required=True)
    parser.add_argument("--end_date_arg", help='End date for pulling taxi fare data', required=True)
    parser.add_argument("--output_filepath", help='Output filepath', required=True)
    parser.add_argument("--output_filename", help='Output filename', required=True)
    return parser.parse_args(argv)


def get_taxi_data(start_date=None, end_date=None):
    """Get taxi fare data for the specified period"""
    data = None
    try:
        #start_date = parser.parse(start_date)
        #end_date = parser.parse(end_date)
        nyc_tlc = NycTlcGreen(start_date=start_date, end_date=end_date)
        data = nyc_tlc.to_pandas_dataframe()
        logging.info('Successfully received taxi fare data.')
    except Exception as e:
        logging.warning(f'Exception: {e}. Failed to load taxi fare data.')
    finally:
        if data is None:
            final_value = 'No data returned.'
        else:
            final_value = data
    return final_value

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
    #start = datetime.strptime(args.start_date_arg, "%Y-%m-%d")
    #end = datetime.strptime(args.end_date_arg, "%Y-%m-%d")
    start = parser.parse(args.start_date_arg)
    end = parser.parse(args.end_date_arg)
    taxi_data = get_taxi_data(start_date=start, end_date=end)
    logging.info(f"First five rows is:\n {taxi_data.head()}")
    logging.info(f"Last five rows is:\n {taxi_data.tail()}")
    register_datasets(df=taxi_data,full_dataset_name=f'Taxi fare date from {start} to {end}')
    taxi_data.to_csv(args.output_filepath +'/'+ args.output_filename, index=False,
            encoding='utf-8')
