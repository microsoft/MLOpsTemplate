import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse
import sys
import os
from sklearn.model_selection import train_test_split
sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()


    # add arguments
    parser.add_argument("--nyc_file_name", type=str, default="green_taxi.parquet")
    parser.add_argument("--public_holiday_file_name", type=str, default="holidays.parquet")
    parser.add_argument("--weather_file_name", type=str, default="weather.parquet")
    parser.add_argument("--prep_data", type=str,default="data", help="Path of prepped data")
    parser.add_argument("--input_folder", type=str, default="data")
    parser.add_argument("--run_mode", type=str, default="local")

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

def main(args):
    
    # read in data

    green_taxi_df = pd.read_parquet(os.path.join(args.input_folder, args.nyc_file_name))

    green_taxi_df[["month_num", "day_of_month","day_of_week", "hour_of_day", "country_code", "hr_sin", "hr_cos", "dy_sin", "dy_cos"]] = \
        green_taxi_df[["lpepPickupDatetime"]].apply(build_time_features, axis=1)

    columns_to_remove = ["lpepDropoffDatetime", "puLocationId", "doLocationId", "extra", "mtaTax",
                     "improvementSurcharge", "tollsAmount", "ehailFee", "tripType", "rateCodeID", 
                     "storeAndFwdFlag", "paymentType", "fareAmount", "tipAmount"]

    green_taxi_df.drop(columns_to_remove, axis=1, inplace=True)


    green_taxi_df["datetime"] = green_taxi_df["lpepPickupDatetime"].dt.normalize()


    holidays_df = pd.read_parquet(os.path.join(args.input_folder, args.public_holiday_file_name))

    holidays_df = holidays_df.rename(columns={"countryRegionCode": "country_code"})
    holidays_df["datetime"] = holidays_df["date"].dt.normalize()

    holidays_df.drop(["countryOrRegion", "holidayName", "date"], axis=1, inplace=True)

    taxi_holidays_df = pd.merge(green_taxi_df, holidays_df, how="left", on=["datetime", "country_code"])
    taxi_holidays_df[taxi_holidays_df["normalizeHolidayName"].notnull()]
    

    weather_df = pd.read_parquet(os.path.join(args.input_folder,args.weather_file_name))

    weather_df["datetime"] = weather_df["datetime"].dt.normalize()

    # group by datetime
    aggregations = {"precipTime": "max", "temperature": "mean", "precipDepth": "max"}
    weather_df_grouped = weather_df.groupby("datetime").agg(aggregations)
    weather_df_grouped.head(10)

    taxi_holidays_weather_df = pd.merge(taxi_holidays_df, weather_df_grouped, how="left", on=["datetime"])
    taxi_holidays_weather_df.describe()

    final_df = taxi_holidays_weather_df.query("pickupLatitude>=40.53 and pickupLatitude<=40.88 and \
                                           pickupLongitude>=-74.09 and pickupLongitude<=-73.72 and \
                                           tripDistance>0 and tripDistance<75 and \
                                           passengerCount>0 and passengerCount<100 and \
                                           totalAmount>0")
    final_df, test_df = train_test_split(final_df, test_size=0.2, random_state=100)
    os.makedirs(args.prep_data, exist_ok=True)
    
    if args.run_mode =='local':
        print("Data Files were written successfully to folder:", args.prep_data)
    
    if args.run_mode =='remote':
        print("Data Files were written successfully to AZML Default Data Store folder")
    
    final_df.to_parquet(os.path.join(args.prep_data, "final_df.parquet"))
    test_df.to_parquet(os.path.join(args.prep_data, "test_df.parquet"))


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)
