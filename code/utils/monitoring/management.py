from azure.mgmt.kusto import KustoManagementClient
from azure.mgmt.kusto.models import EventHubDataConnection
from azure.identity import ClientSecretCredential
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.mgmt.eventhub import EventHubManagementClient
from azure.mgmt.eventhub.models import Eventhub
from azure.mgmt.eventhub.models import AuthorizationRule
import asyncio

import time
import pandas as pd
from .data import Real_Time_Data_Collector
#The table and column mapping that are created as part of the Prerequisites
def create_event_hub(tenant_id,subscription_id, client_id, client_secret,eventhub_rg,eventhub_namespace,eventhub_name):
    credentials = ClientSecretCredential(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id
    )
    param =Eventhub(message_retention_in_days=7,partition_count=2)
    client = EventHubManagementClient(credentials,subscription_id)
    event_hub=client.event_hubs.create_or_update(resource_group_name=eventhub_rg,namespace_name=eventhub_namespace, event_hub_name=eventhub_name, parameters=param)
    rule =AuthorizationRule(rights=["Manage", "Listen", "Send"])
    client.event_hubs.create_or_update_authorization_rule(eventhub_rg,eventhub_namespace,eventhub_name,"aml",rule )
    key = client.event_hubs.list_keys(eventhub_rg,eventhub_namespace,eventhub_name,"aml")
    event_hub_resource_id= f"/subscriptions/{subscription_id}/resourceGroups/{eventhub_rg}/providers/Microsoft.EventHub/namespaces/{eventhub_namespace}/eventhubs/{eventhub_name}"
    return key.primary_connection_string,event_hub_resource_id
    

def create_table_and_mapping(tenant_id, client_id, client_secret, cluster_uri, db_name, table_name, sample_pd_data):
    #need more enhancement
    schema = {k:str(v) for k,v in sample_pd_data.dtypes.items() }
    type_mapping = {
        "object":"string",
        "datetime64[ns]":"datetime",
        "int32":"int",
        "int64":"int",
        "float64":"real",
        "float32":"real",

    }

    CREATE_TABLE_COMMAND =f".create table {table_name} ("
    for col_name, col_dtype in schema.items():
        CREATE_TABLE_COMMAND += col_name +": "+type_mapping.get(col_dtype,"string")+", "
    CREATE_TABLE_COMMAND=CREATE_TABLE_COMMAND[:-2] +")"
    

    # read more at https://docs.microsoft.com/en-us/onedrive/find-your-office-365-tenant-id

    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)

    KUSTO_CLIENT = KustoClient(KCSB_DATA)
    RESPONSE = KUSTO_CLIENT.execute_mgmt(db_name, CREATE_TABLE_COMMAND)
    DESTINATION_TABLE_COLUMN_MAPPING = f"{table_name}_mapping"
    print(CREATE_TABLE_COMMAND)

    dataframe_from_result_table(RESPONSE.primary_results[0])



    DESTINATION_TABLE_COLUMN_MAPPING=f"{table_name}_mapping"
    CREATE_MAPPING_COMMAND = f".create table {table_name} ingestion json mapping '{DESTINATION_TABLE_COLUMN_MAPPING}'"
    CREATE_MAPPING_COMMAND += "'["
    for col_name, col_dtype in schema.items():

        CREATE_MAPPING_COMMAND += "{\"column\":\""+col_name+"\","+"\"Properties\":{\"path\":\"$."+col_name+"\"} }," 
    CREATE_MAPPING_COMMAND=CREATE_MAPPING_COMMAND[:-1] +"]'"


    print(CREATE_MAPPING_COMMAND)
    try:
        KUSTO_CLIENT.execute(db_name,f".drop table {table_name}  ingestion json mapping '{DESTINATION_TABLE_COLUMN_MAPPING}' ")
    except:
        print("mapping is not found, creating new")
    RESPONSE = KUSTO_CLIENT.execute_mgmt(db_name, CREATE_MAPPING_COMMAND)

    dataframe_from_result_table(RESPONSE.primary_results[0])
