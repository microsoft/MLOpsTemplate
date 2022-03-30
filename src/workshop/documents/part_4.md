# Part 4: Continuous integration (CI)

## Goal 
After learning about how GitHub can be leveraged for MLOps, your team decides to start by automatting the model training and evaluation process with a CI pipeline.

## Pre-requisites
- Complete parts 0, 1, 2 and 3

## Tasks

- Create CI Pipeline with the following components:
    - Trigger workflow when a Pull Request is merged to integration banch 
    - Run the AML pipeline
    - Create PR request to main if new code results in higher performing model
    - Locate the CI pipeline template named my_workshop_ci.yml under .guthub/workflows




Let's consider a common scenario in a ML development team. One of the team members is going to work on a new feature (examples can be changes to feature engineering, hyper-parameter selection, type of the model, etc). For this work, a common pattern is to first fork and clone the repository on your local machine (which you already have done in Step 0). 

Now you will create a new branch in order to start your work. Let's call it "yourname-dev".

- Run following command to creat a new branch
    ```bash
    git checkout -b yourname-dev
    ```

This creates a new branch and your current working branch is set to yourname-dev. If you wanted to make sure, you can run the following command:
    
```bash 
git branch
```
Hopefully "yourname-dev" branch is colored green with a * next to it.

In this step we want to make some changes to our ML code, locate and open the following file:

-  /src/workshop/core/training/ml_training.py

Let's make a quick change to line 44 of the code and update it to:

- model = RandomForestRegressor(n_estimators= 120)

The default for the model is set to 100 and we increased the number of estimators to 120- since we think this might improve our model's performance. Make sure to save the changes to the file. Now we want to commit these changes to the local branch and push them to our github repository.

- Run following commands in sequence to stage changes, commit them and then push them to your repo. Git status show the files that have been modfied. It's a useful command to know what's the latest status of the files.
    ```bash
    git status
    git add .
    git commit -am "a short summary of changes made- put your own comments here"
    git push origin yourname-dev
    ```
At this point you have made some changes to the code and have pushed the changes to the repository.

- Go to your browser and go to your repository. 
- Click on "pull requests" tab and you will see a message: yourname-dev had recent pushes X minutes ago.
- Click on "Compare and pull request", set the base: integration and compare: yourname-dev and click on Create pull request.
- Click on "Merge pull request"

This creates a pull request to the integration branch and merges it. As a reminder, integration branch is a branch which is as up to date as the main branch but we use it to test the new model. If the new model does not pass the evaluation, it will stop us from going to the CD process and making changes to the main branch where our production code lives.

The merge to the integration branch triggers the workshop_ci workflow. Click on the Actions tab on your repository and you will see ci workflow running after a few minutes. Click and examine all the steps, note that the CI Workflow is running following the steps in the workshop_ci.yml file which you located earlier.

The CI workflow has multiple steps, including setting up python version, installing libraries needed, logging in to Azure and running the training model pipeline and evaluating the model. As a part of this workflow, the updated model from our current changes is compared to our best previous model and if it performs better it passes the evaluation step (more details below).

You can check out different steps of the training pipeline under:

- /src/workshop/pipelines/training_pipeline.yml

At this point (it takes about 10 minutes for the pipeline to run), if all steps pass (you can check the status under the actions in the repository), a new pull request is made to the main branch. 

### Optional Reading
For the evaluation and comparison of the current model with our best previous model, we have included some code in the following script:

/src/workshop/core/evaluating/ml_evaluating.py

Note that on line 85 of the script we are comparing the R square of the current model with our best previous model in order to decide if we want to allow any changes to the model and main branch. You might want to edit this and relax it a little bit in order for the evaluation step to pass if you already have a really good model registered.






 


## Success criteria
- A workflow with the above components successfully runs when triggered

## Reference materials

- [GitHub Actions](https://github.com/features/actions)
- [GitHub Actions Workflow Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [Azure ML CLI v2](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-cli)
- [Azure ML CLI v2 Examples](https://github.com/Azure/azureml-examples/tree/main/cli)

---

## [To Next Part 5](part_5.md)

