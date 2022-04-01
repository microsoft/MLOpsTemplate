
# Part 2: Use cloud scale compute to run, deploy and manage ML experiment with Azure ML

## Goal 
After successfully restructuring the jupyter notebook and run modules locally, your team wants to leverage Azure cloud to run the experiment at scale.
They also want to take advantage of experiment tracking and model management capabilities in Azure ML to keep track of experiment. 
Finally, the team wants to deploy the model as a rest endpoint for real time inferencing and experience the option of deploying it as batch inferencing.

## Pre-requisites
- Complete parts 0 and 1

## Tasks
- Review the templates (files without my_ prefix) under ```data_engineering```, ```training``` and   ```evaluating``` folders
- Go to src/workshop 
    ```bash 
    cd src/workshop
    ```
- Set defaults values
```bash 
az configure --defaults group=YOUR_RESOURCE_GROUP workspace=YOUR_WORKSPACE location=westus2

```
- Run individual modules with azure ml using the CLI v2. 
    - Run ```my_feature_engineering.py``` module under ```data_engineering``` folder
        - Review and update following parameters in the ```my_feature_engineering.yml```
            - Line # 13 ```compute: azureml:YOUR_COMPUTE_CLUSTER_NAME``` update ```YOUR_COMPUTE_CLUSTER_NAME```
        - Run the solution
            ```bash 
            az ml job create -f core/data_engineering/my_feature_engineering.yml 
            ```
    - run ```my_ml_training.py``` module under ```training``` folder
        - Review and update following parameters in the ```my_ml_training.yml```
            - Line # 13 ```compute: azureml:YOUR_COMPUTE_CLUSTER_NAME``` update ```YOUR_COMPUTE_CLUSTER_NAME```
        - Run the solution 
            ```bash 
            az ml job create -f core/training/my_ml_training.yml 
            ```
    - run ```my_ml_evaluating.py``` module under ```evaluating``` folder
        - Review and update the ```my_ml_evaluating.yml``` job file
            - line # 18, ```compute: azureml:YOUR_COMPUTE_CLUSTER_NAME``` update ```YOUR_COMPUTE_CLUSTER_NAME```
        - Run the solution 
            ```bash 
            az ml job create -f core/evaluating/my_ml_evaluating.yml 
            ```
- Review how metrics and  model are captured using mlflow inside train and evaluating python modules
- Create a pipeline that run feature_engineering, training and evaluation together
    - Review and update the ```my_training_pipeline.yml``` under ```pipelines``` 
            - Update  ```YOUR_COMPUTE_CLUSTER_NAME``` in the yml file like what you did for individual runs above
    - Run the pipeline  
        ```bash 
        az ml job create -f core/pipelines/my_training_pipeline.yml 
        ```
- Deploy to Azure ML Managed Online Endpoint
    - Update the ```my_endpoint.yml``` file and ```my_deployment.yml``` by filling the name of the endpoint (should be a unique name)
    - Use CLI to create your endpoint and create a green deployment 
    - Create a score_test script to call the deployed service with mock-up data
    - Run 
        ```bash 
        az ml online-endpoint create --file core/scoring/my_endpoint.yml 
        ```
        ```bash 
        az ml online-deployment create --file core/scoring/my_deployment.yml 
        ```
        ```bash 
        az ml online-endpoint invoke -n YOUR_ENDPOINT_NAME --deployment green --request-file core/scoring/scoring_test_request.json 
        ``` 
        Observe the returned scores from the endpoint evaluation.

### The entire training pipeline is illustrated with this diagram

![training_pipeline](images/training_pipeline.png)
## Success criteria
- Run the modules individually in Azure 
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
