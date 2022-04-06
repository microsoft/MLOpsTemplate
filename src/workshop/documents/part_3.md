
# Part 3: Use GitHub for Version Control and Automation

## Pre-requisites
- Complete parts 0, 1, and 2
- Familiarity with git

## Goal 
- Setup a centralized version control to keep track of project code and manage different feature development tracks and releases
- Understand how to automate and orchestrate common tasks such as environment setup, training, testing 

## Summary

## Steps
1. Create your own development branch where you can make and track changes. This branch will be your development area to create and test new code or pipelines before committing or merging the code into a common branch, such as ```integration```.

How: 
- Navigate to the repo if not already there by running ```cd PATH_TO_REPO``` with the proper path to the cloned location.
- Run following command to create a new branch named "yourname-dev"
    ```bash
    git checkout -b yourname-dev
    ```
- This will set the working branch to ```yourname-dev```. To check, run the following command:
        ```bash
    git branch
    ```
```json
    TODO: Create your own branch
```

2. Create an automated unit test task such that will be triggered by pushing the code the code to your development/feature branch. Let's use the ```Feature_Engineering``` module as the automated unit test to run to make sure the module performs correctly. 

How:
- Locate the file named ```unit_test.yml``` in the ```.github/workflows``` folder
- Make the following updates to the file:
    - Finish the trigger that will run the workflow when you push a change to your feature branch by replacing #SETUP on line 6 with your branch name
        - See https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows to learn more on how to create triggers
    - Update the secret name on line 26 by replacing the ```MY_AZURE_CREDENTIALS``` to match the GitHub secret name for your Service Principal that was created during step 0. It most likely has a name similar to ```AZURE_CREDENTIALS_USERNAME```. Your line will look something like this:
    ```yaml
    creds: ${{ secrets.MY_AZURE_CREDENTIALS }}
    ```
    - Update line 30 by replacing GROUP, WORKSPACE, and LOCATION with the properties (resource group name, workspace name, and location) of your Azure Machine Learning Workspace created in step 0.
3. Next, review the job that has been created already that does the following steps:
    - Check out repo
    - Login into Azure
    - Create AML job to run feature engineering module using the [custom action](../../../.github/actions/aml-job-create/action.yaml) and the existing [feature engineering job file](../core/data_engineering/my_feature_engineering.yml)
    > Note: Make sure you follow the next step to edit the ```my_feature_engineering.yml``` file to your datastore name and compute cluster or else the workflow will fail.
4. Make changes to feature_engineering job file to ensure job will run successful
Locate the file named ```my_feature_engineering.yml``` in the ```.github/src/workshop/data_engineering``` folder
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
- Service Principal is created and credentials are in Github
- Understanding of branch strategy with feature branch, integration branch and main branch
- Understanding of what workflows are and how they can be triggered
- Successfully run one workflow from feature branch 

## Reference materials
- [GitHub Actions](https://github.com/features/actions)
- [GitHub Actions Workflow Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)

---

## [To Next Part 4](part_4.md)
