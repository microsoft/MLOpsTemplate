
# Part 0: Workshop Environment Setup 

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

    1. Create resources in Azure

    2. Setup github account and settings

    3. Choose and setup your development environment

        Option A using CI in AML
        Option B using your local machine (PC or MAC)

### 1. Create resources in Azure

To create resources you need Owner role or Contributor role. If you don't have one of role you can't run the script. So make sure you have proper role.

- Go to [Azure Portal](https://portal.azure.com) and open __Cloud Shell__
    
    ![cloudshell](./images/cloudshell.png)

- Change directory to `$HOME/clouddrive'
    > Note: This is cloudshell path.

    ```bash
    cd $HOME/clouddrive
    ```

- Run following command to clone repo
    ```bash
    git clone https://github.com/microsoft/MLOpsTemplate.git
    ```
- Change directory to `$HOME/clouddrive/MLOpsTemplate/src/workshop/documents/IaC/`
- Run `iac_mlopsworkshop.azcli`

    1. Read message carefully and hit `Enter` key to move next step.
        ![](./images/run_mlopsworkshop_azcli000.png)

    1. Type your Subscription Name. Note that it's __CaSE SeNSiTivE__.
        ![](./images/run_mlopsworkshop_azcli001.png)

    1. Type region where you want to create the resources. Default region is `westus2`.
        ![](./images/run_mlopsworkshop_azcli002.png)
    
    1. The script will run 5 to 7 mintues.
        > Note that this script will create SP (Service Principal) under scope of your resource group.
        >
        > Save the Service Principal `ClientID(AppId)`, `Password` in a safe place
        >
        > In case you lost, the information also saved in the path where you ran the script.

        ![](./images/run_mlopsworkshop_azcli003.png)

> IMPORTANT: If this script failed, you can't do following labs.
>
> Please contact your CSA or lab instructor with the error message.

### 2. Setup github account and settings

- Setup your github account if you don't have one
- Create a new repo
- Push the downloaded repo (https://github.com/microsoft/MLOpsTemplate) to the your new repo

### 3. Choose your development environment

    There are two topion to setup local development environment. 
    Choose an option - A or B. 

#### Option A. Use Compute Instance for code development
- Go to your Compute Instance in your Azure Machine Learning Workspace

- Clone this git repo from the Terminal of Compute Instance
    > Note: Make sure you're running the command from the path like following. This is path in your Compute Instance
    >> `~/cloudfiles/code/User/{YOURALIAS}$`

    ![](./images/run_mlopsworkshop_azcli004.png)

- Generate and register data for the workshop
    - Update arguments {value} and then run following commands

        ```bash
        cd ./MLOpsTemplate/src/workshop
        conda activate azureml_py38
        pip install --upgrade pandas
        python ./data/create_datasets.py --datastore_name workspaceblobstore --ml_workspace_name {amlwrkshp-000} --sub_id {SUBSCRIPTIONID} --resourcegroup_name {amlwrkshp-000-rg}
        ```

- Install az ml CLI v2
    - Continue to run following commands from the Terminal

        ```bash 
        az extension remove -n azure-cli-ml
        az extension add -n ml -y
        ```

- Setup az cli
    > Note: Az ml CLI v2 is for local ML code testing.
    - Run follwoing command from the Termianl

        ```bash
        az login
        ```

    - You need to loging to be authenticated to use az cli
        ![](./images/run_mlopsworkshop_azcli006.png)
        After copy the __code__ and go to the link, [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin). 
        
        Use the code and follow the instruction to finish the login.

- Configure subscription and Azure Machine Learning Workspace

    ```bash
    az account set -s "<YOUR_SUBSCRIPTION_NAME_OR_ID>"
    az configure --defaults group="<YOUR_RG_NAME>" workspace="<YOUR_AML_NAME>" location="<YOUR_REGION_NAME>"
    az configure -l -o table
    ```
    
    > Note: You can find the __Resource Group Name, Azure Machine Learning Name__ and __the Location__ from the user profile in the AML Studio.
    >
    > ![](./images/run_mlopsworkshop_azcli008.png)

    The results will look like following
    ![](./images/run_mlopsworkshop_azcli007.png)


#### Option B. Use your local/on-premises for code development
- Create local python development environment
    - Use VSCode for python if possible
    - Using conda, create a new virtual environment or use an existing virtual environment with azureml-sdk, pandas, sckit-learn
    - Create a local project folder in your local computer
    - cd to MLOpsTemplate\src\workshop
- Generate and register data for the workshop
    - run ```python data/create_datasets.py --datastore_name YOUR_DATA_STORE_NAME```. You can also change default datastore_name inside the create_dataset.py script

- [Install az CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli#install)

- Install az ml CLI v2
    - Continue to run following commands from the Terminal

        ```bash 
        az extension remove -n azure-cli-ml
        az extension add -n ml -y
        ```

- Setup az cli
    > Note: Az ml CLI v2 is for local ML code testing.
    - Run follwoing command from the Termianl

        ```bash
        az login
        ```

    - You need to loging to be authenticated to use az cli
        ![](./images/run_mlopsworkshop_azcli006.png)
        After copy the __code__ and go to the link, [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin). 
        
        Use the code and follow the instruction to finish the login.

- Configure subscription and Azure Machine Learning Workspace

    ```bash
    az account set -s "<YOUR_SUBSCRIPTION_NAME_OR_ID>"
    az configure --defaults group="<YOUR_RG_NAME>" workspace="<YOUR_AML_NAME>" location="<YOUR_REGION_NAME>"
    az configure -l -o table
    ```
    
    > Note: You can find the __Resource Group Name, Azure Machine Learning Name__ and __the Location__ from the user profile in the AML Studio.
    >
    > ![](./images/run_mlopsworkshop_azcli008.png)

    The results will look like following
    ![](./images/run_mlopsworkshop_azcli007.png)


## Reference materials

---

## [To Next Part 1](part_1.md)
