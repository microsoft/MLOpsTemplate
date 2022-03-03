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
def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--nyc_ml_dataset", type=str, default="NycTlc_ML_Test")
    parser.add_argument("--input_file_name", type=str, default="test_df.parquet")
    parser.add_argument("--run_mode", type=str, default="local")
    parser.add_argument("--datastore_name", type=str, default="mltraining")
    parser.add_argument("--prep_data", default=None, type=str, help="Path to prepped data")
    parser.add_argument("--model_folder", default="model", type=str, help="Path to model data")
    parser.add_argument("--model_name", type=str, help="Name of the model in workspace")


    # parse args
    args = parser.parse_args()

    # return args
    return args



def main(args):
    # read in data
    if args.run_mode =='remote':
        run = Run.get_context()
        ws = run.experiment.workspace
    else:
        ws = Workspace.from_config()
    # datastore= ws.datastores[args.datastore_name]
    if args.prep_data is not None: #when this script does not run in the pipeline mode
        print("in pipeline mode")
        test_df = pd.read_parquet(os.path.join(args.prep_data,args.input_file_name))

    else:
        print("in standalone mode")
        test_df = ws.datasets[args.nyc_ml_dataset].to_pandas_dataframe()
    catg_cols = ["vendorID", "month_num", "day_of_month", "normalizeHolidayName", "isPaidTimeOff"]
    # num_cols = ["passengerCount", "tripDistance", "precipTime", "temperature", "precipDepth", "hr_sin", "hr_cos", "dy_sin", "dy_cos"]
    label = ["totalAmount"]
    # make sure categorical columns are strings
    test_df[catg_cols] = test_df[catg_cols].astype("str")
    y_test = test_df[label]
    X_test = test_df.drop(label, axis=1)
    # split data
    candidate_model_file = os.listdir(args.model_folder)[0]
    candidate_model_path=os.path.join(args.model_folder,candidate_model_file)
    candidate_model = joblib.load(candidate_model_path)
    current_model=None
    try:
        current_model = Model(ws,args.model_name )
        os.makedirs("current_model", exist_ok=True)

        current_model.download("current_model")
        current_model_file =os.listdir("current_model")[0]
        print("current_model_file ",current_model_file)
        current_model = joblib.load(os.path.join("current_model",current_model_file))
    except:
        print("Model does not exist")
    if current_model: #current model exist, perform evaluation

    # test 2 algorithms
        y_pred_current = current_model.predict(X_test)                              
        r2_current = r2_score(y_test, y_pred_current)
        mape_current = mean_absolute_percentage_error(y_test, y_pred_current)
        rmse_current = np.sqrt(mean_squared_error(y_test, y_pred_current))
        run.log(r2_current,"r2_current")
        run.log(mape_current,"mape_current")
        run.log(rmse_current,"rmse_current")

        y_pred_candidate = candidate_model.predict(X_test)                               
        r2_candidate = r2_score(y_test, y_pred_candidate)
        mape_candidate = mean_absolute_percentage_error(y_test, y_pred_candidate)
        rmse_candidate = np.sqrt(mean_squared_error(y_test, y_pred_candidate))

        run.log(r2_candidate,"r2_candidate")
        run.log(mape_candidate,"mape_candidate")
        run.log(rmse_candidate,"rmse_candidate")


        if r2_candidate > r2_current:
            print("better model found, registering")
            Model.register(ws,model_path=candidate_model_path,model_name=args.model_name)
        else:
            
            raise Exception("candidate model does not perform better, exiting")
    else:
        print("First time model train, registering")
        Model.register(ws,model_path=candidate_model_path,model_name=args.model_name)
# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)