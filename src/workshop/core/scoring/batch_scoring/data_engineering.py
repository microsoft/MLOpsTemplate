import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import os

import argparse,os
import pandas as pd
import datetime
# data engineering

# read arguments

def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()


    # add arguments
    parser.add_argument("--nyc_file_name", type=str, default="green_taxi.parquet")
    parser.add_argument("--public_holiday_file_name", type=str, default="holidays.parquet")
    parser.add_argument("--weather_file_name", type=str, default="weather.parquet")
    parser.add_argument('--input_folder', type=str)
    parser.add_argument('--output_folder', type=str)

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
def engineer_features(green_taxi_df,holidays_df,weather_df ):

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

    taxi_holidays_weather_df = pd.merge(taxi_holidays_df, weather_df_grouped, how="left", on=["datetime"])

    final_df = taxi_holidays_weather_df.query("pickupLatitude>=40.53 and pickupLatitude<=40.88 and \
                                           pickupLongitude>=-74.09 and pickupLongitude<=-73.72 and \
                                           tripDistance>0 and tripDistance<75 and \
                                           passengerCount>0 and passengerCount<100")
    return final_df

def main(args):
    
    # read in data
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    day = today.day
    folder = "{:02d}-{:02d}-{:4d}".format(month,day,year)
    green_taxi_df = pd.read_parquet(os.path.join(args.input_folder,folder, args.nyc_file_name))


    holidays_df = pd.read_parquet(os.path.join(args.input_folder,folder, args.public_holiday_file_name))

    weather_df = pd.read_parquet(os.path.join(args.input_folder,folder,args.weather_file_name))

    final_df = engineer_features(green_taxi_df, holidays_df, weather_df)
    # if os.path.exists(args.output_folder):
    #     os.remove(args.output_folder)
 
    final_df.to_parquet(args.output_folder+"/data.parquet")
    print("done writing data")
    ml_table_content = """
paths:
  - pattern: ./*.parquet
    """
    with open(os.path.join(args.output_folder,"MLTable"),'w') as mltable_file:
        mltable_file.writelines(ml_table_content)



# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)
