
# Part 2: Use cloud scale compute to run, deploy and manage ML experiment with Azure ML

## Pre-requisites
- Complete [Part 0](part_0.md), [Part 1](part_1.md)
- Run each module feature_engineering, ml_training and evaluating successfully in local mode
- Have Azure ML workspace setup with a Compute Cluster

## Summary 
After successfully restructuring the jupyter notebook and run modules locally, your team wants to leverage Azure cloud to run the experiment at scale.
They also want to take advantage of experiment tracking and model management capabilities in Azure ML to keep track of experiment. 
Finally, the team wants to deploy the model as a rest endpoint for real time inferencing and experience the option of deploying it as batch inferencing.
To accomplish these goals, you will perform the following:
- Run feature_engineering module as a job in Azure AML 
- Run ml_training module as a job in Azure ML and observe the experiment metrics 
- Run evaluating module as a job in Azure ML and observe how the model can be registered to Azure ML model's repo
- Run the three modules together as a pipeline
- Deploy and test the produced ML model as an API using Azure Managed Online Endpoint


## Steps
- Go to src/workshop 
    ```bash 
    cd src/workshop
    ```
- Set defaults values
    ```bash 
    az configure --defaults group=YOUR_RESOURCE_GROUP workspace=YOUR_WORKSPACE

    ```
- Run individual modules with azure ml using the CLI v2. 
    - Run ```feature_engineering.py``` module under ```data_engineering``` folder
        - Review and update following parameters in the ```feature_engineering.yml```
            - Line # 13 ```compute: azureml:SOME_COMPUTE_CLUSTER``` and update it with your AML Compute Cluster's name
        - Run the job
            ```bash 
            az ml job create -f core/data_engineering/feature_engineering.yml 
            ```
        - Go to Azure ML Studio and locate the run detail
    - Run ```ml_training.py``` module under ```training``` folder
        - Review and update following parameters in the ```ml_training.yml```
            - Line # 13 ```compute: azureml:SOME_COMPUTE_CLUSTER``` and update it with your AML Compute Cluster's name
        - Run the job 
            ```bash 
            az ml job create -f core/training/ml_training.yml 
            ```
        - Go to Azure ML Studio and locate the run detail

    - Run ```ml_evaluating.py``` module under ```evaluating``` folder
        - Review and update the ```ml_evaluating.yml``` job file
            - Line # 18 ```compute: azureml:SOME_COMPUTE_CLUSTER``` and update it with your AML Compute Cluster's name
        - Run the job 
            ```bash 
            az ml job create -f core/evaluating/ml_evaluating.yml 
            ```
        - Go to Azure ML Studio and locate the run detail, observe the ML metrics and how the model was logged to Azure ML's model repo

- Create a pipeline that run feature_engineering, training and evaluation together
    - Review and update the ```training_pipeline.yml``` under ```pipelines``` 
            - Update  ```compute: azureml:SOME_COMPUTE_CLUSTER``` and update it with your AML Compute Cluster's name
    - Run the pipeline  
        ```bash 
        az ml job create -f core/pipelines/training_pipeline.yml 
        ```
    - Go to the run detail at Azure ML studio and observe the relationship graph among the modules.
- Discuss and answer this question: Why should run the modules both individually and together in a pipeline? 
- Deploy to Azure ML Managed Online Endpoint
    - Update the ```endpoint.yml``` file and ```deployment.yml``` by updating the name of the endpoint (should be a unique name)
    - Create your endpoint
        ```bash 
        az ml online-endpoint create --file core/scoring/endpoint.yml 
        ```
    - Create a green deployment 
        ```bash 
        az ml online-deployment create --file core/scoring/deployment.yml 
        ```
    - Test the deployed service with mock-up data from scoring_test_request.json
   
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
- Model is deployed successfully to managed endpoint. 
- Testing is successful


## Reference materials
- [Azure ML CLI v2 tutorial](https://docs.microsoft.com/en-us/learn/paths/train-models-azure-machine-learning-cli-v2/)
- [Azure ML CLI single job examples](https://github.com/Azure/azureml-examples/tree/main/cli/jobs/single-step)
- [Azure ML CLI pipeline examples](https://github.com/Azure/azureml-examples/tree/main/cli/jobs/pipelines)
- [Deploy to managed online endpoint](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-managed-online-endpoints)
- [Deploy to batch endpoint](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-batch-endpoint)

## [Go to Part 3](part_3.md)
