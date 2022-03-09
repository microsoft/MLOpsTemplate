from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table


class Drift_Analysis():
    def __init__(self, tenant_id, client_id, client_secret, cluster_uri,db):
        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
        self.client = KustoClient(KCSB_DATA)
        self.db =db
    def query(self, query):
        response = self.client.execute(self.db, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe


def test_kusto_query(tenant_id,client_id,client_secret,cluster_uri,db_name ):

    analysis = Drift_Analysis(tenant_id, client_id, client_secret, cluster_uri,db_name)
    print(analysis.query("""
    isd_weather4| take(10)
    """))






