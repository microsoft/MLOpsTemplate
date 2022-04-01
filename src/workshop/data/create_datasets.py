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
from sklearn.model_selection import train_test_split
import numpy as np
def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--year", type=str,default=2016)
    parser.add_argument("--sample_size", type=str, default=2000)
    parser.add_argument("--nyc_dataset_name", type=str, default="NycTlcGreen")
    parser.add_argument("--public_holiday_dataset_name", type=str, default="PublicHoliday")
    parser.add_argument("--weather_dataset_name", type=str, default="Weather")

    parser.add_argument("--datastore_name", type=str, default="workspaceblobstore")
    parser.add_argument("--ml_workspace_name", type=str, default=None)
    parser.add_argument("--sub_id", type=str, default=None)
    parser.add_argument("--resourcegroup_name", type=str, default=None)

    # parse args
    args = parser.parse_args()

    # return args
    return args

def build_time_features(vector):
    pickup_datetime = vector[0]
    month_num = pickup_datetime.month
    day_of_month = pickup_datetime.day
    day_of_week = pickup_datetime.weekday()
    hour_of_day = pickup_datetime.hour
    country_code = "US"
    hr_sin = np.sin(hour_of_day*(2.*np.pi/24))
    hr_cos = np.cos(hour_of_day*(2.*np.pi/24))
    dy_sin = np.sin(day_of_week*(2.*np.pi/7))
    dy_cos = np.cos(day_of_week*(2.*np.pi/7))
    
    return pd.Series((month_num, day_of_month, day_of_week, hour_of_day, country_code, hr_sin, hr_cos, dy_sin, dy_cos))

def create_ml_dataset(green_taxi_df,holidays_df,weather_df):

    green_taxi_df[["month_num", "day_of_month","day_of_week", "hour_of_day", "country_code", "hr_sin", "hr_cos", "dy_sin", "dy_cos"]] = \
    green_taxi_df[["lpepPickupDatetime"]].apply(build_time_features, axis=1)

    columns_to_remove = ["lpepDropoffDatetime", "puLocationId", "doLocationId", "extra", "mtaTax",
                     "improvementSurcharge", "tollsAmount", "ehailFee", "tripType", "rateCodeID", 
                     "storeAndFwdFlag", "paymentType", "fareAmount", "tipAmount"]

    green_taxi_df.drop(columns_to_remove, axis=1, inplace=True)


    green_taxi_df["datetime"] = green_taxi_df["lpepPickupDatetime"].dt.normalize()



    holidays_df = holidays_df.rename(columns={"countryRegionCode": "country_code"})
    holidays_df["datetime"] = holidays_df["date"].dt.normalize()

    holidays_df.drop(["countryOrRegion", "holidayName", "date"], axis=1, inplace=True)

    taxi_holidays_df = pd.merge(green_taxi_df, holidays_df, how="left", on=["datetime", "country_code"])
    taxi_holidays_df[taxi_holidays_df["normalizeHolidayName"].notnull()]
    

    weather_df["datetime"] = weather_df["datetime"].dt.normalize()

    # group by datetime
    aggregations = {"precipTime": "max", "temperature": "mean", "precipDepth": "max"}
    weather_df_grouped = weather_df.groupby("datetime").agg(aggregations)
    weather_df_grouped.head(10)

    taxi_holidays_weather_df = pd.merge(taxi_holidays_df, weather_df_grouped, how="left", on=["datetime"])
    # taxi_holidays_weather_df.describe()

    final_df = taxi_holidays_weather_df.query("pickupLatitude>=40.53 and pickupLatitude<=40.88 and \
                                           pickupLongitude>=-74.09 and pickupLongitude<=-73.72 and \
                                           tripDistance>0 and tripDistance<75 and \
                                           passengerCount>0 and passengerCount<100 and \
                                           totalAmount>0")
    return final_df

