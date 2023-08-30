# Part 5: Continuous Delivery (CD)

## Pre-requisites
- Complete [Part 0](part_0.md), [Part 1](part_1.md), [Part 2](part_2.md), [Part 3](part_3.md) and [Part 4](part_4.md)

## Summary 

After a successful run of the CI (continuous integration) pipeline, your team is looking to complete the process with a CD (continuous delivery, or continuous deployment) pipeline that will handle the deployment of the new, better-performing model while maintaining continuous delivery of the model to processes that depend on the model's availability, without introducing any downtime in production, also known as a "hot swap".

The goal of this section is to get a fully functional CD pipeline running that will:
    
1. Authenticates using a Service Principal to be able to leverage the Azure Databricks commands in your workflow.
2. Be automatically triggered based on a Pull Request (PR) that is approved to merge the new code that passes the integration tests in the `integration` branch into the `main` branch of the repo.
3. If the model performance metrics show improvement over the current production model on production data, then promote the new model to production and archive the old model. 

## Steps

1. As you have done since Part 3, you define triggers as part of a Azure Pipelines workflow. The CD workflow is triggered when a pull request is created and the new code in `integration` is merged into the `main` branch. The PR to `main` is opened  if the new code results in a model that outperforms the prior model on test data. The triggers for this workshop have already been defined in `.azure_pipelines/workflows/cd.yml`. 

The key elements of the trigger section are as follows:

```
# .azure_pipelines/workflows/cd.yml

trigger:
  branches:
    exclude:
      - integration
    include:
      - main
  paths:
    include:
      - src/workshop/notebooks/part_1_1_data_prep.ipynb
      - src/workshop/notebooks/part_1_2_training.ipynb
      - src/workshop/notebooks/part_1_3_evaluating.ipynb
      - .azure_pipelines/cd.yml

```

2. The CD workflow relies on the Azure CLI to control the infrastructure and implement the automation of the model deployments. Therefore, we need to setup this workflow to login to Azure via a Service Principal to be able to leverage the Azure CLI.

    > Action Items:
    > 1. Open up the `cd.yml` file in your Azure repo under `.azure_pipelines/`.
    > 2. Update the 'creds: ${{ secrets...' section in this file to setup your secret name. Follow the instructions in this file annotated with #setup.

    > Note: Please refer to [Use the Azure login action with a service principal secret](https://docs.microsoft.com/en-us/azure/developer/github/connect-from-azure?tabs=azure-portal%2Cwindows#use-the-azure-login-action-with-a-service-principal-secret) to create the proper Azure Credentials if you haven't done so already (you should have already defined such secret to complete the CI part of the workshop, i.e. [Part 4](part_4.md)).

3. In our scenario, a model is deployed to production when it occupies the "Production" model slot in the model registry. Our CD pipeline needs to ensure that the current best model is always available in the "Production" slot. The Azure Pipeline we specify for CD automates these deployments.

Now let's configure the Azure Pipelines configuration file that controls the CD process located at `.azure_pipelines/cd.yml`

> Action Item:
>- Edit `cd.yml` to setup your Azure resource group name and Azure ML workspace name which are being passed as parameters to a set of custom GitHub Actions. Look for #setup and follow the instructions in the file.

> Action Items:
> 1. Commit your configuration changes and push them up to the Azure Repo in your own development branch. 
> 2. Go to the Azure Pipelines UI, select the pipeline you configured in 'cd.yml', and trigger it to run now on your own branch.
> 3. Once triggered, click on it to open up the details and monitor its execution.


4. (optional) Test the new deployment using `/notebooks/part_1_4_scoring`.

## Success criteria

- The CD pipeline runs sucessfully each time a PR request to 'main' is merged. Please test this by creating your own PR to main.
- Check that the better new model is deployed to the Production slot in your model registry, the Models section of Azure Databricks.


## Congratulations!
This completes this workshop. You have gained hands-on experience with many of the key concepts involved in MLOps using Azure Databricks and Azure DevOps. 