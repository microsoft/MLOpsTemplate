import pandas as pd
import numpy as np
import os
import argparse
from azureml.core import Run, Dataset,Datastore, Workspace
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score, mean_absolute_percentage_error, mean_squared_error
import joblib
from azureml.core import Model
import mlflow
def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_file_name", type=str, default="test_df.parquet")
    parser.add_argument("--prep_data", default="data", type=str, help="Path to prepped data")
    parser.add_argument("--model_folder", default="data", type=str, help="Path to model data")
    parser.add_argument("--model_name",default='nyc_fare_prediction',type=str, help="Name of the model in workspace")
    parser.add_argument("--run_mode", type=str, default="local")


    # parse args
    args = parser.parse_args()

    # return args
    return args



def main(args):
    if args.run_mode =='remote':
        run = Run.get_context()
        ws = run.experiment.workspace
        run_id = run.id
    
    # read in data
    test_df = pd.read_parquet(os.path.join(args.prep_data,args.input_file_name))

    catg_cols = ["vendorID", "month_num", "day_of_month", "normalizeHolidayName", "isPaidTimeOff"]
    # num_cols = ["passengerCount", "tripDistance", "precipTime", "temperature", "precipDepth", "hr_sin", "hr_cos", "dy_sin", "dy_cos"]
    label = ["totalAmount"]
    # make sure categorical columns are strings
    test_df[catg_cols] = test_df[catg_cols].astype("str")
    
    # split data
    y_test = test_df[label]
    X_test = test_df.drop(label, axis=1)
    
    # load model'
    
    if args.run_mode =='local':
        model_file = "linear_regression.joblib"
        model_path=os.path.join(args.model_folder,model_file)
        current_model = joblib.load(model_path)
        y_pred_current = current_model.predict(X_test)                              
        r2 = r2_score(y_test, y_pred_current)
        mape = mean_absolute_percentage_error(y_test, y_pred_current)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_current))
        print("Evaluation finished! Metrics:")
        print(f"R2:", r2)
        print(f"MAPE:", mape)
        print(f"RMSE:", rmse)

    if args.run_mode =='remote':
           
        for model_file in os.listdir(args.model_folder):
            if ".joblib" in model_file:
                candidate_model_file=model_file
        candidate_model_path=os.path.join(args.model_folder,candidate_model_file)
        candidate_model = joblib.load(candidate_model_path)
        
        y_pred_candidate = candidate_model.predict(X_test)                               
        r2_candidate = r2_score(y_test, y_pred_candidate)
        mape_candidate = mean_absolute_percentage_error(y_test, y_pred_candidate)
        rmse_candidate = np.sqrt(mean_squared_error(y_test, y_pred_candidate))
        mlflow.log_metric("mape_candidate",mape_candidate)
        mlflow.log_metric("r2_candidate",r2_candidate)
        mlflow.log_metric("rmse_candidate",rmse_candidate)
        
        current_model=None

        try:
            current_model_aml = Model(ws,args.model_name)
            os.makedirs("current_model", exist_ok=True)
            current_model_aml.download("current_model",exist_ok=True)
            current_model = mlflow.sklearn.load_model(os.path.join("current_model",args.model_name))
        except:
            print("Model does not exist")
    
        if current_model: #current model exist, perform evaluation
            # test 2 algorithms
            y_pred_current = current_model.predict(X_test)                              
            r2_current = r2_score(y_test, y_pred_current)
            mape_current = mean_absolute_percentage_error(y_test, y_pred_current)
            rmse_current = np.sqrt(mean_squared_error(y_test, y_pred_current))
            mlflow.log_metric("mape_current",mape_current)
            mlflow.log_metric("r2_current",r2_current)
            mlflow.log_metric("rmse_current",rmse_current)
            if r2_candidate >= r2_current:
                print("better model found, registering")
                mlflow.sklearn.log_model(candidate_model,args.model_name)
                model_uri = f'runs:/{run_id}/{args.model_name}'
                mlflow.register_model(model_uri,args.model_name)

            else:
                raise Exception("candidate model does not perform better, exiting")
        
        else:
            print("First time model train, registering")
            mlflow.sklearn.log_model(candidate_model,args.model_name)
            model_uri = f'runs:/{run_id}/{args.model_name}'
            mlflow.register_model(model_uri,args.model_name)

# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)
