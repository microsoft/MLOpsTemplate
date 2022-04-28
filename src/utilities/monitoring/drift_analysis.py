from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
from monitoring import KV_SP_ID, KV_SP_KEY, KV_ADX_DB, KV_ADX_URI, KV_TENANT_ID


class Drift_Analysis():
    def __init__(self,ws=None,tenant_id=None, client_id=None,client_secret=None,cluster_uri=None,database_name=None):

        if ws is not None:
            kv = ws.get_default_keyvault()
            self.client_id = kv.get_secret(KV_SP_ID)
            self.client_secret = kv.get_secret(KV_SP_KEY)
            self.cluster_uri = kv.get_secret(KV_ADX_URI)
            self.database_name = kv.get_secret(KV_ADX_DB)
            self.tenant_id = kv.get_secret(KV_TENANT_ID)
        else:
            self.tenant_id = tenant_id
            self.client_id = client_id
            self.cluster_uri = cluster_uri
            self.database_name = database_name
            self.client_secret=client_secret
        self.cluster_ingest_uri = self.cluster_uri.split(".")[0][:8]+"ingest-"+self.cluster_uri.split(".")[0].split("//")[1]+"."+".".join(self.cluster_uri.split(".")[1:])
        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_uri, self.client_id, self.client_secret, self.tenant_id)
        self.client = KustoClient(KCSB_DATA)
    def query(self, query):#generic query
        response = self.client.execute(self.database_name, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe
    def list_tables(self):
        return list(self.query(".show tables")['TableName'])
    def list_table_columns(self, table_name):
        return self.query(f".show table {table_name}")[['AttributeName', 'AttributeType']]
    def get_time_range(self, table_name, timestamp_col=None):
        columns = self.list_table_columns(table_name)
        timestamp_cols = columns[columns['AttributeType']=='DateTime']
        if timestamp_cols.shape[0]==0:
            raise Exception("No timestamp column found! ")
        if timestamp_col is None:
            if "timestamp" in timestamp_cols['AttributeName'].values:
                timestamp_col ='timestamp'
            else:
                timestamp_col = timestamp_cols['AttributeName'].values[0]
        time_range = self.query(f"{table_name} | summarize time_start = min(['{timestamp_col}']), time_end = max(['{timestamp_col}'])")
        return str(time_range['time_start'].values[0]), str(time_range['time_end'].values[0])
    def analyze_drift(self, table_name, dt_from, dt_to, bin):
        pass
    def compare_drift(self, baseline_table,baseline_filter_expr, target_table, target_filter_expr):
        pass





