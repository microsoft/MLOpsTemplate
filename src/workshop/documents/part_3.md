
# Part 3: Use GitHub for Version Control and Automation


## Goal 
- Setup a centralized version control to keep track of project code and manage different feature development tracks and releases
- Understand how to automate and orchestrate common tasks such as environment setup, training, testing 

## Pre-requisites
- Complete parts 0, 1, and 2
- Familiarity with git

## Tasks
- Setup Github repo and prepare neccessary connections and credentials
    - [Add the credentials to Azure](https://docs.microsoft.com/en-us/azure/developer/github/connect-from-azure?tabs=azure-portal%2Cwindows#use-the-azure-login-action-with-a-service-principal-secret)
- Discuss about Branch strategy
- Learn about Github Action and Workflow
- Create your own development branch 
    - Run following command to create a new branch named "yourname-dev"
        ```bash
        git checkout -b yourname-dev
        ```
    - This will set the working branch to ```yourname-dev```. To check, run the following command:
         ```bash
        git branch
        ```
- Design an automated unit test task on a feature branch such as Feature_Engineering where upon pushing the code, an automated unit test is run to make sure the module performs correctly.
    - Locate the file named ```unit_test.yml``` in the ```.github/workflows```
    - In the file, create a trigger that will run the workflow when you push a change to the feature branch
        - See https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows for details on how to define such trigger
    - Next, create a job with the following steps:
         - Check out repo
         - Login into Azure
         - Create AML job to run feature engineering module using the [custom action](.github/actions/aml-job-create/action.yaml) and the existing [feature engineering job file](src/workshop/core/data_engineering/feature_engineering.yml)
- Commit changes to your feature branch and check to see if the new workflow was triggered
    - Run the following commands in sequence to stage changes, commit them, and then push them to your repo. Git status shows the files that have been modified. It is useful for seeing the latest status of the files.
    1. ```bash 
        git status
    2. ```bash 
        git add .
    3. ```bash
        git commit -am "a short summary of changes- insert summary"
    4. ```bash
        git push origin yourname-dev

## The CI CD Workflow is Shown Below:
![pipeline](images/part3cicd.png)

## Success criteria
- Understanding of integration vs main branch and when code is pushed to each branch
- Understanding of what workflows are and how they can be triggered
- Service Principal credentials are in Github

## Reference materials
- [Workflow syntax for Github Actions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions](https://github.com/features/actions)
- [GitHub Actions Workflow Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)

---

## [To Next Part 4](part_4.md)