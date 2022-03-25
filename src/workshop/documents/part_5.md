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