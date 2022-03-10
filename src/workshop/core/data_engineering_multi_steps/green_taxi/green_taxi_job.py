# libraries
from azureml.opendatasets import NycTlcGreen
from azureml.opendatasets import PublicHolidays
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

# parse job arguments
parser = argparse.ArgumentParser()
parser.add_argument('--start_date', type=str, dest='start_date', help='start date')
parser.add_argument('--end_date', type=str, dest='end_date', help='end date')
parser.add_argument('--output_file', type=str, dest='output_file', help='output file')
args = parser.parse_args()
start_date = args.start_date
end_date = args.end_date
output_file = args.output_file
print("start_date:", start_date)
print("end_date:", end_date)
print("output_file:", output_file)

#
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

# parameters
start = datetime.strptime(start_date,"%m/%d/%Y")
end = datetime.strptime(end_date,"%m/%d/%Y")

# data engineering
green_taxi_df = pd.concat([NycTlcGreen(start + relativedelta(months=x), end + relativedelta(months=x)) \
        .to_pandas_dataframe().sample(2000) for x in range(12)])
green_taxi_df[["month_num", "day_of_month","day_of_week", "hour_of_day", "country_code", "hr_sin", "hr_cos", "dy_sin", "dy_cos"]] = green_taxi_df[["lpepPickupDatetime"]].apply(build_time_features, axis=1)
columns_to_remove = ["lpepDropoffDatetime", "puLocationId", "doLocationId", "extra", "mtaTax",
                     "improvementSurcharge", "tollsAmount", "ehailFee", "tripType", "rateCodeID", 
                     "storeAndFwdFlag", "paymentType", "fareAmount", "tipAmount"]
green_taxi_df.drop(columns_to_remove, axis=1, inplace=True)
green_taxi_df["datetime"] = green_taxi_df["lpepPickupDatetime"].dt.normalize()
holidays_df = PublicHolidays().to_pandas_dataframe()
holidays_df = holidays_df.rename(columns={"countryRegionCode": "country_code"})
holidays_df["datetime"] = holidays_df["date"].dt.normalize()
holidays_df.drop(["countryOrRegion", "holidayName", "date"], axis=1, inplace=True)
taxi_holidays_df = pd.merge(green_taxi_df, holidays_df, how="left", on=["datetime", "country_code"])
taxi_holidays_df[taxi_holidays_df["normalizeHolidayName"].notnull()]

# output to parquet
taxi_holidays_df.to_parquet(output_file, compression="gzip")