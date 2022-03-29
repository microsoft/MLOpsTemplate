# Part 4: Continuous integration (CI)

## Goal 
After learning about how GitHub can be leveraged for MLOps, your team decides to start by automatting the model training process with a CI pipeline.

## Pre-requisites
- Complete parts 0, 1, 2 and 3

## Tasks
- Locate the CI pipeline template named my_workshop_ci.yml under .github/workflows
- Setup CI Pipeline with the following components:
    - Trigger workflow when PR to integration branch is created
        - See https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows for details on how to define such trigger
    - Next, create a job with the following steps:
        - Check out repo
        - Login into Azure
        - Create AML job to run the training pipline using the [custom action](.github/actions/aml-job-create/action.yaml) and the existing [training pipeline](src/workshop/core/pipelines/training_pipeline.yml)

## Success criteria
- A workflow with the above components successfully runs when triggered

## Reference materials
- [Workflow syntax for Github Actions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions](https://github.com/features/actions)
- [GitHub Actions Workflow Triggers](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [Azure ML CLI v2](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-cli)
- [Azure ML CLI v2 Examples](https://github.com/Azure/azureml-examples/tree/main/cli)
