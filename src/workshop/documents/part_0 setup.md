
# Part 1: Setup 

## Goal 

- Setup Azure ML workspace and components
- Setup github account and settings
- Setup local python development environment 
- Generate and register data for the workshop

## Pre-requisites
- Familarity with git command, branch concept 
- Knowlege of python programming, Pandas and Scikit-learn
- Conda

## Tasks
- Setup an AML workspace in your Azure subscription
    - Setup Azure ML CLI V2 az extension add -n ml -y (https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli)
    - Prepare an Azure Storage container
    - Register a datastore that points to the container
    - Create a compute cluster with DS11 or higher 
- Setup github account and settings
    - Setup your github account if you don't have one
    - Create a new repo 
    - Download the https://github.com/microsoft/MLOpsTemplate and push this new content to your repo
- Create local python development environment
    - Use VSCode for python if possible
    - Using conda, create a new virtual environment or use an existing virtual environment with azureml-sdk, pandas, sckit-learn
    - Create a local project folder in your local computer
    - cd to MLOpsTemplate\src\workshop
- Generate and register data for the workshop
    - run ```python data/create_datasets.py --datastore_name YOUR_DATA_STORE_NAME```. You can also change default datastore_name inside the create_dataset.py script 



## Reference materials