def create_ingestion(tenant_id,subscription_id, client_id, client_secret,location,table_name,event_hub_resource_id,resource_group_name,cluster_name,db_name):
    #Directory (tenant) ID
    mapping_rule_name = f"{table_name}_mapping"


    credentials = ClientSecretCredential(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id
        )
    kusto_management_client = KustoManagementClient(credentials, subscription_id)

    
    data_connection_name = table_name
    #The event hub that is created as part of the Prerequisites
    consumer_group = "$Default"

    data_format = "MULTIJSON"
    #Returns an instance of LROPoller, check https://docs.microsoft.com/python/api/msrest/msrest.polling.lropoller?view=azure-python
    kusto_management_client.data_connections.begin_delete(resource_group_name=resource_group_name, cluster_name=cluster_name, database_name=db_name, data_connection_name=data_connection_name)
    poller = kusto_management_client.data_connections.begin_create_or_update(resource_group_name=resource_group_name, cluster_name=cluster_name, database_name=db_name, data_connection_name=data_connection_name,
                                            parameters=EventHubDataConnection(event_hub_resource_id=event_hub_resource_id, consumer_group=consumer_group, location=location,
                                                                                table_name=table_name, mapping_rule_name=mapping_rule_name, data_format=data_format))  
    poller.result() 
def provision_resource(tenant_id,subscription_id, client_id, client_secret,adx_rg, eventhub_rg,eventhub_namespace,cluster_uri, db_name, table_name, sample_pd_data):
    cluster_name = cluster_uri.split(".")[0].split("//")[1]
    print(cluster_name)
    location = cluster_uri.split(".")[1]

    primary_connection_string,event_hub_resource_id= create_event_hub(tenant_id,subscription_id, client_id, client_secret,eventhub_rg,eventhub_namespace,table_name)
    print("finished creating eventhub ",table_name)
    create_table_and_mapping(tenant_id, client_id, client_secret, cluster_uri, db_name, table_name, sample_pd_data)
    print("finished creating table and mapping ",table_name, " at db ", db_name)

    create_ingestion(tenant_id,subscription_id, client_id, client_secret,location,table_name,event_hub_resource_id,adx_rg,cluster_name,db_name)
    print("finished creating ingestion ",table_name )

    return primary_connection_string

        

if __name__ == "__main__":

    tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
    #Application ID
    client_id = "111bc278-fd78-4ca0-9476-80b661ad4191"
    #Client Secret
    client_secret = "pyL7Q~MrkOERCjgOmxGReV32RpT6lBOFKq8Z7"
    subscription_id = "c006615f-00c9-454e-bb12-e77bc24411bc"

    cluster_uri = "https://nserafino.centralus.kusto.windows.net" #URL of the ADX Cluster
    db_name = "db01"
    table_name = "isd_weather4"
    #make sure the grant access to as DB admin at cluster level for for the SP.
    resource_group_name = "trial" #RG for the ADX cluster
    eventhub_rg ="trial"
    eventhub_namespace = "serafinoeventhub"
        #The cluster and database that are created as part of the Prerequisites
    cluster_name = "nserafino"
    database_name = "db01"
    adx_rg ='trial'
    # location = "West US 2"

    sample_pd_data = pd.read_parquet("test/data/test_data.parquet").head(100)
    sample_pd_data['timestamp'] = sample_pd_data['datetime']
    sample_pd_data.drop(['datetime'], inplace=True, axis=1)
    start_time = time.time()
    primary_connection_string=provision_resource(tenant_id,subscription_id, client_id, client_secret,eventhub_rg,eventhub_namespace,cluster_uri, db_name, table_name, sample_pd_data)
    print("provision finished in {} seconds.".format(time.time() - start_time))
    print(primary_connection_string)
    data_collector =Real_Time_Data_Collector(primary_connection_string,table_name)
    start_time = time.time()
    asyncio.run(data_collector.log_data(sample_pd_data))
    print("Send messages in {} seconds.".format(time.time() - start_time))