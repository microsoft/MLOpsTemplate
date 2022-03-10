# libraries
import argparse
import pandas as pd

# parse job arguments
parser = argparse.ArgumentParser()
parser.add_argument('--green_taxi_file', type=str, dest='green_taxi_file', help='green taxi file')
parser.add_argument('--weather_file', type=str, dest='weather_file', help='weather file')
parser.add_argument('--output_file', type=str, dest='output_file', help='output file')
args = parser.parse_args()
green_taxi_file = args.green_taxi_file
weather_file = args.weather_file
output_file = args.output_file
print("green_taxi_file:", green_taxi_file)
print("weather_file:", weather_file)
print("output_file:", output_file)

# read inputs
taxi_holidays_df = pd.read_parquet(green_taxi_file)
weather_df_grouped = pd.read_parquet(weather_file)

# data engineering
taxi_holidays_weather_df = pd.merge(taxi_holidays_df, weather_df_grouped, how="left", on=["datetime"])

# output to parquet
taxi_holidays_weather_df.to_parquet(output_file, compression="gzip")