# Part 4: Continuous Integration (CI)

## Pre-requisites
- Complete [Part 0](part_0.md), [Part 1](part_1.md), [Part 2](part_2.md), [Part 3](part_3.md)

## Summary
After learning about how GitHub can be leveraged for MLOps, your team decides to start by automating the model training and evaluation process with a CI pipeline. Continuous Integration (CI) is the process of developing, testing, integrating, and evaluating new features in a staging environment where they are ready for deployment and release. 

## Steps:

1. Locate the CI pipeline template under ```.github/workflows/workshop_ci.yml``` and add all the needed information for resource group name, workspace name, location and secrets for Azure and Github. They are all tagged with ```#setup```. 

    > Action Item: Update resource group name, workspace name, location, Azure Secret and Github Secret inside workshop_ci.yml file.

2. Now Let's consider a common scenario in a ML development team. One of the team members is going to work on a new feature (examples can be changes to feature engineering, hyper-parameter selection, type of the model, etc). For this work, a common pattern is to first fork and clone the repository on your local machine (which you already have done in Step 0).  Then you need to switch to the ```yourname-dev``` local branch which you created in step 3.

    > Action Item: Run the following command to switch to ```yourname-dev``` branch
    ```bash
    git checkout yourname-dev
    ```
    This takes you to yourname-dev branch, so your current working branch is set to yourname-dev. 

    > Action Item: Run the following command to ensure you are in the correct branch.  
    ```bash
    git branch
    ```
    > Note: Hopefully "yourname-dev" branch is colored green with a * next to it.

3. In this step we want to make some changes to our ML code, locate and open the following file: ```/src/workshop/core/training/ml_training.py```

    >Action Item: Update `ml_training.py`, you can search for #setup and modify `alpha` to: `model = Ridge(alpha=100)`

    The default for the model is set to 100,000. By updating alpha we think it will improve the model performance, let's find out! Make sure to save the changes to the file. Now we want to commit these changes to the local branch and push them to our github repository. This will update the remote github branch on the repository.

4. Run following commands in sequence (one by one) to stage changes, commit them and then push them to your repo. Git status show the files that have been modified. It's a useful command to know what's the latest status of the files.

    >Action Items: Run the following commands sequentially:
    ```bash
    git status
    ```
    ```bash
    git add .
    ```
    ```bash
    git commit -am "a short summary of changes made- put your own comments here"
    ```
    ```bash
    git push origin yourname-dev
    ```
5. At this point you have made some changes to your code and have pushed the changes to your brnach on the repository. In order for us to make these changes permanent and take it eventually to deployment and production, we need to place these changes in the "integration" branch.

    >Action Items:
    >- Go to your browser and go to your repository. 
    >- Click on "pull requests" tab and Click on "New pull request". 
    >
    >- Set the `base` branch to `integration` and the `compare` branch to `yourname-dev`.
    >- Make sure the integration branch you choose as the base is pointing to your forked repository and **NOT** the Microsoft MLOpsTemplate repository.
    >- Click on "Create pull request".
    >- Click on "Merge pull request".

    This creates a pull request to the integration branch and merges it. As a reminder, integration branch is a branch which is as up to date as the main branch but we use it to evaluate the new feature. Here we made some changes to the model, and we want to make sure the new model passes the evaluation. If not,it will stop us from going to the CD process and making changes to the main branch where our production code lives.

6. The merge to the integration branch triggers the workshop_ci workflow. Click on the Actions tab on your repository and you will see CI workflow running after a few minutes. Click and examine all the steps, note that the CI Workflow is running following the steps in the ```workshop_ci.yml``` file which you located earlier. Note that in the first few lines of this file we have defined the workflow to be triggered when a pull request is merged in the "integration" branch.

    The CI workflow has multiple steps, including setting up python version, installing libraries needed, logging in to Azure and running the training model pipeline and evaluating the model. As a part of this workflow, the updated model from our current changes is compared to our best previous model and if it performs better it passes the evaluation step (more details below).

    You can check out different steps of the training pipeline under: ```/src/workshop/pipelines/training_pipeline.yml```. 
    
    >Note: At this point, it takes about 10 minutes for the pipeline to run.
    
    If all steps pass (you can check the status under the actions in the repository), a new pull request is made to the main branch. If the workflow fails, there could be a few different reasons, you can open the workflow steps on the actions tab of the repository and examine it. Most likely if it fails in this case is due to the evaluation part, where our new model performs worse than our best previous model and doesn't pass the evaluation step and the whole workflow fails. To resolve that continue reading the following section.

> OPTIONAL READING: For the evaluation and comparison of the current model with our best previous model, we have included some code in the following script: ```/src/workshop/core/evaluating/ml_evaluating.py```. Note that on line 85 of the script we are comparing the R-square of the current model with our best previous model in order to decide if we want to allow any changes to the model and main branch. You might want to edit this and relax it a little bit in order for the evaluation step to pass if you already have a really good model registered. Note that you can change the evaluation metrics based on your actual use case in the future.

## Success criteria
- Trigger CI workflow when a pull request is merged to the integration branch
- Successfully run the CI workflow which also includes the AML pipeline
- Create a Pull Request to the main branch if new code results in higher performing model

## Reference materials

- [GitHub Actions](https://github.com/features/actions)
- [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-token)
- [GitHub Actions Workflow Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [Azure ML CLI v2](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-cli)
- [Azure ML CLI v2 Examples](https://github.com/Azure/azureml-examples/tree/main/cli)


## [Go to Part 5](part_5.md)

