import os
import argparse
from azureml.core import Workspace
import pandas as pd
import os
import json
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import shutil
from azureml.core import Run

def least_confidence(tenant_id,client_id,client_secret,cluster_uri,db, scoring_table, model_name, limit=200, prob_limit=25):
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query= f"""
    let upper_prob= toscalar({scoring_table}| where model_name == '{model_name}'| summarize percentile(prob,{prob_limit}));
    let latest_model_version = toscalar({scoring_table}| where model_name == '{model_name}'| summarize last_model_version = max(model_version));
    {scoring_table}|where prob < upper_prob and model_version == latest_model_version and model_name == '{model_name}'| project file_path, prediction, prob, probs | sort by prob asc| limit {limit}
    """
    response = client.execute(db, query)

    return dataframe_from_result_table(response.primary_results[0])

def smallest_margin_uncertainty(tenant_id,client_id,client_secret,cluster_uri,db, scoring_table, model_name, limit=200, prob_limit=25):
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query = f"""
    let latest_model_version = toscalar({scoring_table}| where model_name == '{model_name}'| summarize last_model_version = max(model_version));
    let margins = {scoring_table}
    | where model_version == latest_model_version and model_name == '{model_name}'
    | mv-apply test=todynamic(probs) to typeof(double) on (top 2 by test | summarize differ=max(test) - min(test));
    let uppermargin = toscalar(margins | summarize percentile(differ, {prob_limit}));
    margins
    | where differ < uppermargin
    | sort by differ asc
    | limit {limit}
    | project file_path, prediction, prob, probs
    """
    response = client.execute(db, query)

    return dataframe_from_result_table(response.primary_results[0])

def entrophy_sampling(tenant_id,client_id,client_secret,cluster_uri,db, scoring_table, model_name, limit=200, prob_limit=75):
    KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster_uri, client_id, client_secret, tenant_id)
    client = KustoClient(KCSB_DATA)
    query = f"""
    let latest_model_version = toscalar({scoring_table}| where model_name == '{model_name}'| summarize last_model_version = max(model_version));
    let entrophyscores= {scoring_table}
    | where model_version == latest_model_version and model_name == '{model_name}'
    | mv-apply test=todynamic(probs) to typeof(double) on (summarize result = sum(test * -log(test)));
    let upper_entrophy_score = toscalar(entrophyscores| summarize entrophy_score=percentile(result,{prob_limit}));
    entrophyscores
    | where result > upper_entrophy_score 
    | sort by result desc
    | limit {limit}
    | project file_path, prediction, prob, probs
    """
    response = client.execute(db, query)

    return dataframe_from_result_table(response.primary_results[0])
