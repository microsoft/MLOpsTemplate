# Part 4: Continuous integration (CI)

## Goal 
After learning about how GitHub can be leveraged for MLOps, your team decides to start by automatting the model training and evaluation process with a CI pipeline.

## Pre-requisites
- Complete parts 0, 1, 2 and 3

## Tasks
- Create CI Pipeline with the following components:
    - Trigger workflow when PR to integration branch is created
    - Run the AML pipeline
    - Create PR request to main if new code results in higher performing model
    - Locate the CI pipeline template named my_workshop_ci.yml under .guthub/workflows




Let's consider a common scenario in a ML development team. One of the team members is going to work on a new feature (examples can be changes to feature engineering, hyper-parameter selection, type of the model, etc). For this work, a common pattern is to first fork and clone the repository on your local machine (which you already have done in Step 0). 

Now you will create a new branch in order to start your work. Let's call it "yourname_dev".

- Run following command to creat a new branch
    ```bash
    git checkout -b yourname_dev
    ```

This creates a new branch and your current working branch is set to yourname_dev. If you wanted to make sure, you can run the following command:
    
```bash 
git branch
```
Hopefully "yourname_dev" branch should be colored green with a * next to it.

In this step we want to make some changes to our ML code, locate and open the following file:

- .. /src/workshop/core/training/ml_training.py

Let's make a quick change to line 44 of the code and update it to:

- model = RandomForestRegressor(n_estimators= 120)

The default for the model is set to 100 and we increased the number of estimators to 120- since we think this might improve our model's performance. Make sure to save the changes to the file. Now we want to commit these changes to our local branch and push them to our github repository.

- Run following commands in sequence to stage changes, commit them and then push them to your repo. Git status show the files that have been modfied. It's a useful command to know what's the latest status of the files.
    ```bash
    git status
    git add .
    git commit -am "a short summary of changes made- put your own comments here"
    git push origin yourname_dev
    ```
At this point you have made some changes to the code and have pushed the changes to the repository.  







    

## Success criteria
- A workflow with the above components successfully runs when triggered

## Reference materials
- [GitHub Actions](https://github.com/features/actions)
- [GitHub Actions Workflow Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [Azure ML CLI v2](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-cli)
- [Azure ML CLI v2 Examples](https://github.com/Azure/azureml-examples/tree/main/cli)

---

## [To Next Part 5](part_5.md)




# Part 5: Continuous deployment (CD)

## Goal 
After a successful run of the CI pipeline, your team is looking to complete the process with a CD pipeline that will handle the deployment of the model without introducing any downtime in production (hot swap).

## Pre-requisites
- Complete parts 0, 1, 2, 3 and 4

## Tasks

- Located the CD pipeline template named my_workshop_cd.yml under .guthub/workflows

### High Level Goals

- The goal of this section is to get a fully functional CD pipeline that will:
    
    1. Trigger based on creation of a Pull Request (PR) to main
    2. Create a model API endpoint (webservice) using an Azure ML Managed Endpoint and deploy the model to the endpoint into one of the 2 deployment slots (blue/green slots, which will switch staging/production roles)
    3. Test the deployment to the endpoint of the new model
    4. On success of test, swap the deployment to accept 100% of the service endpoint traffic (and therefore become 'production')
       

### Implementation Details and Instructions

1. Setup your CD pipeline yaml file to trigger on Pull Request to main:
    - See https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows for details on how to define such trigger.
    - Please also setup a trigger that will enable to run the CD pipeline on demand from the GitHub UI as this will greatly facilitate testing. See 'workflow_dispatch'.

2. Use the .github/actions/aml-endpoint-deploy provided custom action in your CD yaml pipeline.
    - Configure the custom action parameters to match your Azure environment.
    - Have a look at the code inside the custom action (action.yaml) to see how simple it is to build custom actions leveraging any scripting packages, libraries, and the Azure CLI (az) which gives you full access to anything available in AML. Please notice the section of codes relevant to: a) creating then endpoint if it doesn't exist, b) reading the endpoint details to check its traffic, and identify which deployment slot to target to stage the new model, c) deployment of the model.

    Test your CD pipeline by checking your code into your own development branch, and going to the GitHub UI under 'Actions', and select 'my_workshhop_CD', and trigger it on your own branch.

    Troubleshoot and debug until the first step of the CD pipeline (deployment) is functional.

3. Use the .github/actions/aml-endpoint-test provided custom action in your CD yaml pipeline.
    - Configure the custom action parameters to match your Azure environment.
    - Have a look at the custom action, and feel free to modify the test code to your liking. One could consider building a python test script instead of using the az ml command to test the endpoint more thoroughly. Please note that the az ml commands would enable you to retrieve any required metadata about the endpoint for further testing (for instance its URI) and that you can customize targetting a specific deployment of the endpoint URI (via a header hint named 'azureml-model-deployment'). See https://docs.microsoft.com/en-us/azure/machine-learning/how-to-safely-rollout-managed-endpoints#test-the-new-deployment 

    Test your CD pipeline by checking your code into your own development branch, and going to the GitHub UI under 'Actions', and select 'my_workshhop_CD', and trigger it on your own branch.

    Troubleshoot and debug until the first two steps of the CD pipeline (deployment + test) are functional.

4. Use the .github/actions/aml-endpoint-swap provided custom action in your CD yaml pipeline.
    - Configure the custom action parameters to match your Azure environment.
    - Review the custom action code to see how the custom action reads the endpoint metadata, to identify which endpoint is currently live (100% traffic), to proceed with the proper traffic re-assignments of the deployments of this endpoint.

    Test your CD pipeline by checking your code into your own development branch, and going to the GitHub UI under 'Actions', and select 'my_workshhop_CD', and trigger it on your own branch.

    Troubleshoot and debug until all 3 steps of this CD pipeline are green. Validate that each time you run the CD pipeline, the deployment goes to the 0% endpoint, tests it, and then switches the traffic around.

## Success criteria

- The CD pipeline runs sucessfully each time a PR request is done to 'main'. Please test this by triggering a new CI run (which on success should generate a PR to main), or creating your own PR to main.

## Reference materials

- [GitHub Actions](https://github.com/features/actions)
- [GitHub Actions Workflow Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [Azure ML CLI v2](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-cli)
- [Azure ML CLI v2 Examples](https://github.com/Azure/azureml-examples/tree/main/cli)
- [Azure ML Managed Endpoints](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-managed-online-endpoints)
- [Azure ML Safe Rollout of Managed Endpoints](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-safely-rollout-managed-endpoints)




