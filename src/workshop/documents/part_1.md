
# Part 1: Structure code for fast iterative development
## Pre-requisites
- Complete [Part 0](part_0.md) to setup the Azure ML workspace. Ensure the following:
	- Your conda environment ``mlops-workshop-local`` is activated.
	- You completed the step to run [create_datasets.py](part_0.md#option-a-use-compute-instance-for-code-development).

## Summary 
Your team has been working on a new ML problem. The team has been performing exploratory work on data and algorithm and has come to a state that the solution direction is solidified. Now, it is a time to put a structure into the work so that the team can iterate faster toward building a fully functional solution.   

So far, team members have been working mostly on Jupyter notebooks on their personal compute (Azure CI & PC). As the first step in MLOps, your team needs to accompblish the followings:  

- Modularization: monolithic notebook is refactored into python modules that can be developed and tested independently and in parallel by multiple members 
- Parameterization: The modules are parameterized so that they be rerun with different parameter values.

To illustrate how the process works, the notebook was refactored into a feature engineering module, an ml training module and an ml evaluating module and you will run these modules individually in local development environment to see how they work.

 ![monolithic to modular](./images/monolithic_modular.png)

## Steps

> Note: You can run following tasks on Compute Instance in your Azure Machine Learning. You can use __Jupyter__ or __VSCode__.

1. Familiarize yourself with the steps in this [jupyter
  notebook](../notebooks/taxi-tutorial.ipynb). This showcases the overall data engineering and model building
  process. **There is no need to run this as part of this workshop.**
    > Note: If you do want to run this notebook, it is recommended to run this in a virtual environment using the conda dependencies specified in this file: `MLOpsTemplate/src/workshop/conda-local.yml`. Additionally, if you run the notebook from a Compute Instance, you can first configure your conda environment with these dependencies, and then leverage the ability to add new kernels referenced [here](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-access-terminal#add-new-kernels) to run your notebook.
   
2. Discuss in your team why a monolithic code structure is a challenge to a scalable and repeatable ML development process? 
    > Note: Now observe how the monolithic notebook was refactored into a feature/data engineering module, a ML training module and a model validation module so that they can be developed and run independently.

3. Go to the workshop folder.
    > Action Items: Run the following code snippet.
    ```bash 
    cd src/workshop
    ```
    > Note: Review the ```workshop/data``` folder. There are data files that were created by the data generation process. The same data files were also sent to the  Azure Machine Learning Studio's default datastore under ```workspaceblobstore/mlops_workshop/data```.
4. Create your own development branch where you can make and track changes. This branch will be your development area to create and test new code or pipelines before committing or merging the code into a common branch, such as ```integration```.

    - Run following command to create a new branch named "yourname-dev"
        ```bash
        git checkout -b yourname-dev
        ```
    - This will set the working branch to ```yourname-dev```. To check, run the following command:
        ```bash
        git branch
        ```
5. Review the refactored engineering logic from the notebook at ```feature_engineering.py``` module under the ```data_engineering``` folder.
    - The module performs the following:
        - Accepts the following parameters:
            - ```input_folder```: path to a folder for input data. The value for local test run is ```data```
            - ```prep_data```: path to a folder for output data. The value for local test run is ```data```
            - ```public_holiday_file_name```: name of the public holiday file. The value for local test run is ```holidays.parquet``` 
            - ```weather_file_name```: name of the weather raw file.It's ```weather.parquet``` 
            - ```nyc_file_name```: name of the newyork taxi raw file. It's ```green_taxi.parquet``` 
        - Performs data transformation, data merging and feature engineering logics 
        - Splits the data into train and test sets where test_size is 20%
        - Writes the output data files to output folder
        > Action Item: Run the following code snippet.
         ```bash 
          python core/data_engineering/feature_engineering.py \
	  --input_folder data \
	  --prep_data data \
	  --public_holiday_file_name holidays.parquet \
	  --weather_file_name weather.parquet \
	  --nyc_file_name green_taxi.parquet
5. Review the refactored ML training logic at ```ml_training.py``` module under training folder. 
    - The module performs the following:
        - Accepts the following parameters:
            - ```prep_data```: path to a folder for input data. The value for local test run is ```data```
            - ```input_file_name```: name of the input train data file. The value for local test run is ```final_df.parquet```
            - ```model_folder```: path to a output folder to save trained model.The value for local test run is ```data```
        - Splits input train data into train and validation dataset, perform training  
        - Prints out MAPE, R2 and RMSE metrics
        - Writes the train model file to output folder
        > Action Item: Run the following code snippet.
         ```bash 
          python core/training/ml_training.py \
	  --prep_data data \
	  --input_file_name final_df.parquet \
	  --model_folder data
6. Review the refactored ML training logic at ```ml_evaluating.py``` module under evaluating folder. 
    - The module performs the following:
        - Accepts the following parameters:
            - ```prep_data```: path to a folder for test input data.The value for local test run is ```data```.
            - ```input_file_name```: name of the input test data file. The value for local test run is  ```test_df.parquet```.
            - ```model_folder```: path to a model folder.The value for local test run is ```data```
        - Loads the model 
        - Scores the model on input test data, print out MAPE, R2 and RMSE metrics
        > Action Item: Run the following code snippet.
         ```bash 
            python core/evaluating/ml_evaluating.py \
	       --prep_data data \
	       --input_file_name test_df.parquet

## Success criteria
- Feature engineering module: 
    - Data is processed correctly and output to a folder as final_df.parquet and test_df.parquet files and ready to be ML trained
- ML training module
    - Perform ML training and print out MAPE, R2 and RMSE metrics from input datasets
    - Produce the model at the output location
- ML evaluating module
    -  Perform ML training and print out MAPE, R2 and RMSE metrics from an input dataset and output a model file

## [Go to Part 2](part_2.md)
