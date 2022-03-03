# libraries
from azureml.opendatasets import NoaaIsdWeather
from datetime import datetime
from dateutil.relativedelta import relativedelta
import argparse
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

# parameters
start = datetime.strptime(start_date,"%m/%d/%Y")
end = datetime.strptime(end_date,"%m/%d/%Y")

# data engineering
weather_df = pd.concat([NoaaIsdWeather(cols=["temperature", "precipTime", "precipDepth"], start_date=start + relativedelta(months=x), end_date=end + relativedelta(months=x))\
        .to_pandas_dataframe().query("latitude>=40.53 and latitude<=40.88 and longitude>=-74.09 and longitude<=-73.72 and temperature==temperature") for x in range(12)])
weather_df["datetime"] = weather_df["datetime"].dt.normalize()
aggregations = {"precipTime": "max", "temperature": "mean", "precipDepth": "max"}
weather_df_grouped = weather_df.groupby("datetime").agg(aggregations)

# output to parquet
weather_df_grouped.to_parquet(output_file, compression="gzip")