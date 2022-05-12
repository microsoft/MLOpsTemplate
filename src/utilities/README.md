# Ray on Azure ML

NEW!

1. ray-on-aml now supports Spark from [raydp](https://github.com/oap-project/raydp) with Delta Lake, Synapse JDBC and latest pyspark 3.2.1. Checkout [spark examples](./examples/spark/spark_examples.ipynb)
2. GPU & custom base image for interactive use: if you have GPU compute cluster, then either use ray_on_aml.getRay(gpu_support=True) which internally uses mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.1-cudnn8-ubuntu18.04:20211221.v1 as base image. You can supply your own base image with ray_on_aml.getRay(base_image="YOUR_OWN_BASE_IMAGE")
3. VSCode is now supported. You can run interactive notebook with VSCode.

This package simplifies setup of core Ray and Ray's components such as Dask on Ray, Ray tune,Ray rrlib, Ray serve and Spark in Azure ML.
It also comes with supports for high performance data access to Azure data sources such as Azure Storage, Delta Lake , Synapse SQL.
It supports both interactive and job uses.

## Architecture

![RayOnAML_Interactive_Arch](https://github.com/james-tn/ray-on-aml/raw/master/images/RayOnAML_Interactive_Arch.png)

## Setup & Quick Start Guide


### 1. Prepare Azure ML environment

For interactive mode, setup a compute cluster and a compute instance in the same VNET.

Checklist 
> [ ] Azure Machine Learning Workspace
> 
> [ ] Virtual network/Subnet
>
> [ ] Create Compute Instance in the Virtual Network
> 
> [ ] Create Compute Cluster in the same Virtual Network

### 2. Select kernel 

Use a python 3.7+ conda environment from ```(Jupyter) Notebook``` in Azure Machine Learning Studio. 

### 3. Install library

```bash
pip install --upgrade ray-on-aml
```
> Installing this library will also install ```ray[tune]==1.12.0,  ray[serve]==1.12.0, pyarrow>= 5.0.0, dask[complete]==2021.12.0, adlfs==2021.10.0, fsspec==2021.10.1, xgboost_ray==0.1.8, fastparquet==0.7.2```

### 4. Run ray-on-aml
Run in interactive mode in a Compute Instance notebook

```python
from ray_on_aml.core import Ray_On_AML
ws = Workspace.from_config()
ray_on_aml =Ray_On_AML(ws=ws, compute_cluster ="Name_of_Compute_Cluster", maxnode=3) 
ray = ray_on_aml.getRay() 
# may take 7 mintues or longer.Check the AML run under ray_on_aml experiment for cluster status.  
```
Note that by default,the library sets up your current compute instance as Ray head and all nodes in the remote compute cluster as workers. 
If you want to use  one of the nodes in the remote AML compute cluster as head node and the remaining are worker nodes, simply pass ```ci_is_head=False``` 
to ```ray_on_aml.getRay()```.
To install additional library, use ```additional_pip_packages``` and ```additional_conda_packages``` parameters.
The ray cluster will request 5 nodes from AML if ``maxnode`` is not specified.
```python
ray_on_aml =Ray_On_AML(ws=ws, compute_cluster ="Name_of_Compute_Cluster", additional_pip_packages= \
['torch==1.10.0', 'torchvision', 'sklearn'])
```

For use in an Azure ML job, include ray_on_aml as a pip dependency and inside your script, do this to get ray
Remember to use RunConfiguration(communicator='OpenMpi') in your AML job's ScriptRunConfig so that ray-on-aml can work correctly.

```python

from ray_on_aml.core import Ray_On_AML
ray_on_aml =Ray_On_AML()
ray = ray_on_aml.getRay()

if ray: #in the headnode
    pass
    #logic to use Ray for distributed ML training, tunning or distributed data transformation with Dask

else:
    print("in worker node")
```
### 5. Ray Dashboard
The easiest way to view Ray dashboard is using the connection from [VSCode for Azure ML](https://code.visualstudio.com/docs/datascience/azure-machine-learning). 
Open VSCode to your Compute Instance then open a terminal, type http://127.0.0.1:8265/ then ctrl+click to open the Ray Dashboard.
![VSCode terminal trick](./images/vs_terminal.jpg)

This trick tells VScode to forward port to your local machine without having to setup ssh port forwarding using VScode's extension on the CI.

![Ray Dashboard](./images/ray_dashboard.jpg)


### 6. Shutdown ray cluster

To shutdown cluster,  run following.
```python
ray_on_aml.shutdown()
```

### 7. Customize Ray version and the library's base configurations

Interactive cluster: There are two arguments in Ray_On_AML() class initilization to specify base configuration for the library with following default values.
```python
Ray_On_AML(ws=ws, compute_cluster ="Name_of_Compute_Cluster",base_conda_dep =['adlfs==2021.10.0','pip==21.3.1'],\ 
base_pip_dep = ['ray[tune]==1.12.0','ray[rllib]==1.12.0','ray[serve]==1.12.0', 'xgboost_ray==0.1.6', 'dask==2021.12.0',\
'pyarrow >= 5.0.0','fsspec==2021.10.1','fastparquet==0.7.2','tabulate==0.8.9'])
```
You can change ray and other libraries versions. Do this with extreme care as it may result in conflicts impacting intended features of the package. 
If you change ray version here, you will need to manually re-install the ray library at the compute instance to match with the custom version of the cluster in case the compute instance is the head node.
AML Job cluster: If you need to customize your ray version, you can do so by adding ray dependency after ray-on-aml. The reason is ray-on-aml comes with some recent ray version. It needs to be overidden. For example if you need ray 0.8.7, you can do like following in your job's env.yml file
```python
      - ray-on-aml==0.1.8
      - ray[rllib,tune,serve]==0.8.7
```
Check out [RLlib example with customized ray version](./examples/rl/rl_main.ipynb) to learn more 
### 8. Quick start examples
Check out [quick start examples](./examples/quick_start_examples.ipynb) to learn more 

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

## Security

Microsoft takes the security of our software products and services seriously, which includes all source code repositories managed through our GitHub organizations, which include [Microsoft](https://github.com/Microsoft), [Azure](https://github.com/Azure), [DotNet](https://github.com/dotnet), [AspNet](https://github.com/aspnet), [Xamarin](https://github.com/xamarin), and [our GitHub organizations](https://opensource.microsoft.com/).

If you believe you have found a security vulnerability in any Microsoft-owned repository that meets [Microsoft's definition of a security vulnerability](https://docs.microsoft.com/en-us/previous-versions/tn-archive/cc751383(v=technet.10)), please report it to us as described below.

## Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them to the Microsoft Security Response Center (MSRC) at [https://msrc.microsoft.com/create-report](https://msrc.microsoft.com/create-report).

If you prefer to submit without logging in, send email to [secure@microsoft.com](mailto:secure@microsoft.com).  If possible, encrypt your message with our PGP key; please download it from the [Microsoft Security Response Center PGP Key page](https://www.microsoft.com/en-us/msrc/pgp-key-msrc).

You should receive a response within 24 hours. If for some reason you do not, please follow up via email to ensure we received your original message. Additional information can be found at [microsoft.com/msrc](https://www.microsoft.com/msrc). 

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

  * Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
  * Full paths of source file(s) related to the manifestation of the issue
  * The location of the affected source code (tag/branch/commit or direct URL)
  * Any special configuration required to reproduce the issue
  * Step-by-step instructions to reproduce the issue
  * Proof-of-concept or exploit code (if possible)
  * Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

If you are reporting for a bug bounty, more complete reports can contribute to a higher bounty award. Please visit our [Microsoft Bug Bounty Program](https://microsoft.com/msrc/bounty) page for more details about our active programs.


## Preferred Languages

We prefer all communications to be in English.

## Policy

Microsoft follows the principle of [Coordinated Vulnerability Disclosure](https://www.microsoft.com/en-us/msrc/cvd).
