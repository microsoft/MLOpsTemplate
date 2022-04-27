from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
from monitoring import KV_SP_ID, KV_SP_KEY, KV_ADX_DB, KV_ADX_URI, KV_TENANT_ID


class Drift_Analysis():
    def __init__(self,table_name,ws=None,tenant_id=None, client_id=None,client_secret=None,cluster_uri=None,database_name=None):

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
        response = self.client.execute(self.db, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe
    def analyze_drift(self, table_name, dt_from, dt_to, bin):
        pass
    def compare_drift(self, baseline_table,baseline_filter_expr, target_table, target_filter_expr):
        pass





