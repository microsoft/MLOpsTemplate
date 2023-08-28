
# Part 2:  Preparing notebooks for remote triggering

## Pre-requisites
- Complete [Part 0](part_0.md), [Part 1](part_1.md)
- In your Databricks Repo, have a personal dev branch that you created off of the `integration` branch, named `dev-{yourname}` or similar (for example, `dev-nick`). 
- Run each notebook successfully via the Databricks notebook UI -- data prep, training, and evaluating.
- Confirm that you have a Model labeled "Production" in the Models section of Databricks.

## Summary 
After successfully restructuring the end-to-end Databricks notebook into task-focused, modular notebooks, and running those notebooks via the Databricks UI, your team wants to prepare to run the notebooks automatically in response to code changes.

To do this, we need to move away from untracked, user-driven notebooks to version-controlled notebooks that can be run not by a person but by a Service Principal, which is a type of application with narrowly constrained rights and responsibilities. Your MLOps platform administrator should already have created a Service Principal, granted it the appropriate permissions to interact with your Databricks service, and given you permissions to use the Service Principal to run notebooks and workflows in Databricks.

To introduce these concepts you will next do the following:
- Preview how to run the data prep notebook via REST API 
- Preview how to use the Service Principal to run the notebook 
- Review the configuration of an Azure Pipeline in Azure DevOps to run a "unit test" notebook using the Service Principal
- Manually trigger the Azure Pipeline from Azure DevOps


## Steps
1. Many actions you take in Databricks, including running a notebook, can be triggered programmatically via API. Let's unpack an example call to the API to run a notebook:
![Sample Databricks API to run job](images/part_2_run_job.png)

In the first line we see `curl -X POST`, which means we're using a command-line utility, curl, to issue a request to a URL address.
At the bottom we see where the request is sent, to `$(databricks_workspace_uri)/api/2.1/jobs/run-now`. The `$(databricks_workspace_uri)` part is a variable referring to the URI of your Databricks instance, which corresponds to what you can find in the address bar of your browser and is of the form "https://{some string}.azuredatabricks.net/". 

Many variables used in this pipeline were specified in Part 0 during the platform setup, and they are in the Azure DevOps library as a variable group. Those can include secured secrets, including those in a linked Azure Key Vault.


After that is the `/api/2.1/jobs/run-now`, which is how we express the command to run the notebook.

2. Next, in order to run a notebook in Databricks you need to have the right permissions. This is what the `Authorization: Bearer '"$(token)"'` is about. Unless we pass the right token along with the API request, the request will be rejected and no action will be taken. From the `$(token)` notation, we see that the token is a variable. How do we get that token? Prior to making the Databricks API request, we're going to request the token for the Service Principal from the Azure AD API.

![Azure AD Login API](images/part_2_aad_login.png)

With this REST call, we are asking Azure AD for an OAuth token for the Service Principal, referred to by its `client_id`. We are passing the `client_secret`, as a variable, for the Service Principal along with the request, and if the request is authorized, we'll get back a JSON message that will include the `access_token` as one of the elements of the JSON, which we use `jq` to parse and extract to the variable `token`. That `token` is what is referenced by `$(token)` in the call to the Databricks API. For security purposes, this token only lives for an hour, so each time we call the API, we'll first have the Service Principal authenticate.

3. So we now know that running the notebook via the Databricks API requires first authenticating and getting a token that reflects the right permissions. We'd like these two steps to run on a secure machine in a pipeline that can be automated in response to certain events like code changes that have been saved and committed to our repo. Azure Pipelines is a platform enabling just such functionality. 

Here is an example Azure Pipeline definition:

![Azure Pipeline to run Databricks Notebook](images/part_2_azpipe_run_nb.png)

In the `steps` section we can see the authentication request (1) followed by the Databricks API request to run a notebook (2).

These `curl` requests have to be run somewhere, and in the `pool` section we see that Azure Pipelines will run them on a virtual machine running the latest Linux ubuntu OS.

At the top of the pipeline configuration there is a `trigger` section, which is where we'll specify the conditions under which the steps should be executed. We'll configure the trigger section in Part 3 of the workshop.

4. For now let's manually trigger the Azure Pipeline to confirm it does what we expect. In your browser, navigate to your Azure DevOps project at https://dev.azure.com and go to the Pipelines section of the sidebar.

You should see a pipeline named "Data Prep Unit Test Pipeline." Click on the pipeline name to see a list of prior runs of the pipeline, along with a blue button to "Run pipeline". Use the blue "Run pipeline" button to manually trigger the pipeline.

Be sure to run the pipeline on your dev branch of the repo:

![Azure Pipeline Job](images/part_2_ado_manual_trigger.png)

5. Let's review what happens next. Click on the "Job" link to open up the Azure Pipeline job you just saved and ran.
![Azure Pipeline Job](images/part_2_pipe_job.png)

You'll see a long list of steps that have run on the Linux VM in Azure pipelines. All steps in the Azure Pipeline should show a green checkmark as having successfully completed. Many of the steps are utility steps, but they also include the two steps we explicitly defined in the pipeline YAML, namely the authorization step, labeled "Get Entra ID token" -- Entra is the new brand name for Azure AD --, and the run notebook step, labeled "Run Databricks notebook via API". Click on "Run Databricks notebook via API".
![Azure Pipeline Job - Databricks API step](images/part_2_pipe_adb_step.png)

6. Finally, let's confirm that the command we issued to our Databricks workspace from the Azure Pipeline actually triggered the Databricks notebook to run. In your browser, return to Azure Databricks and navigate to Workflows > Job runs. You should see a job with name "Data Prep Pipeline Run - {your branch name}" that was run as your Service Principal.


## Success criteria
- Basic understanding of how to call the Databricks API to run a notebook.
- Basic understanding that the Service Principal can execute the API call, if it is authenticated and has the right permissions.
- Basic understanding of how an Azure Pipeline can be configured to automate the sequence of steps for Service Principal authentication followed by Databricks notebook run using the Databricks API.
- Review the Azure Pipeline run.
- Confirm that the Azure Pipeline ran a notebook job in Azure Databricks.


## [Go to Part 3](part_3.md)
