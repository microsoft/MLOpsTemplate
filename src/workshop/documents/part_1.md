
# Part 1: Structure code for fast iterative development

## Goal 
Your team has been working on a new ML problem. The team has been performing exploratory work on data and algorithm and has come to the state that the solution direction is solidified. Now, it is a time to put a structure into the work so that the team can iterate faster toward building a fully functional solution.   

So far, team members working mostly on Jupyter notebook on their personal compute (Azure CI & PC), as the first step in MLOps, you need to re-engineer the process so that the team can achieve the followings:  

- Modularization: restructure the notebook into python modules
- Parameterization: Adding parameters so that modules can be rerun with different parameters 

## Pre-requisites
- Complete [Part 0](https://github.com/microsoft/MLOpsTemplate/blob/hyun-dev/src/workshop/documents/part_0.md) the setup process to setup Azure ML workspace
- Run [create_datasets.py](https://github.com/microsoft/MLOpsTemplate/blob/hyun-dev/src/workshop/documents/part_0.md#option-a-use-compute-instance-for-code-development) to create local datasets for unit test as well remote full dataset

## Tasks

> Note: You can run following tasks on Compute Instance in your Azure Machine Learning. You can use __Jupyter__ or __VSCode__.

- Review the [jupyter notebook](../notebooks/taxi-tutorial.ipynb) that represent the work of a data scientist up to this point, make sure you can run the notebook and understand it.
- Split the notebook into a feature/data engineering module, a ML training module and a model validation module 
- Parameterize the module so that they can accept different input values at runtime
- Detailed instructions:
    - Review the templates under ```data_engineering```, ```training``` and   ```evaluating``` folders
    - Create 3 seperate folders: ```my_data_engineering```, ```my_evaluating```, ```my_training``` under ```workshop/core``` folder
    - Check the workshop/data folder: there are data files that were created by the data generation process. The same data files were also sent to your datastore 
    - Refactor the data engineering logic into a ```feature_engineering.py``` module under ```data_engineering``` folder. The module performs the followings:
        - Accept following parameters:
            - ```input_folder```: path to a folder for input data which is ```data```
            - ```prep_data```: path to a folder for output data
            - ```public_holiday_file_name```: name of the public holiday file. It's ```holidays.parquet``` file in data folder
            - ```weather_file_name```: name of the weather raw file.It's ```weather.parquet``` file in data folder
            - ```nyc_file_name```: name of the newyork taxi raw file. It's ```green_taxi.parquet``` file in data folder
        - Perform data transformation, data merging and feature engineering logics 
        - Split the data into train and test sets where test_size is 20%
        - Write the output data files to output folder
        - Check and run reference solution at ```core/data_engineering/feature_engineering.py```
            - Go to src/workshop ```cd src/workshop```
            - Run ```python core/data_engineering/feature_engineering.py --input_folder data --prep_data data --public_holiday_file_name holidays.parquet --weather_file_name weather.parquet --nyc_file_name green_taxi.parquet```
    - Refactor the ML training logic into a ```ml_training.py``` module under training folder. The module performs the followings:
        - Accept following parameters:
            - prep_data: path to a folder for input data. In stanalone mode, it's the ```data``` folder.
            - input_file_name: name of the input train data file. In stanalone mode, it's the ```final_df.parquet``` in the ```data``` folder.
            - model_folder: path to a output folder to save trained model
        - Split input train data into train and validation dataset, perform training  
        - print out MAPE, R2 and RMSE metrics
        - Write the train model file to output folder
        - Check and run reference solution at ```core/training/training.py```
            - Go to src/workshop ```cd src/workshop```
            - Run ```python core/training/ml_training.py --prep_data data --input_file_name final_df.parquet --model_folder data```

    - Refactor the ML validation logic into a ```ml_evaluating.py``` module under evaluating folder. The module performs the followings:
        - Accept following parameters:
            - prep_data: path to a folder for test input data.In stanalone mode, it's the ```data``` folder.
            - input_file_name: name of the input test data file. It's the ```test_df.parquet``` in the ```data``` folder.
            - model_folder: path to a model folder 
        - Load the model 
        - Score the model on input test data, print out MAPE, R2 and RMSE metrics
        - Check and run reference solution at ```core/evaluating/ml_evaluating.py```
            - Go to src/workshop ```cd src/workshop```
            - Run ```python core/evaluating/ml_evaluating.py --prep_data data --input_file_name test_df.parquet```

## Success criteria
- Feature engineering module:
    - The feature_engineering module can accept the unit test input files 
    - Data is processed correctly and output to a folder as final_df.parquet and test_df.parquet files and ready to be ML trained
- ML training module
    - Perform ML training and print out Accuracy, R2 and RMSE metrics from input unit test dataset
    - Produce the model at the output location
- ML evaluating module
    -  Perform ML training and print out Accuracy, R2 and RMSE metrics from an input dataset and output a model file
- Run the 3 modules in a sequence of feature_engineering -> ml_training -> ml_evaluating with next module uses output from the previous module


## Reference materials

---

## [To Next Part 2](https://github.com/microsoft/MLOpsTemplate/blob/hyun-dev/src/workshop/documents/part_2.md)
