
# Part 2: Use cloud scale compute to run, deploy and manage ML experiment with Azure ML

## Goal 
After successfully restructuring the jupyter notebook and run modules locally, your team wants to leverage Azure cloud to run the experiment at scale.
They also want to take advantage of experiment tracking and model management capabilities in Azure ML to keep track of experiment. 
Finally, the team wants to deploy the model as a rest endpoint for real time inferencing and experience the option of deploying it as batch inferencing.

## Pre-requisites
- Complete parts 0 and 1

## Tasks
- Review the templates (files without my_ prefix) under ```data_engineering```, ```training``` and   ```evaluating``` folders
- Run individual modules with azure ml using the CLI v2. 
    - Run ```my_feature_engineering.py``` module under ```data_engineering``` folder
        - Review and update following parameters in the ```my_feature_engineering.yml```
            - ```input_folder```: path to the folder in datastore location, e.g. ```azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
        - Run the solution
            - Go to src/workshop ```cd src/workshop```
            - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
            - Run ```az ml job create -f core/data_engineering/my_feature_engineering.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME```

    - run ```my_ml_training.py``` module under ```training``` folder
        - Review and update following parameters in the ```my_ml_training.yml```
            - ```input_folder```: path to the folder in datastore location, e.g. ```azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
        - Check and run reference solution at ```core/training/my_ml_training.yml```
            - Go to src/workshop ```cd src/workshop```
            - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
            - Run ```az ml job create -f core/training/my_ml_training.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME```
    - run ```my_ml_evaluating.py``` module under ```evaluating`` folder
        - Review and update the ```my_ml_evaluating.yml``` job file
            - ```prep_data```: ```folder: azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
            - model_folder:: ```folder: azureml://datastores/{NAME_OF_YOUR_DATASTORE}/paths/mlops_workshop_data```
            - run_mode: ```"remote"```
        - Run the solution 
            - Go to src/workshop ```cd src/workshop```
            - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
            - Run ```az ml job create -f core/evaluating/my_ml_evaluating.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME```
- Review how metrics and  model are captured using mlflow inside python files
- Create a pipeline that run feature_engineering, training and evaluation together
    - Review and update the ```my_training_pipeline.yml``` under ```pipelines``` 
            - Change the names of compute cluster  and the data store in the yml file 
    - Run the pipeline  
    - Run solution 
        - Go to src/workshop ```cd src/workshop```
        - Run ```az ml job create -f core/pipelines/my_training_pipeline.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE_NAME```
- Deploy to Azure ML Managed Online Endpoint
    - Review the template in ```scoring``` folder
    - Update the ```my_endpoint.yml``` file and ```my_deployment.yml``` file
    - Use CLI to create your endpoint and create a blue deployment 
    - Create a score_test script to call the deployed service with mock-up data
    - Run reference solution
        - Go to src/workshop ```cd src/workshop```
        - Change the names of compute cluster in the yml file to (default is ```DS11```) and the data store (default is ```mltraining```)
        - Run ```az ml online-endpoint create --file core/scoring/my_endpoint.yml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE```
        - Run ```az ml online-deployment create --file core/scoring/my_deployment.yaml --resource-group YOUR_RESOURCE_GROUP --workspace-name YOUR_WORKSPACE```
        - Run ```az ml online-endpoint invoke -n mlops-workshop-endpoint --deployment blue --request-file core/scoring/scoring_test_request.json --resource-group YOUR_WORKSPACE --workspace-name YOUR_WORKSPACE``` and observe the returned scores from the endpoint evaluation.
- Deploy to Azure ML Batch Endpoint (@todo)

### The entire training pipeline is illustrated with this diagram

![training_pipeline](images/training_pipeline.png)
## Success criteria
- Run the module individually in Azure 
- Capture metrics and models in ml_training and ml_evaluating modules
- Run three modules together in a pipeline
- Model is deployed successfully to managed endpoint. Testing is successful


## Reference materials
- Azure ML CLI v2 tutorial: https://docs.microsoft.com/en-us/learn/paths/train-models-azure-machine-learning-cli-v2/
- Azure ML CLI single job examples: https://github.com/Azure/azureml-examples/tree/main/cli/jobs/single-step
- Azure ML CLI pipeline examples: https://github.com/Azure/azureml-examples/tree/main/cli/jobs/pipelines
- Deploy to managed online endpoint: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-managed-online-endpoints
- Deploy to batch endpoint: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-batch-endpoint

---

## [To Next Part 3](part_3.md)
