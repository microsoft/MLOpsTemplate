# Check list

## Azure 
1. Do you have Azure account?

2. Do you have Contoributor role for your Azure Subscription?
        - If you don't, do you have contributor role for Azure Resource Group?
        - If you don't, you can't run the workshop.

3. Do you have a Service Principal (SP)?
        - If you don't, do you know the SP and it's information (client id, secret)?
        - If you don't, can you ask your Cloud team to create the SP for limited scope of a resource group? (If not, you cannot run the workshop.)

4. Do you know who can help you to handle issues?

5. Do you know a person from Cloud infra/security team who can help you:
        - Create Azure resources
        - Grant permission 

6. Did you register 'Microsoft.MachineLearningServices' for your Azure subscription?
> Note: If you're not sure, go to the Azure Portal > Subsciprtions > 'YourSubscription' > Resource providers' > Search 'Microsoft.MachineLearningServices'

![ml_services](./images/arm100.png)

## Github
1. Do you have github account?
> Note: If not, create a new account and follow part 0 instruction for the workshop

# [Go back to Part 0](./part_0.md)
