# Pre-Workshop Checklist
> Note: Review the following criteria to ensure you can complete the workshop. These are critical pieces of access to get right for a successful workshop experience.

## Azure 
1. Do you have an Azure account?

2. Do you have a `Contributor` role for your Azure Subscription?
    - If you don't, do you have a `Contributor` role for the Azure Resource Group?
         > Note: If you don't, you can't run the workshop.

3. Do you have a Service Principal?
    - If you don't, do you know the Service Principal and it's information (client id, secret)?
    - If you don't, can you ask your Cloud team to create the Service Principal for limited scope of a resource group?
         > Note: If you don't, you can't run the workshop.

4. Do you know who can help you to handle issues?

5. Do you know a person from your Cloud infra/security team who can help you:
    - Create Azure resources
    - Grant permission

6. Did you register 'Microsoft.MachineLearningServices' for your Azure subscription?
> Note: If you're not sure, go to the Azure Portal > Subscriptions > 'YourSubscription' > Resource providers' > Search 'Microsoft.MachineLearningServices'

![ml_services](./images/arm100.png)

## Github
1. Do you have a Github account?
> Note: If not, create a new account and follow the instructions in Part 0 of the workshop.



### Github Self-Hosted Runner
1. If AML workspace is provisioned with Private Endpoints, Github Actions and workflows will be able to connect to the workspaces. 
2. You can deploy Self hosted runners in your own environment which can connect to AML workspace. 
3. To do this, please [see this](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners) for more details. 
4. If a self hosted runner is used, modify the files in the workflow folder as below:
        
        runs-on: [label, linux, X64]

# [Go to Part 0](./part_0.md)
