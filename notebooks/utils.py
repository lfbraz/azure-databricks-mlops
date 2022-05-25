# Databricks notebook source
import pandas as pd
import numpy as np

# SKLearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# MLFlow
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from mlflow.tracking.client import MlflowClient
from mlflow.entities import ViewType

import shutil
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

# Shap
import shap
import matplotlib.pyplot as plt
    
def get_dataset(filename):
    data = spark.read.parquet(filename)
    return data.toPandas()

def preprocessing(dataset):
    numeric_columns = []
    for col in dataset.columns:
        if(dataset[col].dtypes!='object'):
            numeric_columns.append(col)

    dataset = dataset.dropna()
    return dataset, numeric_columns

def split_dataset(dataset, seed, test_size=0.33):
    train_dataset, test_dataset = train_test_split(dataset, random_state=seed, test_size=test_size)
    return train_dataset, test_dataset

def get_X_y(train, test, target_column, numeric_columns, drop_columns):
    X_train = train[numeric_columns].drop(drop_columns, axis=1)
    X_test = test[numeric_columns].drop(drop_columns, axis=1)

    y_train = train[target_column]
    y_test = test[target_column]
    return X_train, X_test, y_train, y_test

def persist_shap(model, X_train):
    shap_values = shap.TreeExplainer(model).shap_values(X_train)
    shap.summary_plot(shap_values, X_train, show=False)
    plt.savefig('/dbfs/mnt/documents/images/shap.png')

def train_model(X_train, y_train, X_test, y_test):
    mlflow.set_experiment('/churn-prediction')

    with mlflow.start_run(run_name='mlops-train') as run:
        train = xgb.DMatrix(data=X_train, label=y_train)
        test = xgb.DMatrix(data=X_test, label=y_test)

        # Pass in the test set so xgb can track an evaluation metric. XGBoost terminates training when the evaluation metric
        # is no longer improving.
        model = xgb.train(params=params, dtrain=train, num_boost_round=1000,\
                           evals=[(test, "test")], early_stopping_rounds=50
                         )

        mlflow.xgboost.log_model(model, 'model')
        persist_shap(model, X_train)
        mlflow.log_artifact('/dbfs/mnt/documents/images/shap.png')
        run_id = run.info.run_id

    return "runs:/" + run_id + "/model"

def validate_model(model, X_test, y_test):
    predictions_test = model.predict_proba(X_test)[:,1]
    auc_score = roc_auc_score(y_test, predictions_test)
    return auc_score

# COMMAND ----------

def get_model_uri(experiment_name, run_name):
    experiment = MlflowClient().get_experiment_by_name(experiment_name)
    experiment_ids = eval('[' + experiment.experiment_id + ']')

    query = f"tag.mlflow.runName = '{run_name}'"
    run = MlflowClient().search_runs(experiment_ids, query, ViewType.ALL)[0]

    return "runs:/" + run.info.run_id + "/model"

def load_model(model_uri):
    model = mlflow.xgboost.load_model(model_uri)
    return model

def persist_model(model, model_path):
    shutil.rmtree(model_path)

    # Persist the XGBoost model
    mlflow.xgboost.save_model(model, model_path)

def register_model(experiment_name, run_name, model_name):
    model_uri = get_model_uri(experiment_name, run_name)
    result = mlflow.register_model(model_uri, model_name)
    return result

def transition_model(model_name, stage):
    client = MlflowClient()
    model = client.search_model_versions(f"name='{model_name}'")[0]
    result = client.transition_model_version_stage(name=model.name, version=model.version, stage=stage)
    print(f'The model: {result.name} version: {result.version} was transitioned to stage: {result.current_stage}' )
