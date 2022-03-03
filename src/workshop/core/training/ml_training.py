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
def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--nyc_ml_dataset", type=str, default="NycTlc_ML")
    parser.add_argument("--run_mode", type=str, default="local")
    parser.add_argument("--datastore_name", type=str, default="mltraining")
    parser.add_argument("--prep_data", default=None, type=str, help="Path to prepped data")
    parser.add_argument("--model_folder", type=str,default="model", help="Path of model ouput folder")
    parser.add_argument("--input_file_name", type=str, default="final_df.parquet")


    # parse args
    args = parser.parse_args()

    # return args
    return args


def createClassModel(algo_name, catg, nums):
  numeric_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='constant', fill_value=0))])
  
  categorical_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='constant', fill_value="MISSING")), ('onehot', OneHotEncoder(handle_unknown='ignore'))])
  
  preprocesser = ColumnTransformer(transformers=[('num', numeric_transformer, nums), ('cat', categorical_transformer, catg)])
  
  if algo_name == 'linear_regression':
    model = LinearRegression()
  elif algo_name == 'random_forest':
    model = RandomForestRegressor()
  else:
    pass
  ModelPipeline = Pipeline(steps=[('preprocessor', preprocesser), ("model", model)])
  return ModelPipeline

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
        final_df = pd.read_parquet(os.path.join(args.prep_data,args.input_file_name))
    else:
        print("in standalone mode")
        final_df = ws.datasets[args.nyc_ml_dataset].to_pandas_dataframe()
    catg_cols = ["vendorID", "month_num", "day_of_month", "normalizeHolidayName", "isPaidTimeOff"]
    num_cols = ["passengerCount", "tripDistance", "precipTime", "temperature", "precipDepth", "hr_sin", "hr_cos", "dy_sin", "dy_cos"]
    label = ["totalAmount"]
    # make sure categorical columns are strings
    final_df[catg_cols] = final_df[catg_cols].astype("str")

    # split data
    X_train, X_test, y_train, y_test = train_test_split(final_df.drop(label, axis=1), final_df[label], test_size=0.2, random_state=222)

    # test 2 algorithms
    os.makedirs(args.model_folder, exist_ok=True)

    for algorithmname in ["linear_regression", "random_forest"]:
        fitPipeline = createClassModel(algorithmname, catg_cols, num_cols) # get pipeline
        fitPipeline.fit(X_train, y_train.values.ravel())                   # fit pipeine

        y_pred = fitPipeline.predict(X_test)                               # score with fitted pipeline

        # Evaluate
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        if args.run_mode =='remote':
            run.log("algorithm",algorithmname)
            run.log("R2", r2)
            run.log("MAPE", mape)
            run.log("RMSE", rmse)
        else:
            print(algorithmname)
            print("R2:", r2)
            print("MAPE:", mape)
            print("RMSE:", rmse)
        joblib.dump(fitPipeline,args.model_folder+"/"+algorithmname+".joblib")

# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)