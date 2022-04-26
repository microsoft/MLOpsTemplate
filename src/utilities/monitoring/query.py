from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
import threading, queue
import time
import plotly.graph_objects as go
import numpy as np
from azure.kusto.ingest import (
    QueuedIngestClient
)
import pandas as pd
import numpy as np
from dash import dcc, html
import plotly
from dash.dependencies import Input, Output
from jupyter_dash import JupyterDash
class KustoQuery():
    def __init__(self, tenant_id, client_id,client_secret,cluster_uri,database_name,table_name):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.cluster_uri = cluster_uri
        self.cluster_ingest_uri = cluster_uri.split(".")[0][:8]+"ingest-"+cluster_uri.split(".")[0].split("//")[1]+"."+".".join(cluster_uri.split(".")[1:])
        self.database_name = database_name
        self.client_secret=client_secret
        self.table_name= table_name
        KCSB_DATA = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_uri, self.client_id, self.client_secret, self.tenant_id)
        KCSB_DATA_INGEST = KustoConnectionStringBuilder.with_aad_application_key_authentication(self.cluster_ingest_uri, self.client_id, self.client_secret, self.tenant_id)
        self.kusto_client = KustoClient(KCSB_DATA)
        self.queue_client = QueuedIngestClient(KCSB_DATA_INGEST)
    def query(self, query):
        response = self.kusto_client.execute(self.database_name, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe
    def retrieve_last_records(self,ts_col_name = "timestamp", max_records = 1000, ago ='5m'):
        query = f"{self.table_name}|where {ts_col_name}> ago({ago})| sort by {ts_col_name}|take({max_records})"
        response = self.kusto_client.execute(self.database_name, query)
        dataframe = dataframe_from_result_table(response.primary_results[0])
        return dataframe
    def anomaly_detection(self, min_t, max_t, step, metric, agg, ts_col, groupby, sensitivity=1.5, filter=None):
        if filter:
            filter =f"| where {groupby} == '{filter}' "
        else:
            filter = ""
        query =f"""
        let min_t = datetime({min_t});
        let max_t = datetime({max_t});
        let dt = {step};
        {self.table_name}
        | make-series num={agg}({metric}) on {ts_col} from min_t to max_t step dt by {groupby} 
        {filter}
        | extend (anomalies, score, baseline) = series_decompose_anomalies(num, {sensitivity}, -1, 'linefit')
        """
        output= self.query(query)
        groups = np.unique(output[groupby])
        for group in groups:
            output_group = output[output[groupby]==group]
            anomalies = np.array(output_group["anomalies"].values[0])
            anomalies =np.array(output_group["num"].values[0])*anomalies
            anomalies = [None if i == 0 else i for i in anomalies]
            fig = go.Figure([go.Scatter(x=output_group[ts_col].values[0], y=output_group["num"].values[0], name=f"Actual_{group}")])
            fig.add_trace(go.Scatter(mode="markers", x=output_group[ts_col].values[0], y=anomalies, name=f"Anomalies_{group}"))

            fig.add_trace(go.Scatter(x=output_group[ts_col].values[0], y=output_group["baseline"].values[0], name=f"baseline_{group}"))
            fig.show()


class RT_Visualization(KustoQuery):
    def scatter(self, max_records, ago,groupby, y_metric, x_metric='timestamp'):

        app = JupyterDash(__name__)

        app.layout = html.Div(
            html.Div([
                html.H4('Real Time Monitoring'),
                # html.Div(id='live-update-text'),
                dcc.Graph(id='live-update-graph'),
                dcc.Interval(
                    id='interval-component',
                    interval=1*2000, # in milliseconds
                    n_intervals=0
                )
            ])
        )

        @app.callback(Output('live-update-graph', 'figure'),
                    Input('interval-component', 'n_intervals'))
        def update_graph_live(n):
            data = self.retrieve_last_records(ago=ago, max_records=max_records)
            groupby_items = np.unique(data[groupby])

            # Create the graph with subplots
            fig = plotly.tools.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
            fig['layout']['margin'] = {
                'l': 30, 'r': 10, 'b': 30, 't': 10
            }
            fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
            for item in groupby_items:
                data_item = data[data[groupby]==item]
                fig.append_trace({
                    'x': data_item[x_metric],
                    'y': data_item[y_metric],
                    'name': f"{groupby} "+str(item),
                    'mode': 'lines+markers',
                    'type': 'scatter',

                }, 1, 1)
            return fig


        app.run_server(mode='inline')

