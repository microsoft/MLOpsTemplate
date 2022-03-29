
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
- Design an automated unit test task on a feature branch such as Feature_Engineering where upon pushing the code, an automated unit test is run to make sure the module performs correctly.

## The CI CD Workflow is Shown Below:
- ![pipeline](images/part3cicd.png)

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