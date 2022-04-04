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
- README.md
- conda-local.yml > Configuration for conda environment, with dependencies
- core
	- data_engineering > Python and yaml files to support feature engineering code
	- evaluating > Python and yaml files to support model evaluation based upon key metrics
│   ├── pipelines
│   │   ├── my_training_pipeline.yml
│   │   └── training_pipeline.yml
│   ├── scoring
│   │   ├── conda.yml
│   │   ├── deployment.yml
│   │   ├── endpoint.yml
│   │   ├── my_deployment.yml
│   │   ├── my_endpoint.yml
│   │   ├── score.py
│   │   └── scoring_test_request.json
│   └── training
│       ├── conda_ml_training.yml
│       ├── ml_training.py
│       ├── ml_training.yml
│       ├── my_ml_training.yml
│       └── scripts
│           ├── __init__.py
│           ├── authentication
│           │   ├── __init__.py
│           │   └── service_principal.py
│           ├── existing_model
│           │   ├── __init__.py
│           │   ├── feature_engineer.py
│           │   ├── register_dataset.py
│           │   ├── register_model.py
│           │   └── train_pipeline.py
│           └── setup
│               ├── __init__.py
│               ├── clusters.py
│               └── create-aml-infra.sh
├── data
│   ├── create_datasets.py
│   ├── final_df.parquet
│   ├── green_taxi.parquet
│   ├── holidays.parquet
│   ├── linear_regression.joblib
│   ├── random_forest.joblib
│   ├── test_df.parquet
│   └── weather.parquet
├── documents
│   ├── EZMLOps_introduction.pptx
│   ├── IaC
│   │   ├── iac_cc.yml
│   │   ├── iac_ci.yml
│   │   └── iac_mlopsworkshop.azcli
│   ├── images
│   │   ├── cicd.png
│   │   ├── cloudshell.png
│   │   ├── monolithic_modular.png
│   │   ├── part3cicd.png
│   │   ├── run_mlopsworkshop_azcli000.png
│   │   ├── run_mlopsworkshop_azcli001.png
│   │   ├── run_mlopsworkshop_azcli002.png
│   │   ├── run_mlopsworkshop_azcli003.png
│   │   ├── run_mlopsworkshop_azcli004.png
│   │   ├── run_mlopsworkshop_azcli005.png
│   │   ├── run_mlopsworkshop_azcli006.png
│   │   ├── run_mlopsworkshop_azcli007.png
│   │   ├── run_mlopsworkshop_azcli008.png
│   │   ├── run_mlopsworkshop_azcli009.png
│   │   ├── run_mlopsworkshop_azcli010.png
│   │   └── training_pipeline.png
│   ├── part_0.md
│   ├── part_1.md
│   ├── part_2.md
│   ├── part_3.md
│   ├── part_4.md
│   └── part_5.md
├── infra
│   └── conda.yml
└── notebooks
    └── taxi-tutorial.ipynb


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
