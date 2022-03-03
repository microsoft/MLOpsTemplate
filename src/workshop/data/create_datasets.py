from azureml.opendatasets import NycTlcGreen
from azureml.opendatasets import PublicHolidays
from azureml.opendatasets import NoaaIsdWeather
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse
from azureml.core import Run, Dataset,Datastore, Workspace
import shutil

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--year", type=str,default=2016)
    parser.add_argument("--sample_size", type=str, default=2000)
    parser.add_argument("--nyc_dataset_name", type=str, default="NycTlcGreen")
    parser.add_argument("--public_holiday_dataset_name", type=str, default="PublicHoliday")
    parser.add_argument("--weather_dataset_name", type=str, default="Weather")

    parser.add_argument("--datastore_name", type=str, default="mltraining")

    # parse args
    args = parser.parse_args()

    # return args
    return args



def main(args):
    # read in data
    os.makedirs("data/.tmp", exist_ok=True)
    ws = Workspace.from_config()
    datastore= ws.datastores[args.datastore_name]
    start = datetime.strptime(f"1/1/{args.year}","%m/%d/%Y")
    end = datetime.strptime(f"1/31/{args.year}","%m/%d/%Y")

    green_taxi_df = pd.concat([NycTlcGreen(start + relativedelta(months=x), end + relativedelta(months=x)) \
            .to_pandas_dataframe().sample(args.sample_size) for x in range(12)])
    green_taxi_df.sample(1000).to_parquet("data/green_taxi.parquet")
    green_taxi_df.to_parquet("data/.tmp/green_taxi.parquet")

    

    # Public holidays
    holidays_df = PublicHolidays().to_pandas_dataframe()
    holidays_df.sample(1000).to_parquet("data/holidays.parquet")
    holidays_df.to_parquet("data/.tmp/holidays.parquet")

    weather_df = pd.concat([NoaaIsdWeather(cols=["temperature", "precipTime", "precipDepth"], start_date=start + relativedelta(months=x), end_date=end + relativedelta(months=x))\
            .to_pandas_dataframe().query("latitude>=40.53 and latitude<=40.88 and longitude>=-74.09 and longitude<=-73.72 and temperature==temperature") for x in range(12)])
    weather_df.sample(1000).to_parquet("data/weather.parquet")
    weather_df.to_parquet("data/.tmp/weather.parquet")
    datastore.upload(src_dir='data/.tmp',
                 target_path='mlops_workshop_data',
                 overwrite=True)
    shutil.rmtree('data/.tmp')

# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)