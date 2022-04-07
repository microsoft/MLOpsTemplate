# MLOps Workshop

## Introduction
The MLOps workshop is an instructor-led workshop that provides guidance on an MLOps
implementation in Azure. This workshop leverages [Azure Machine
Learning](https://azure.microsoft.com/en-us/services/machine-learning/?msclkid=99faf4b9b43f11ec8a3dc121747bf2a7)
and [Github
Actions](https://docs.microsoft.com/en-us/azure/developer/github/github-actions?msclkid=a9587556b43f11ecb200fd14b82d03f0)
to implement a robust set of workflows to support machine learning models in production. 

Initially, we will start with code in a single Jupyter notebook that outputs a model for a regression problem.
This code will then move to a Github environment and be modularized and version controlled. This will lay the
foundation for good software practices and allow multiple data scientists/engineers to work collaboratively on
the code in a distributed manner. Then, we will reinforce DevOps practices around continuous integration and
continuous deployment with specific workflows to support model training and evaluation. MLOps builds off a
strong foundation in DevOps and looks to additionally manage the model and data lifecycles to support the best model
in production.

The core business problem revolves around predicting taxi fares in New York. This is based on an [Azure Open
Dataset](https://azure.microsoft.com/en-us/services/open-datasets/#overview) sourced from
[here](https://docs.microsoft.com/en-us/azure/open-datasets/dataset-taxi-green?tabs=azureml-opendatasets). The
need to predict numerical values is a regression problem that is a common need for many enterprises across
data sets in their organizations. For the purpose of this workshop, the key stages of exploring the data,
engineering predictive features (data engineering) and model building (training, hyperparameter tuning,
algorithm selection, etc.) will be assumed to be done and already codified in this [Jupyter
notebook](https://github.com/microsoft/MLOpsTemplate/blob/thomassantosh-dev/src/workshop/notebooks/taxi-tutorial.ipynb).
The core focus of the workshop will then be how to productionalize this code, lay the DevOps foundation, and
support the best model in production.


## Audience
- Customer data scientists
- ML engineers
- ML platform architects and managers
- ... and any other roles that require hands-on experience to support ML models in Azure

## Goals
- Understand key elements of modern MLOps and how it helps improve and accelerate ML practices.
- Design experiments, deployment environments and MLOps pipelines in Azure Machine Learning.
- Get hands-on experience in building continuous integration and continuous deployment pipelines with new Azure ML vNext and Github Actions.

## Structure
- Part 0: [MLOps overview and environment setup](documents/part_0.md)
- Part 1: [Structure code for fast iterative development](documents/part_1.md)
- Part 2: [Use cloud scale compute and monitor experiment with Azure ML](documents/part_2.md)
- Part 3: [Use github for version control and automation](documents/part_3.md)
- Part 4: [Continuous integration (CI)](documents/part_4.md)
- Part 5: [Continuous deployment (CD)](documents/part_5.md) 
- Part 6: Observability 

## Repo Structure
- `README.md`
- `conda-local.yml` > Python third-party dependencies, specified for a conda environment
- `core`
	- ``data_engineering`` > Python and YAML files to support feature engineering
	- ``evaluating`` > Python and YAML files to support model evaluation based on specific model metrics
	- ``pipelines`` > YAML files to support creation of ML pipelines
	- ``scoring`` > Python and YAML files to support model deployment and scoring
	- ``training`` > Python and YAML files to support model training
- ``data`` > Base datasets in parquet, with a Python file to load the data into the default datastore
- ``documents`` > Setup scripts, and markdown files to support a hands-on workshop
- ``infra`` > Setup scripts to support initial creation of the Azure Machine Learning infrastructure and resources
- ``notebooks`` > Jupyter notebook containing all the code related to data exploration, cleansing, feature engineering and model
  creation


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
