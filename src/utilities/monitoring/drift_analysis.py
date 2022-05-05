from azure.kusto.data import KustoClient, KustoConnectionStringBuilder,ClientRequestProperties
from azure.kusto.data.helpers import dataframe_from_result_table
from monitoring import KV_SP_ID, KV_SP_KEY, KV_ADX_DB, KV_ADX_URI, KV_TENANT_ID
import concurrent.futures
from datetime import timedelta

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
        self.client_req_properties = ClientRequestProperties()
        self.client_req_properties.set_option(self.client_req_properties.no_request_timeout_option_name , True)
        timeout = timedelta(hours=1, seconds=30)
        self.client_req_properties.set_option(self.client_req_properties.request_timeout_option_name , timeout)

        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_uri, self.client_id, self.client_secret, self.tenant_id)
        self.client = KustoClient(KCSB_DATA)

    def query(self, query):#generic query
        response = self.client.execute(self.database_name, query, self.client_req_properties)
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
    def get_timestamp_col(self, table_name):
        columns = self.list_table_columns(table_name)
        timestamp_cols = columns[columns['AttributeType']=='DateTime']
        if timestamp_cols.shape[0]==0:
            raise Exception("No timestamp column found! ")
        if "timestamp" in timestamp_cols['AttributeName'].values:
            timestamp_col ='timestamp'
        else:
            timestamp_col = timestamp_cols['AttributeName'].values[0]
        return timestamp_col
    def analyze_drift(self,base_table_name,tgt_table_name, base_dt_from, base_dt_to, tgt_dt_from, tgt_dt_to, bin, limit=10000000, concurrent_run=True):
        base_tbl_columns = self.list_table_columns(base_table_name)
        tgt_tbl_columns = self.list_table_columns(tgt_table_name)
        common_columns = base_tbl_columns.merge(tgt_tbl_columns)
        timestamp_cols = common_columns[common_columns['AttributeType']=='DateTime']
        if timestamp_cols.shape[0]==0:
            raise Exception("No timestamp column found! ")
        if "timestamp" in timestamp_cols['AttributeName'].values:
            time_stamp_col ='timestamp'
        else:
            time_stamp_col = timestamp_cols['AttributeName'].values[0]
        numerical_columns = common_columns[(common_columns['AttributeType']!='DateTime')&(common_columns['AttributeType']!='StringBuffer')]
        numerical_columns = numerical_columns['AttributeName'].values
        categorical_columns = common_columns[common_columns['AttributeType']=='StringBuffer']['AttributeName'].values
        if concurrent_run:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                categorical_output_future = executor.submit(self.analyze_drift_categorical, categorical_columns, time_stamp_col, base_table_name,tgt_table_name, base_dt_from, base_dt_to, tgt_dt_from, tgt_dt_to,bin, limit)
                numberical_output_future = executor.submit(self.analyze_drift_numerical,numerical_columns, time_stamp_col, base_table_name,tgt_table_name, base_dt_from, base_dt_to, tgt_dt_from, tgt_dt_to, bin, limit)
                categorical_output = categorical_output_future.result()
                numberical_output = numberical_output_future.result()
        else:
            categorical_output =self.analyze_drift_categorical(categorical_columns, time_stamp_col, base_table_name,tgt_table_name, base_dt_from, base_dt_to, tgt_dt_from, tgt_dt_to,bin, limit)
            numberical_output = self.analyze_drift_numerical(numerical_columns, time_stamp_col, base_table_name,tgt_table_name, base_dt_from, base_dt_to, tgt_dt_from, tgt_dt_to, bin, limit)



        output =numberical_output.merge(categorical_output, how="outer", on = "frequency")
        return output
    def analyze_drift_categorical(self,categorical_columns, time_stamp_col, base_table_name,tgt_table_name, base_dt_from, base_dt_to, tgt_dt_from, tgt_dt_to, bin, limit=10000000):
        cat_feature_list = ""
        cat_feature_list_with_quote =""
        for feature in categorical_columns:
            cat_feature_list_with_quote = cat_feature_list_with_quote+f"'{feature}'"+","
        cat_feature_list_with_quote = cat_feature_list_with_quote[:-1]
        for feature in categorical_columns:
            cat_feature_list = cat_feature_list+feature+","
        cat_feature_list = cat_feature_list[:-1]
        query =f"""
let categorical_features = dynamic([{cat_feature_list_with_quote}]);
let target = 
{tgt_table_name}
| where ['{time_stamp_col}'] >= datetime('{tgt_dt_from}') and ['{time_stamp_col}'] <= datetime('{tgt_dt_to}') 
| limit {limit}
| project ['{time_stamp_col}'], {cat_feature_list}, properties = pack_all()
| mv-apply categorical_feature = categorical_features to typeof(string) on (
    project categorical_feature, categorical_feature_value = tolong(properties[categorical_feature])
)
| project-away properties, {cat_feature_list}
| summarize target_categorical_feature_value = make_list(categorical_feature_value), target_dcount= dcount(categorical_feature_value) by frequency=bin(['{time_stamp_col}'],{bin}),categorical_feature
| where array_length(target_categorical_feature_value)>0;
{base_table_name}
| where ['{time_stamp_col}'] >= datetime('{base_dt_from}') and ['{time_stamp_col}'] <= datetime('{base_dt_to}') 
| limit {limit}
| project ['{time_stamp_col}'], {cat_feature_list}, properties = pack_all()
| mv-apply categorical_feature = categorical_features to typeof(string) on (
    project categorical_feature, categorical_feature_value = tolong(properties[categorical_feature])
)
| project-away properties, {cat_feature_list}
| summarize base_categorical_feature_value = make_list(categorical_feature_value), base_dcount= dcount(categorical_feature_value) by categorical_feature
|where array_length(base_categorical_feature_value)>0
|join target on categorical_feature
| evaluate hint.distribution = per_node python(
//
typeof(*, euclidean:double),               //  Output schema: append a new fx column to original table 
```
#from scipy.special import kl_div
from scipy.spatial import distance
from scipy.stats import wasserstein_distance

import numpy as np
result = df
n = df.shape[0]
distance1=[]
distance2 =[]
for i in range(n):
    distance1.append(wasserstein_distance(df['base_categorical_feature_value'][i], df['target_categorical_feature_value'][i]))

result['euclidean'] =n #placeholder, waiting for implementation

```
)|project frequency,  categorical_feature,euclidean,  base_dcount,target_dcount
        
        """
        # print(query)
        return self.query(query)

    def analyze_drift_numerical(self,numerical_columns, time_stamp_col, base_table_name,tgt_table_name, base_dt_from, base_dt_to, tgt_dt_from, tgt_dt_to, bin, limit=10000000):
        num_feature_list = ""
        num_feature_list_with_quote =""
        for feature in numerical_columns:
            num_feature_list_with_quote = num_feature_list_with_quote+f"'{feature}'"+","
        num_feature_list_with_quote = num_feature_list_with_quote[:-1]
        for feature in numerical_columns:
            num_feature_list = num_feature_list+feature+","
        num_feature_list = num_feature_list[:-1]
        query = f"""
let numeric_features = dynamic([{num_feature_list_with_quote}]);
let target = 
{tgt_table_name}
| where ['{time_stamp_col}'] >= datetime('{tgt_dt_from}') and ['{time_stamp_col}'] <= datetime('{tgt_dt_to}') 
| limit {limit}
| project ['{time_stamp_col}'], {num_feature_list}, properties = pack_all()
| mv-apply numeric_feature = numeric_features to typeof(string) on (
    project numeric_feature, numeric_feature_value = tolong(properties[numeric_feature])
)
| project-away properties, {num_feature_list}
| summarize  target_numeric_feature_value = make_list(numeric_feature_value), target_min = min(numeric_feature_value), target_max= max(numeric_feature_value), target_mean =percentiles(numeric_feature_value,50) by frequency=bin(['{time_stamp_col}'],{bin}), numeric_feature
| where array_length(target_numeric_feature_value)>0;
{base_table_name}
| where ['{time_stamp_col}'] >= datetime('{base_dt_from}') and ['{time_stamp_col}'] <= datetime('{base_dt_to}') 
| limit {limit}
| project {num_feature_list}, properties = pack_all()
| mv-apply numeric_feature = numeric_features to typeof(string) on (
    project numeric_feature, numeric_feature_value = tolong(properties[numeric_feature])
)
| project-away properties, {num_feature_list}
| summarize  base_numeric_feature_value = make_list(numeric_feature_value), base_min = min(numeric_feature_value), base_max= max(numeric_feature_value), base_mean =percentiles(numeric_feature_value,50) by numeric_feature
|where array_length(base_numeric_feature_value)>0
|join target on numeric_feature
| evaluate hint.distribution = per_node python(
//
typeof(*, wasserstein:double),               //  Output schema: append a new fx column to original table 
```
from scipy.stats import wasserstein_distance
#from scipy.special import kl_div
from scipy.spatial import distance
import numpy as np
result = df
n = df.shape[0]
distance1=[]
distance2 =[]
for i in range(n):
    distance1.append(wasserstein_distance(df['base_numeric_feature_value'][i], df['target_numeric_feature_value'][i]))

result['wasserstein'] =distance1

```
)|project frequency, numeric_feature, wasserstein, base_min, base_max,base_mean,target_min, target_max,target_mean

"""
        # print(query)

        return self.query(query)


    def sample_data_points(self, table_name, col_name, start_date, end_date=None, horizon=None, max_rows = 10000):
        timestamp_col = self.get_timestamp_col(table_name)
        if end_date is None:
            end_date = f"datetime_add('day',{horizon}, datetime('{start_date}'))"
        else:
            end_date = f"datetime('{end_date}')"
        query = f"{table_name}|where ['{timestamp_col}'] >= datetime('{start_date}') and ['{timestamp_col}'] <= {end_date}| sample {max_rows}|project {col_name}"
        return self.query(query)



