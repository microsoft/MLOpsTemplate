import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder,ClientRequestProperties
from azure.kusto.data.helpers import dataframe_from_result_table
from monitoring import KV_SP_ID, KV_SP_KEY, KV_ADX_DB, KV_ADX_URI, KV_TENANT_ID
import concurrent.futures
from datetime import timedelta
import pandas as pd
from azure.ml import MLClient
from azure.ml import command, Input
from azure.identity import DefaultAzureCredential
from azure.ml.entities import Environment, BuildContext
from textwrap import dedent
import shutil


class Drift_Analysis():
    def __init__(self,ws=None,tenant_id=None, client_id=None,client_secret=None,cluster_uri=None,database_name=None):

        if ws is not None:
            kv = ws.get_default_keyvault()
            self.client_id = kv.get_secret(KV_SP_ID)
            self.client_secret = kv.get_secret(KV_SP_KEY)
            self.cluster_uri = kv.get_secret(KV_ADX_URI)
            self.database_name = kv.get_secret(KV_ADX_DB)
            self.tenant_id = kv.get_secret(KV_TENANT_ID)
        elif tenant_id is None: 
            #check if this under AML run
            try:
                from azureml.core import Run
                run = Run.get_context()
                ws = run.experiment.workspace
                kv = ws.get_default_keyvault()
                self.client_id = kv.get_secret(KV_SP_ID)
                self.client_secret = kv.get_secret(KV_SP_KEY)
                self.cluster_uri = kv.get_secret(KV_ADX_URI)
                self.database_name = kv.get_secret(KV_ADX_DB)
                self.tenant_id = kv.get_secret(KV_TENANT_ID)
            except:
                Exception("If not in AML run, need to provide either workspace object or  service principal credential and ADX cluster details")
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
    def analyze_drift(self,base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit=10000000, concurrent_run=True):
        base_tbl_columns = self.list_table_columns(base_table_name)
        target_tbl_columns = self.list_table_columns(target_table_name)
        common_columns = base_tbl_columns.merge(target_tbl_columns)
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
                categorical_output_future = executor.submit(self.analyze_drift_categorical, categorical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to,bin, limit)
                numberical_output_future = executor.submit(self.analyze_drift_numerical,numerical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit)
                categorical_output = categorical_output_future.result()
                numberical_output = numberical_output_future.result()
        else:
            categorical_output =self.analyze_drift_categorical(categorical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to,bin, limit)
            numberical_output = self.analyze_drift_numerical(numerical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit)



        output =numberical_output.merge(categorical_output, how="outer", on = "target_start_date")
        return output
    def analyze_drift_v2(self,base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit=10000000, concurrent_run=True):
        base_tbl_columns = self.list_table_columns(base_table_name)
        target_tbl_columns = self.list_table_columns(target_table_name)
        common_columns = base_tbl_columns.merge(target_tbl_columns)
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
                categorical_output_futures=[]
                numberical_output_futures =[]

                for cat_feature in categorical_columns:
                    categorical_output_future = executor.submit(self.analyze_drift_categorical, [cat_feature], time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to,bin, limit)
                    categorical_output_futures.append(categorical_output_future)

                for num_feature in numerical_columns:
                    numberical_output_future = executor.submit(self.analyze_drift_numerical,[num_feature], time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit)
                    numberical_output_futures.append(numberical_output_future)

                categorical_output = pd.concat([categorical_output_future.result() for categorical_output_future in categorical_output_futures])
                numberical_output =  pd.concat([numberical_output_future.result() for numberical_output_future in numberical_output_futures]) 
        else:
            categorical_output =self.analyze_drift_categorical(categorical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to,bin, limit)
            numberical_output = self.analyze_drift_numerical(numerical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit)



        output =numberical_output.merge(categorical_output, how="outer", on = "target_start_date")
        return output
    def analyze_drift_categorical(self,categorical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit=10000000):
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
{target_table_name}
| where ['{time_stamp_col}'] >= datetime('{target_dt_from}') and ['{time_stamp_col}'] <= datetime('{target_dt_to}') 
| limit {limit}
| project ['{time_stamp_col}'], {cat_feature_list}, properties = pack_all()
| mv-apply categorical_feature = categorical_features to typeof(string) on (
    project categorical_feature, categorical_feature_value = tolong(properties[categorical_feature])
)
| project-away properties, {cat_feature_list}
| summarize target_categorical_feature_value = make_list(categorical_feature_value), target_dcount= dcount(categorical_feature_value) by target_start_date=bin(['{time_stamp_col}'],{bin}),categorical_feature
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
import random
import numpy as np
result = df
n = df.shape[0]
distance2 =[]
for i in range(n):
    base_features = df["base_categorical_feature_value"][i]
    target_features = df["target_categorical_feature_value"][i]
    if len(target_features) > len(base_features):
        target_features = random.sample(target_features, len(base_features))
    elif len(target_features) < len(base_features):
        base_features = random.sample(base_features, len(target_features))
    distance2.append(distance.euclidean(base_features, target_features))
