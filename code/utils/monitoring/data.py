###collect data to 


import time
import asyncio
import os

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table

import pandas as pd


class Real_Time_Data_Collector:
    def __init__(self,CONNECTION_STR,EVENTHUB_NAME):
        self.CONNECTION_STR=CONNECTION_STR
        self.EVENTHUB_NAME=EVENTHUB_NAME

    async def send_event_data_batch(self,producer,input_data ):
        # If you know beforehand that the list of events you have will not exceed the
        # size limits, you can use the `send_batch()` api directly without creating an EventDataBatch

        # Without specifying partition_id or partition_key
        # the events will be distributed to available partitions via round-robin.

        event_data_batch = await producer.create_batch()
        try:
            event_data_batch.add(EventData(input_data))
            await producer.send_batch(event_data_batch)

        except ValueError:  # Size exceeds limit. This shouldn't happen if you make sure before hand.
            print("Size of the event data list exceeds the size limit of a single send")
        except EventHubError as eh_err:
            print("Sending error: ", eh_err)

    async def log_data(self,input_df):
        input_df=input_df.to_json(orient="records", date_format='iso')
        producer = EventHubProducerClient.from_connection_string(
        conn_str=self.CONNECTION_STR,
        eventhub_name=self.EVENTHUB_NAME
        )
        async with producer:
            await self.send_event_data_batch(producer,input_df)
class Drift_Analysis():
    def __init__(self, tenant_id, client_id, client_secret, cluster_uri,db):
        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
        self.client = KustoClient(KCSB_DATA)
        self.db =db
    def query(self, query):
        response = self.client.execute(self.db, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe

def test_eventhub():
    CONNECTION_STR = "Endpoint=sb://kafkaeventhub01.servicebus.windows.net/;SharedAccessKeyName=aml;SharedAccessKey=NrHPcd3iD9iXEFg66h4aS3OYvBoKOBgwleqSJFtosRA=;EntityPath=isd_weather4"
    EVENTHUB_NAME = "isd_weather4"
    data_collector =Real_Time_Data_Collector(CONNECTION_STR,EVENTHUB_NAME)
    input_data = pd.read_parquet("test/data/test_data.parquet").head(100)
    input_data['timestamp'] = input_data['datetime']
    input_data.drop(['datetime'], inplace=True, axis=1)
    start_time = time.time()
    asyncio.run(data_collector.log_data(input_data))
    print("Send messages in {} seconds.".format(time.time() - start_time))

def test_kusto_query():
    tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
    #Application ID
    client_id = "af883abf-89dd-4889-bdb3-1ee84f68465e"
    #Client Secret
    client_secret = "XSy7Q~3~uj_ZIlVrQcG98dnAOAK.mikuBsm55"

    cluster_uri = "https://adx02.westus2.kusto.windows.net" #URL of the ADX Cluster
    db_name = "db01"
    analysis = Drift_Analysis(tenant_id, client_id, client_secret, cluster_uri,db_name)
    print(analysis.query("""
    isd_weather4| take(10)
    """))

if __name__ == "__main__":

    test_kusto_query()




