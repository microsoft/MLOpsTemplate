
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

To create resources you need subsciption Owner role or subsciption Contributor role. If you don't have one of role you can't run the script. So make sure you have proper role.

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

- Login to [Github](https://github.com/)

> If you don't have an account for Github, sign up
>
> The workshop can't be done without the Github account

- Go to [https://github.com/microsoft/MLOpsTemplate](https://github.com/microsoft/MLOpsTemplate) and click __fork__

    ![](./images/run_mlopsworkshop_azcli009.png)

- You will have the same repo in you github account Repository


### 3. Choose your development environment


In this step you will clone your repo into your local development environment. The local can be Compute Instance in AML or your laptop. There are two options to setup local development environment. Choose an option.

    - Option A. CI in AML
    - Option B. Your laptop(PC/MAC)

#### Option A. Using Compute Instance in AML
- Go to your Compute Instance in your Azure Machine Learning Workspace
- Open new Terminal
- Clone your 'MLOpsTemplate' repo from the Terminal of Compute Instance
    - Before you run following command, upate {YOURGITHUBACCOUNT} part
    - Sample command
    ```bash
    git clone https://github.com/{YOURGITHUBACCOUNT}/MLOpsTemplate.git
    ```

    > Note: Make sure you're running the command from the path like following. This is path in your Compute Instance
    > `~/cloudfiles/code/Users/YOURALIAS$`

    ![](./images/run_mlopsworkshop_azcli004.png)

- Generate and register data for the workshop
    - Update arguments __"value"__ accordingly and then run following commands from the Terminal

        ```bash
        cd ./MLOpsTemplate/src/workshop
        conda env create -f conda-local.yml
        conda activate mlops-workshop-local
        python ./data/create_datasets.py --datastore_name workspaceblobstore --ml_workspace_name "AML_WS_NAME" --sub_id "SUBSCRIPTION_ID" --resourcegroup_name "RG_NAME"
        ```
        
    > Note: You can find the __Resource Group Name, Azure Machine Learning Name__ and __the Location__ from Azure portal.
    >
    > ![](./images/run_mlopsworkshop_azcli010.png)

- Install az ml CLI v2
    - Continue to run following commands from the Terminal

        ```bash 
        az extension remove -n azure-cli-ml
        az extension add -n ml -y
        ```

- Setup az cli
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
    az account set -s "<YOUR_SUBSCRIPTION_NAME>"
    az configure --defaults group="<YOUR_RG_NAME>" workspace="<YOUR_AML_NAME>" location="<YOUR_REGION_NAME>"
    az configure -l -o table
    ```
    
    > Note: You can find the __Resource Group Name, Azure Machine Learning Name__ and __the Location__ from the user profile in the AML Studio.
    >
    > ![](./images/run_mlopsworkshop_azcli008.png)

    The results will look like following
    ![](./images/run_mlopsworkshop_azcli007.png)


#### Option B. Use your laptop (PC/MAC)
- Create local python development environment
    - Install python, Conda, git and your prefered IDE
        - Use VSCode and VSCode for python if possible

- Clone your 'MLOpsTemplate' repo from the Terminal of Compute Instance
    - Before you run following command, upate {YOURGITHUBACCOUNT} part
    - Sample command
    ```bash
    git clone https://github.com/{YOURGITHUBACCOUNT}/MLOpsTemplate.git
    ```

    - Using conda, create a new virtual environment or use an existing virtual environment with azureml-sdk, pandas, sckit-learn
        - If you don't have conda virtual environment, use following command to create new
            ```bash
            cd ./MLOpsTemplate/src/workshop
            conda env create -f conda-local.yml
            ```

- Generate and register data for the workshop
    - Update __arguments__ and then run following commands from the terminal

        ```bash
        conda activate mlops-workshop-local
        python ./data/create_datasets.py --datastore_name workspaceblobstore --ml_workspace_name "AML_WS_NAME" --sub_id "SUBSCRIPTION_ID" --resourcegroup_name "RG_NAME"
        ```

- [Install az CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli#install)

- Install az ml CLI v2
    - Continue to run following commands from the Terminal

        ```bash 
        az extension remove -n azure-cli-ml
        az extension add -n ml -y
        ```

- Setup az cli
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
    az account set -s "<YOUR_SUBSCRIPTION_NAME>"
    az configure --defaults group="<YOUR_RG_NAME>" workspace="<YOUR_AML_NAME>" location="<YOUR_REGION_NAME>"
    az configure -l -o table
    ```
    
    > Note: You can find the __Resource Group Name, Azure Machine Learning Name__ and __the Location__ from the user profile in the AML Studio.
    >
    > ![](./images/run_mlopsworkshop_azcli008.png)

    The results will look like following
    ![](./images/run_mlopsworkshop_azcli007.png)


---

## [To Next Part 1](part_1.md)
