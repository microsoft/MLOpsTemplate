# MLOps Workshop

## Introduction
The MLOps workshop is an instructor-led workshop that provides guidance on an MLOps
implementation in Azure. MLOps is a pattern of practices rather than a technology, and there are various ways of implementing MLOps on Azure. This workshop leverages [Azure Databricks](https://learn.microsoft.com/en-us/azure/databricks/introduction/)
and [Azure DevOps](https://learn.microsoft.com/en-us/azure/devops/user-guide/what-is-azure-devops?view=azure-devops)
to implement a robust set of workflows to support machine learning models in production. For a workshop using Azure Machine Learning and GitHub Actions, see a similar set of materials [here](https://github.com/microsoft/MLOpsTemplate/).

The core capability deployed in this scenario is a prediction of wine quality using a set of empirical measures. This is based on a [UCI Dataset](https://archive.ics.uci.edu/dataset/186/wine+quality). This is treated as a classification scenario, which occurs frequently for many enterprises. For the purpose of this workshop, the key stages of exploring the data,
engineering predictive features (data engineering) and model building (training, hyperparameter tuning,
algorithm selection, etc.) will be assumed to be done and already codified in this [Databricks
notebook](https://learn.microsoft.com/en-us/azure/databricks/mlflow/end-to-end-example).
The core focus of the workshop will then be how to refactor this notebook for easier maintenance and iterative development, lay the DevOps foundations for the ML lifecycle, for continuous delivery of the best predictive capabilities in production even as data science team members experiment with new techniques to improve model performance.

## Audience
- Data scientists
- ML engineers
- ML platform architects and managers
- ... and any other roles that require hands-on experience to support ML models in Azure

## Goals
- Understand key elements of modern MLOps and how it helps improve and accelerate ML practices.
- Design experiments and MLOps pipelines in Azure Databricks.
- Get hands-on experience in building continuous integration and continuous deployment pipelines with Azure DevOps.


Now, head to [Workshop Environment Setup: Part 0](documents/part_0.md)


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
