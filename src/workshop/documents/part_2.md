
# Part 2: Use cloud scale compute and monitor experiment with Azure ML

## Goal 
After successfully restructuring the jupyter notebook and run modules locally, your team wants to leverage Azure cloud to run the experiment at scale.
They also want to take advantage of experiment tracking and model management capabilities in Azure ML to keep track of experiment.   

## Pre-requisites
- Complete parts 0 and 1

## Tasks
- Review the templates under ```data_engineering```, ```training``` and   ```evaluating``` folders
- Run individual modules with azure ml using the CLI v2. 
    - Run ```feature_engineering.py``` module under ```my_data_engineering``` folder
        - Add following parameters to the yml job file
            - ```input_folder```: path to the folder in datastore location, e.g. ```azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
        - Leave default values for  ```prep_data``` which is ```data```, ```public_holiday_file_name``` which is ```holidays.parquet```,  ```weather_file_name``` which is ```weather.parquet```, ```nyc_file_name```which is ```green_taxi.parquet``` at ``feature_engineering.py``
        - Create environment file ```conda_feature_engineering.yml``` by copying the same file from ```core/data_engineering/``` folder 
        - Check and run reference solution at ```core/data_engineering/feature_engineering.yml```
            - Go to src/workshop ```cd src/workshop```
            - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
            - Run ```az ml job create -f core/data_engineering/feature_engineering.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME``

    - run ```ml_training.py``` module under ```my_training`` folder
        - Add following parameters to the yml job file
            - ```input_folder```: path to the folder in datastore location, e.g. ```azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
        - Leave default values for other parameters at ```ml_training.py```
        - Create environment file ```conda_ml_training.yml``` by copying the same file from ```core/training/``` folder 
        - Check and run reference solution at ```core/training/ml_training.yml```
            - Go to src/workshop ```cd src/workshop```
            - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
            - Run ```az ml job create -f core/training/ml_training.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME``
    - run ```ml_evaluating.py``` module under ```my_evaluating`` folder
        - Accept following parameters to yml job file
            - ```prep_data```: ```folder: azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
            - model_folder:: ```folder: azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
            - run_mode: ```"remote"```
        - Leave default values for other parameters at python file
        - Create environment file ```conda_ml_evaluating.yml``` by copying the same file from ```core/evaluating/``` folder 
        - Check and run reference solution at ```core/evaluating/ml_evaluating.yml```
            - Go to src/workshop ```cd src/workshop```
            - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
            - Run ```az ml job create -f core/evaluating/ml_evaluating.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME``
- Capture metrics and log model using mlflow 
- Create a pipeline that run feature_engineering, training and evaluation together
    - Create a folder for pipelines ```my_pipelines``` 
    - Review the ```training_pipeline.yml``` under ```pipelines`` and create your own pipeline in ```my_pipelines``` 
    - Run the pipeline  
    - Check and run reference solution at ```core/pipelines/training_pipeline.yml```
        - Go to src/workshop ```cd src/workshop```
        - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
        - Run ```az ml job create -f pipelines/training_pipeline.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME``
- Deploy to Azure ML Managed Online Endpoint
    - Review the template in ```scoring``` folder
    - Prepare ```conda.yml``` environment file, ```endpoint.yml``` file and ```deplyment.yml``` file
    - Use CLI to create your endpoint and create a blue deployment 
    - Create a score_test script to call the deployed service with mock-up data
    - Run reference solution
        - Go to src/workshop ```cd src/workshop```
        - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
        - Run ```az ml online-endpoint create --file scoring/endpoint.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE```
        - Run ```az ml online-deployment create --file scoring/deployment.yaml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE```

### The entire training pipeline is illustrated with this diagram

![training_pipeline](images/training_pipeline.png)
## Success criteria
- Run the module individually in Azure 
- Capture metrics and models in ml_training and ml_evaluating modules
- Run three modules together in a pipeline
- Model is deployed successfully to managed endpoint. Testing is successful


## Reference materials
- Azure ML CLI single job examples: https://github.com/Azure/azureml-examples/tree/main/cli/jobs/single-step
- Azure ML CLI pipeline examples: https://github.com/Azure/azureml-examples/tree/main/cli/jobs/pipelines
- Deploy to managed online endpoint: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-managed-online-endpoints


---

## [To Next Part 3](part_3.md)
