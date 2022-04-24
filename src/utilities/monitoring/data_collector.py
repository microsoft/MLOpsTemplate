from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import threading, queue
import time
from azure.kusto.ingest import (
    QueuedIngestClient,
    IngestionProperties,
    KustoStreamingIngestClient,

)
import pandas as pd

class Online_Collector():
    def __init__(self, tenant_id, client_id,client_secret,cluster_uri,database_name,table_name, sample_pd_data=None, enabled_streaming=True):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.cluster_uri = cluster_uri
        self.cluster_ingest_uri = cluster_uri.split(".")[0][:8]+"ingest-"+cluster_uri.split(".")[0].split("//")[1]+"."+".".join(cluster_uri.split(".")[1:])
        self.database_name = database_name
        self.client_secret=client_secret
        self.table_name= table_name
        self.enabled_streaming= enabled_streaming
        self.setup()
        self.sample_pd_data= sample_pd_data
        if self.sample_pd_data:
            self.create_table_and_mapping()

        self.ingestion_props = IngestionProperties(
        database=f"{database_name}",
        table=f"{table_name}",
        )
        self.q = queue.Queue()


    def start_logging_df(self,buffer_time=1, batch_size=1):
        #buffer_time and batch_size are parameters to buffer result before logging to ADX.
        self.start_logging=True
        threading.Thread(target=self.stream_collect_df_daemon, daemon=True, args=(buffer_time,batch_size)).start()
    def stop_logging(self, force=False):
        if force:
            self.start_logging= False 
        else:
            #wait for existing queue to be empty (processing done)
            while (not self.q.empty()):
                time.sleep(1)
            self.start_logging= False 

    def stream_collect_df_daemon(self, buffer_time, batch_size):
        while self.start_logging:
            df_list = []
            record_count=0
            wait_time =0
            start_time = time.time()
            while wait_time < buffer_time and record_count < batch_size:
                try:
                    df = self.q.get(1)
                    df_list.append(df)
                    record_count += df.shape[0]
                except:
                    pass
                check_time = time.time()
                duration = check_time - start_time
                wait_time +=duration
            if record_count>0:   
                self.stream_collect_df(pd.concat(df_list))
        print("logging stopped ")

    def stream_collect_df_queue(self, df):
        self.q.put(df)
    def setup(self):
        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_uri, self.client_id, self.client_secret, self.tenant_id)
        KCSB_DATA_INGEST = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_ingest_uri, self.client_id, self.client_secret, self.tenant_id)
        self.kusto_client = KustoClient(KCSB_DATA)
        self.queue_client = QueuedIngestClient(KCSB_DATA_INGEST)
        self.streaming_client = KustoStreamingIngestClient(KCSB_DATA)
    def create_table_and_mapping(self):
        #need more enhancement
        schema = {k:str(v) for k,v in self.sample_pd_data.dtypes.items() }
        type_mapping = {
            "object":"string",
            "datetime64[ns]":"datetime",
            "int32":"int",
            "int64":"int",
            "float64":"real",
            "float32":"real",

        }

        CREATE_TABLE_COMMAND =f".create table {self.table_name} ("
        for col_name, col_dtype in schema.items():
            CREATE_TABLE_COMMAND += f"['{col_name}']" +": "+type_mapping.get(col_dtype,"string")+", "
        CREATE_TABLE_COMMAND=CREATE_TABLE_COMMAND[:-2] +")"

        

        # read more at https://docs.microsoft.com/en-us/onedrive/find-your-office-365-tenant-id

        print(CREATE_TABLE_COMMAND)

        self.kusto_client.execute_mgmt(self.database_name, CREATE_TABLE_COMMAND)
        if self.enabled_streaming:
          ENABLE_TABLE_STREAMING_POLICY =".alter table "+self.table_name+ " policy streamingingestion '{\"IsEnabled\": true, \"HintAllocatedRate\": 2.1}'" 
          self.kusto_client.execute_mgmt(self.database_name, ENABLE_TABLE_STREAMING_POLICY)
    def setup_table(self, sample_data_df):
        self.sample_pd_data= sample_data_df.head(1)
        self.create_table_and_mapping()
    def stream_collect_df(self,input_data):
        if self.sample_pd_data is not None:
            self.sample_pd_data= input_data.head(1)
            self.create_table_and_mapping()    
        self.streaming_client.ingest_from_dataframe(input_data, ingestion_properties=self.ingestion_props)
    def stream_collect(self,input_data):
        self.streaming_client.ingest_from_stream(input_data, ingestion_properties=self.ingestion_props)
    def batch_collect(self,input_data):
        if not self.sample_pd_data:
            self.sample_pd_data= input_data.head(1)
            self.create_table_and_mapping()
        self.queue_client.ingest_from_dataframe(input_data, ingestion_properties=self.ingestion_props)      
    def query(self, query):
        response = self.kusto_client.execute(self.database_name, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe
    def retrieve_last_records(self,table_name, ts_col_name = "timestamp", max_records = 1000, horizon ='5m'):
        query = f"{table_name}|where {ts_col_name}> ago({horizon})| sort by {ts_col_name}|take({max_records})"
        response = self.kusto_client.execute(self.database_name, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe

def spark_collect(input_data,cluster_uri, client_id, client_secret, tenant_id,database_name,table_name):
  sample_df = input_data.limit(2).toPandas()
  collector = Online_Collector(tenant_id, client_id,client_secret,cluster_uri,database_name,table_name, sample_df, True)
  cluster_ingest_uri=collector.cluster_ingest_uri
  def collect_df(iterator):
    KCSB_DATA_INGEST = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_ingest_uri, client_id, client_secret, tenant_id)
    queue_client = QueuedIngestClient(KCSB_DATA_INGEST)
    ingestion_props = IngestionProperties(
    database=f"{database_name}",
    table=f"{table_name}",
    )

    for df in iterator:
      queue_client.ingest_from_dataframe(df, ingestion_properties=ingestion_props)

      yield pd.DataFrame({"result":[df.shape[0]]})
  return int(input_data.mapInPandas(collect_df,schema="result int").groupby().sum().take(1)[0][0])
      
