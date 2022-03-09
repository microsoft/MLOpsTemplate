from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table

from azure.kusto.ingest import (
    QueuedIngestClient,
    IngestionProperties,
    KustoStreamingIngestClient,

)

class Online_Collector():
    def __init__(self, tenant_id, client_id,client_secret,cluster_uri,database_name,table_name, sample_pd_data):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.cluster_uri = cluster_uri
        self.cluster_ingest_uri = cluster_uri.split(".")[0][:8]+"ingest-"+cluster_uri.split(".")[0].split("//")[1]+"."+".".join(cluster_uri.split(".")[1:])
        self.database_name = database_name
        self.client_secret=client_secret
        self.table_name= table_name
        self.sample_pd_data= sample_pd_data
        self.setup()
        self.create_table_and_mapping()
        self.ingestion_props = IngestionProperties(
        database=f"{database_name}",
        table=f"{table_name}",
        )


    
    def setup(self):
        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_uri, self.client_id, self.client_secret, self.tenant_id)
        KCSB_DATA_INGEST = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_ingest_uri, self.client_id, self.client_secret, self.tenant_id)
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
            CREATE_TABLE_COMMAND += col_name +": "+type_mapping.get(col_dtype,"string")+", "
        CREATE_TABLE_COMMAND=CREATE_TABLE_COMMAND[:-2] +")"
        ENABLE_TABLE_STREAMING_POLICY =".alter table "+self.table_name+ " policy streamingingestion '{\"IsEnabled\": true, \"HintAllocatedRate\": 2.1}'" 
        

        # read more at https://docs.microsoft.com/en-us/onedrive/find-your-office-365-tenant-id

        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_uri, self.client_id, self.client_secret, self.tenant_id)

        KUSTO_CLIENT = KustoClient(KCSB_DATA)
        KUSTO_CLIENT.execute_mgmt(self.database_name, CREATE_TABLE_COMMAND)
        KUSTO_CLIENT.execute_mgmt(self.database_name, ENABLE_TABLE_STREAMING_POLICY)

        DESTINATION_TABLE_COLUMN_MAPPING = f"{self.table_name}_mapping"
        print(CREATE_TABLE_COMMAND)

        # dataframe_from_result_table(RESPONSE.primary_results[0])



        DESTINATION_TABLE_COLUMN_MAPPING=f"{self.table_name}_mapping"
        CREATE_MAPPING_COMMAND = f".create table {self.table_name} ingestion json mapping '{DESTINATION_TABLE_COLUMN_MAPPING}'"
        CREATE_MAPPING_COMMAND += "'["
        for col_name, col_dtype in schema.items():

            CREATE_MAPPING_COMMAND += "{\"column\":\""+col_name+"\","+"\"Properties\":{\"path\":\"$."+col_name+"\"} }," 
        CREATE_MAPPING_COMMAND=CREATE_MAPPING_COMMAND[:-1] +"]'"
        # KUSTO_CLIENT.execute_mgmt(self.database_name, CREATE_MAPPING_COMMAND)



    def stream_collect(self,input_data):
        self.streaming_client.ingest_from_dataframe(input_data, ingestion_properties=self.ingestion_props)
    def batch_collect(self,input_data):
        self.queue_client.ingest_from_dataframe(input_data, ingestion_properties=self.ingestion_props)
#Batch_collector store the data to Azure Blob storage via connection through AML's datastore
class Batch_Collector():
    def __init__(self, datastore, folder):
        self.datastore= datastore
        self.folder = folder

    def collect(self, source_file):
        self.datastore.upload_files(files=[source_file],target_path=self.folder)
        
        return {"filename":source_file.split("/")[-1], "datastore":self.datastore.name, "folder":self.folder}