def main(args):
    # check aml workspace
    # read in data    
    os.makedirs("data/.tmp", exist_ok=True)
    if (args.ml_workspace_name == None):
        print("Please provide your AML Workspace Name")
        print("Example:")
        print("create_datasets.py --datastore_name workspaceblobstore --ml_workspace_name amlwrkshp-000 --sub_id SUBSCRIPTIONID --resourcegroup_name amlwrkshp-000-rg")
        return 0
    elif (args.sub_id == None):
        print("lease provide your Subscription ID")
        print("Example:")
        print("create_datasets.py --datastore_name workspaceblobstore --ml_workspace_name amlwrkshp-000 --sub_id SUBSCRIPTIONID --resourcegroup_name amlwrkshp-000-rg")
        return 0
    if (args.resourcegroup_name == None):
        print("lease provide your Resource Group Name")
        print("Example:")
        print("create_datasets.py --datastore_name workspaceblobstore --ml_workspace_name amlwrkshp-000 --sub_id SUBSCRIPTIONID --resourcegroup_name amlwrkshp-000-rg")
        return 0
    else:
        amlName, subId, rgName  = args.ml_workspace_name, args.sub_id, args.resourcegroup_name
        print("Accessing your AML workspace {0} in {1}".format(amlName, rgName))
    
    ws = Workspace.get(name=amlName, subscription_id=subId, resource_group=rgName)

    print(ws)
    datastore= ws.datastores[args.datastore_name]
    start = datetime.strptime(f"1/1/{args.year}","%m/%d/%Y")
    end = datetime.strptime(f"1/31/{args.year}","%m/%d/%Y")

    green_taxi_df = pd.concat([NycTlcGreen(start + relativedelta(months=x), end + relativedelta(months=x)) \
            .to_pandas_dataframe().sample(args.sample_size) for x in range(12)])
    green_taxi_df.to_parquet("data/.tmp/green_taxi.parquet")
    green_taxi_df_ut= green_taxi_df.sample(1000) #small file for local testing
    green_taxi_df_ut.to_parquet("data/green_taxi.parquet")

    

    # Public holidays
    holidays_df = PublicHolidays().to_pandas_dataframe()
    holidays_df.to_parquet("data/.tmp/holidays.parquet")
    #local dataset
    holidays_df_ut = holidays_df.sample(1000)
    holidays_df_ut.to_parquet("data/holidays.parquet")


    weather_df = pd.concat([NoaaIsdWeather(cols=["temperature", "precipTime", "precipDepth"], start_date=start + relativedelta(months=x), end_date=end + relativedelta(months=x))\
            .to_pandas_dataframe().query("latitude>=40.53 and latitude<=40.88 and longitude>=-74.09 and longitude<=-73.72 and temperature==temperature") for x in range(12)])
    weather_df.to_parquet("data/.tmp/weather.parquet")

    weather_df_ut = weather_df.sample(1000)#small file for local testing
    weather_df_ut.to_parquet("data/weather.parquet")

    final_df = create_ml_dataset(green_taxi_df,holidays_df,weather_df)
    final_df_ut = final_df.sample(1000)
    final_df_ut, test_df_ut = train_test_split(final_df_ut, test_size=0.2, random_state=100)
    final_df, test_df = train_test_split(final_df, test_size=0.2, random_state=100)

    final_df_ut.to_parquet("data/final_df.parquet")
    test_df_ut.to_parquet("data/test_df.parquet")

    final_df.to_parquet("data/.tmp/final_df.parquet")
    test_df.to_parquet("data/.tmp/test_df.parquet")
    shutil.copy('data/linear_regression.joblib','data/.tmp/linear_regression.joblib')
    
    #also uploading to cloud for remote job run
    datastore.upload(src_dir='data/.tmp',
                 target_path='mlops_workshop_data',
                 overwrite=True)
    shutil.rmtree('data/.tmp')

# run script
if __name__ == "__main__":
    # parse args
    print("Running script to create datasets")
    args = parse_args()

    # run main function
    main(args)