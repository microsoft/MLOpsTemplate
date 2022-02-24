import pandas as pd
import asyncio
import time
import sys
sys.path.append('../')
from monitoring.data import Real_Time_Data_Collector

sample_pd_data = pd.read_parquet("data/test_data.parquet").head(100)
sample_pd_data['timestamp'] = sample_pd_data['datetime']
sample_pd_data.drop(['datetime'], inplace=True, axis=1)
start_time = time.time()
table_name = "isd_weather4"
primary_connection_string = 'Endpoint=sb://serafinoeventhub.servicebus.windows.net/;SharedAccessKeyName=aml;SharedAccessKey=LfGlVFFAycwuBHklhckDBE8qO7O+65+k6936gp8eao8=;EntityPath=isd_weather4'
data_collector =Real_Time_Data_Collector(primary_connection_string,table_name)
asyncio.run(data_collector.log_data(sample_pd_data))
print("Send messages in {} seconds.".format(time.time() - start_time))