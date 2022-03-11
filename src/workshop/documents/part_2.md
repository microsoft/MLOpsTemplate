
# Part 2: Use cloud scale compute and monitor experiment with Azure ML

## Goal 
After successfully restructuring the jupyter notebook and run modules locally, your team wants to leverage Azure cloud to run the experiment at scale.
They also want to take advantage of experiment tracking and model management capabilities in Azure ML to keep track of experiment.   

## Pre-requisites
- Complete part 0 and 1

## Tasks
- Review the templates under ```data_engineering```, ```training``` and   ```evaluating``` folders
- Run individual modules with azure ml using the CLI v2. 
    - Run ```feature_engineering.py``` module under ```my_data_engineering``` folder
        - Add following parameters from the yml job file
            - ```input_folder```: path to the folder in datastore location, e.g. ```azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
        - Leave default values for ```prep_data``` which is ```data```, ```public_holiday_file_name``` which is ```holidays.parquet```,  ```weather_file_name``` which is ```weather.parquet```, ```nyc_file_name```which is ```green_taxi.parquet``` 
    - run ```ml_training.py``` module under ```my_training`` folder
        - Add following parameters from the yml job file
            - ```input_folder```: path to the folder in datastore location, e.g. ```azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
        - Leave default values for other parameters 
    - run ```ml_evaluating.py``` module under ```my_evaluating`` folder
        - Accept following parameters:
            - ```prep_data```: ```folder: azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
            - model_folder:: ```folder: azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
            - run_mode: ```"remote"```
        - Leave default values for other parameters 
- Capture metrics and log model using mlflow 
- Create a pipeline that run feature_engineering, training and evaluation together
    - Create a folder for pipelines ```my_pipelines``` 
    - Review the ```training_pipeline.yml``` under ```pipelines`` and create your own pipeline in ```my_pipelines``` 
    - Run the pipeline  
- Create a score file in ```my_scoring``` folder and deploy to Azure ML Managed Online Endpoint
    - Review the template in ```scoring``` folder
    - Use CLI to create your endpoint and create a blue deployment 
    - Create a score_test script to call the deployed service with mock-up data

## Success criteria
- Run the module individually in Azure 
- Capture metrics and models in ml_training and ml_evaluating modules
- Run three modules together in a pipeline
- Model is deployed successfully to managed endpoint. Testing is successful


## Reference materials
- Azure ML CLI single job examples: https://github.com/Azure/azureml-examples/tree/main/cli/jobs/single-step
- Azure ML CLI pipeline examples: https://github.com/Azure/azureml-examples/tree/main/cli/jobs/pipelines
- Deploy to managed online endpoint: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-managed-online-endpoints