result['euclidean'] =distance2

```
)
|extend target_end_date = target_start_date+ {bin}
|project target_start_date, target_end_date, categorical_feature,euclidean,  base_dcount,target_dcount
        
        """
        # print(query)
        return self.query(query)

    def analyze_drift_numerical(self,numerical_columns, time_stamp_col, base_table_name,target_table_name, base_dt_from, base_dt_to, target_dt_from, target_dt_to, bin, limit=10000000):
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
{target_table_name}
| where ['{time_stamp_col}'] >= datetime('{target_dt_from}') and ['{time_stamp_col}'] <= datetime('{target_dt_to}') 
| limit {limit}
| project ['{time_stamp_col}'], {num_feature_list}, properties = pack_all()
| mv-apply numeric_feature = numeric_features to typeof(string) on (
    project numeric_feature, numeric_feature_value = tolong(properties[numeric_feature])
)
| project-away properties, {num_feature_list}
| summarize  target_numeric_feature_value = make_list(numeric_feature_value), target_min = min(numeric_feature_value), target_max= max(numeric_feature_value), target_mean =percentiles(numeric_feature_value,50) by target_start_date=bin(['{time_stamp_col}'],{bin}), numeric_feature
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
)
|extend target_end_date = target_start_date+ {bin}
|project target_start_date,target_end_date, numeric_feature, wasserstein, base_min, base_max,base_mean,target_min, target_max,target_mean

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

    def get_categorical_columns_distribution(self,categorical_columns, time_stamp_col, target_table_name, target_dt_from, target_dt_to, bin):
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
{target_table_name}
| where ['{time_stamp_col}'] >= datetime('{target_dt_from}') and ['{time_stamp_col}'] <= datetime('{target_dt_to}') 
| project ['{time_stamp_col}'], {cat_feature_list}, properties = pack_all()
| mv-apply categorical_feature = categorical_features to typeof(string) on (
    project categorical_feature, categorical_feature_value = tolong(properties[categorical_feature])
)
|summarize count = count() by categorical_feature, categorical_feature_value, bin(['{time_stamp_col}'],{bin})
|summarize value_list= make_list(categorical_feature_value), count_list = make_list(['count']) by ['{time_stamp_col}'],feature =categorical_feature
"""
        # print(query)
        return self.query(query)
    
    def get_numerical_column_distribution(self, numerical_column, time_stamp_col,target_table_name, target_dt_from, target_dt_to, bin):

        query = f"""
let tbl = {target_table_name}| where ['{time_stamp_col}'] >= datetime('{target_dt_from}') and ['{time_stamp_col}'] <= datetime('{target_dt_to}');
let bin_size_temp = toscalar(tbl|summarize (max({numerical_column})- min({numerical_column}))/50);
tbl|summarize count = count() by bin({numerical_column},bin_size_temp), bin(['{time_stamp_col}'],{bin})
| summarize value_list= make_list({numerical_column}), count_list = make_list(['count']) by ['{time_stamp_col}']
        """
        # print(query)

        return self.query(query)

    def get_features_distributions(self,target_table_name, target_dt_from, target_dt_to, bin, concurrent_run=True):
        target_tbl_columns = self.list_table_columns(target_table_name)
        timestamp_cols = target_tbl_columns[target_tbl_columns['AttributeType']=='DateTime']
        if timestamp_cols.shape[0]==0:
            raise Exception("No timestamp column found! ")
        if "timestamp" in timestamp_cols['AttributeName'].values:
            time_stamp_col ='timestamp'
        else:
            time_stamp_col = timestamp_cols['AttributeName'].values[0]
        numerical_columns = target_tbl_columns[(target_tbl_columns['AttributeType']!='DateTime')&(target_tbl_columns['AttributeType']!='StringBuffer')]
        numerical_columns = numerical_columns['AttributeName'].values
        categorical_columns = target_tbl_columns[target_tbl_columns['AttributeType']=='StringBuffer']['AttributeName'].values

        if concurrent_run:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                categorical_output=[]
                numberical_output_futures ={}
                numberical_output=[]
                categorical_output_future = executor.submit(self.get_categorical_columns_distribution, categorical_columns, time_stamp_col,target_table_name,  target_dt_from, target_dt_to,bin)
                for num_feature in numerical_columns:
                    numberical_output_future = executor.submit(self.get_numerical_column_distribution,num_feature, time_stamp_col,target_table_name, target_dt_from, target_dt_to, bin)
                    numberical_output_futures[num_feature] = numberical_output_future

                categorical_output = categorical_output_future.result()
                for num_feature in numerical_columns:
                    num_output = numberical_output_futures[num_feature].result()
                    num_output["feature"]=num_feature
                    numberical_output.append(num_output)

                numberical_output =  pd.concat(numberical_output) 

        else:
            categorical_output =self.get_categorical_columns_distribution(categorical_columns, time_stamp_col,target_table_name,  target_dt_from, target_dt_to,bin)

            numberical_output=[]
            for num_feature in numerical_columns:
                feature_output = self.get_numerical_column_distribution(num_feature, time_stamp_col,target_table_name, target_dt_from, target_dt_to, bin)
                feature_output["feature"]=num_feature
                numberical_output.append(feature_output)
            numberical_output =  pd.concat(numberical_output) 

        output =pd.concat([numberical_output, categorical_output])
        return output
def execute_drift_detect_job(subscription_id="0e9bace8-7a81-4922-83b5-d995ff706507",resource_group="azureml",workspace="ws01ent", compute_name ='DS11', experiment_name= "drift-analysis-job", base_table_name ="", 
target_table_name ="ISDWeather", base_dt_from ="2013-04-13", base_dt_to= "2014-05-13",target_dt_from="2013-04-13", target_dt_to="2014-05-13", bin="7d", limit=3000000):

    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group, workspace
    )

    os.makedirs(".tmp", exist_ok=True)
    conda_file_content= """
    channels:
    - anaconda
    - conda-forge
    dependencies:
    - python=3.8.1
    - pip:
        - azureml-mlflow==1.41.0
        - azure-identity==1.9.0
        - azure-identity==1.9.0
        - azure-mgmt-kusto==2.2.0
        - azure-kusto-data==3.1.2
        - azure-kusto-ingest==3.1.2
        - dash==2.3.1
        - plotly==5.7.0
        - azureml-defaults==1.41.0
        - pandas
        - --extra-index-url https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2
        - azure-ml==0.0.61212840
        - git+https://github.com/microsoft/MLOpsTemplate.git@monitoring-main#subdirectory=src/utilities
    - matplotlib
    - pip < 20.3
    name: drift_detection
    """

    source_file_content="""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
    from monitoring.drift_analysis import Drift_Analysis
    from monitoring.data_collector import Online_Collector
    import calendar;
    import time;
    import argparse
    import pandas as pd
    def parse_args():
        # setup arg parser
        parser = argparse.ArgumentParser()

        parser.add_argument("--base_table_name", type=str)
        parser.add_argument("--target_table_name", type=str)
        parser.add_argument("--base_dt_from", type=str)
        parser.add_argument("--base_dt_to", type=str)
        parser.add_argument("--target_dt_from", type=str)
        parser.add_argument("--target_dt_to", type=str)
        parser.add_argument("--bin", type=str, default="7d")
        parser.add_argument("--limit", type=str, default="100000")
        parser.add_argument("--drift_result_table", type=str, default="data_drift_result")
        parser.add_argument("--feature_distribution_table", type=str, default="feature_distribution")


        # parse args
        args = parser.parse_args()

        # return args
        return args
    def main(args):
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        run_id = args.base_table_name+"_"+args.target_table_name+"_"+ str(ts)
        drift_analysis =Drift_Analysis()

        df_output = drift_analysis.analyze_drift(limit=args.limit,base_table_name = args.base_table_name,target_table_name=args.target_table_name, base_dt_from=args.base_dt_from, base_dt_to=args.base_dt_to, target_dt_from=args.target_dt_from, target_dt_to=args.target_dt_to, bin=args.bin)
        df_output['base_start_date']=pd.to_datetime(args.base_dt_from)
        df_output['base_end_date']=pd.to_datetime(args.base_dt_to)
        # df_output['target_start_date']=pd.to_datetime(df_output['target_start_date'])
        # df_output['target_end_date']=pd.to_datetime(df_output['target_end_date'])
        df_output.drop(['target_end_date_x','target_end_date_y'], axis =1)
        df_output['run_id'] = run_id
        for metric in ['wasserstein', 'base_min', 'base_max','base_mean','target_min', 'target_max','target_mean', 'euclidean','base_dcount','target_dcount']:
            df_output[metric]= df_output[metric].astype("float")
        data_drift_collector = Online_Collector(args.drift_result_table)
        data_drift_collector.batch_collect(df_output)
        feature_distribution = drift_analysis.get_features_distributions(target_table_name=args.target_table_name, target_dt_from=args.target_dt_from, target_dt_to=args.target_dt_to, bin=args.bin)
        feature_distribution['run_id'] = run_id
        feature_ditriction_collector = Online_Collector(args.feature_distribution_table)
        feature_ditriction_collector.batch_collect(feature_distribution)

    if __name__ == "__main__":
        # parse args
        args = parse_args()

        # run main function
        main(args)
        
    """
    source_file = open(".tmp/source_file.py", "w")
    source_file.write(dedent(source_file_content))
    source_file.close()
    conda_file = open(".tmp/conda.yml", "w")
    conda_file.write(dedent(conda_file_content))
    conda_file.close()
    env_docker_conda = Environment(
        image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04",
        conda_file=".tmp/conda.yml",
        name="drift_analysis_job",
        description="Environment created from a Docker image plus Conda environment.",
    )
    job = command(
    code=".tmp",  # local path where the code is stored
    command="python source_file.py --base_table_name ${{inputs.base_table_name}} --target_table_name ${{inputs.target_table_name}} --base_dt_from ${{inputs.base_dt_from}} --base_dt_to ${{inputs.base_dt_to}} --target_dt_from ${{inputs.target_dt_from}} --target_dt_to ${{inputs.target_dt_to}} --bin ${{inputs.bin}} --limit ${{inputs.limit}}",
    inputs={"base_table_name": base_table_name, "target_table_name": target_table_name, "base_dt_from":base_dt_from, "base_dt_to": base_dt_to,"target_dt_from": target_dt_from, "target_dt_to":target_dt_to, "bin":bin, "limit":limit},
    environment=env_docker_conda,
    compute=compute_name,
    display_name=experiment_name,
    experiment_name= experiment_name
    # description,
    
    )

    returned_job = ml_client.create_or_update(job)
    shutil.rmtree(".tmp")
