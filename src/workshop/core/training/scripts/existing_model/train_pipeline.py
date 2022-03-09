from azureml.core import Dataset, Environment, Workspace, ScriptRunConfig
from azureml.core.experiment import Experiment
from azureml.core.compute import ComputeTarget
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.steps import PythonScriptStep, AutoMLStep
from azureml.pipeline.core import Pipeline, PipelineData, TrainingOutput
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.conda_dependencies import CondaDependencies
from azureml.data import OutputFileDatasetConfig, DataType
from azureml.train.automl import AutoMLConfig
import logging
import sys
import os
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..')))
from scripts.authentication.service_principal import ws
from azureml.core.runconfig import DEFAULT_CPU_IMAGE
from azureml.core.runconfig import DockerConfiguration
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def main():

    def_blob_store = ws.get_default_datastore()
    target_cluster = ComputeTarget(workspace=ws, name='cpu-cluster')
    #env= Environment.get(workspace=ws, name='model_env')
    experiment = Experiment(ws, 'TAXI-FARE')
    run_config = RunConfiguration()
    docker_config = DockerConfiguration(use_docker=True)
    run_config.environment.docker.base_image = DEFAULT_CPU_IMAGE
    run_config.docker = docker_config
    run_config.environment.python.user_managed_dependencies = False

    # Specific packages
    run_packages = CondaDependencies()
    run_packages.add_pip_package('pip')
    run_packages.add_pip_package('python-dotenv')
    run_packages.add_pip_package('azureml-opendatasets')
    #run_packages.add_pip_package('scikit-learn')
    run_config.environment.python.conda_dependencies = run_packages

    # Create pipeline parameter for the taxi fare data
    start_date_param = PipelineParameter(name='start_date_param', default_value="2015-01-01")
    end_date_param = PipelineParameter(name='end_date_param', default_value="2015-03-31")

    raw_source = OutputFileDatasetConfig(destination=(def_blob_store,'/raw/')).as_mount()
    raw_filename = 'raw_taxi_fare'
    load_data_step = PythonScriptStep(
            name='Pull data and register raw dataset',
            source_directory='.',
            script_name='./scripts/existing_model/register_dataset.py',
            compute_target=target_cluster,
            arguments=[
                '--start_date_arg', start_date_param,
                '--end_date_arg', end_date_param,
                '--output_filepath', raw_source,
                '--output_filename', raw_filename,
                ],
            runconfig=run_config,
            allow_reuse=False
            )

    engineered_source = OutputFileDatasetConfig(destination=(def_blob_store,'/processed/')).as_mount()
    engineered_filename = 'training_data'
    data_transform_step = PythonScriptStep(
            name='Feature engineer raw attributes',
            source_directory='.',
            script_name='./scripts/existing_model/feature_engineer.py',
            compute_target=target_cluster,
            arguments=[
                '--start_date_arg', start_date_param,
                '--end_date_arg', end_date_param,
                '--input_filepath', raw_source.as_input(),
                '--input_filename', raw_filename,
                '--training_data_filepath', engineered_source,
                '--training_data_filename', engineered_filename,
                ],
            runconfig=run_config,
            allow_reuse=False
            )
    
    # Read in the data from the prior step 
    train_data = engineered_source.read_delimited_files(set_column_types={"totalAmount": DataType.to_float()})
    
    metrics_data = PipelineData(    
            name='metrics_data',    
            datastore=def_blob_store,    
            pipeline_output_name='metrics_output',    
            training_output=TrainingOutput(type='Metrics')    
            )    
        
    model_data = PipelineData(    
            name='best_model_data',    
            datastore=def_blob_store,    
            pipeline_output_name='model_output',    
            training_output=TrainingOutput(type='Model')    
            )

    automl_settings = {
        "iteration_timeout_minutes": 10,
        "experiment_timeout_hours": 2,
        "max_concurrent_iterations":4,
        "enable_early_stopping": True,
        "primary_metric": 'spearman_correlation',
        "featurization": 'auto',
        "verbosity": logging.INFO,
        "n_cross_validations": 5
    }

    automl_config = AutoMLConfig(
            task='regression',
            compute_target=target_cluster,
            #debug_log='automated_ml_errors.log',
            training_data=train_data.as_input(),
            label_column_name="totalAmount",
            **automl_settings
            )

    train_step = AutoMLStep(
            name='Regression modeling for taxi fare data',
            automl_config=automl_config,    
            passthru_automl_config=False,    
            outputs=[metrics_data,model_data],    
            enable_default_model_output=True,
            enable_default_metrics_output=True,
            allow_reuse=True #if False, will trigger a new run, else re-use the existing output
        )

    # Register the model
    model_name = PipelineParameter("model_name", default_value="bestModel")
    register_model_step = PythonScriptStep(
            source_directory='.',
            script_name="./scripts/existing_model/register_model.py",
            name="Register the best model",
            arguments=[
                "--model_name", model_name,
                "--model_path", model_data
                ],
            inputs=[model_data],
            compute_target=target_cluster,
            runconfig=run_config,
            allow_reuse=False
            )

    # Pipeline integration
    steps = [ load_data_step, data_transform_step, train_step, register_model_step]
    pipeline = Pipeline(workspace=ws, steps=steps)
    pipeline_run = experiment.submit(pipeline, pipeline_parameters={
        "start_date_param":"2015-01-01",
        "end_date_param":"2015-01-31"
        })
    pipeline_run.wait_for_completion()

    ## Publish the pipeline
    published_pipeline = pipeline_run.publish_pipeline(
            name='Taxi fare data',
            description='Pipeline to run time series prediction for given stock ticker',
            version='1.0'
            )

if __name__ == "__main__":
    main()
