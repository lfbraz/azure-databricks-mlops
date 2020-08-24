# Databricks notebook source
import pandas as pd
import numpy as np
# Azure libs
from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import Image
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
# SKLearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
# MLFlow
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import mlflow.azureml
from mlflow.tracking.client import MlflowClient
from mlflow.entities import ViewType

def get_dataset(filename):
  data = pd.read_csv("/dbfs/dataset/{}".format(filename), sep=',')
  return data

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

def train_model(X, y, n_estimators, seed):
  mlflow.xgboost.autolog()
  mlflow.set_experiment('/churn-prediction')
  
  with mlflow.start_run(run_name='mlops-train') as run:
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=np.random.RandomState(seed))
    model.fit(X, y)
    mlflow.sklearn.log_model(model, 'model')
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

def get_workspace(workspace_name, workspace_location, resource_group, subscription_id):
  svc_pr = ServicePrincipalAuthentication(
      tenant_id = dbutils.secrets.get(scope = "azure-key-vault", key = "tenant-id"),
      service_principal_id = dbutils.secrets.get(scope = "azure-key-vault", key = "client-id"),
      service_principal_password = dbutils.secrets.get(scope = "azure-key-vault", key = "client-secret"))

  workspace = Workspace.create(name = workspace_name,
                               location = workspace_location,
                               resource_group = resource_group,
                               subscription_id = subscription_id,
                               auth=svc_pr,
                               exist_ok=True)
  
  return workspace

def build_image(workspace, model_uri, model_name, image_name, image_description):
  print(model_uri, workspace, model_name, image_name, image_description)
  model_image, azure_model = mlflow.azureml.build_image(model_uri=model_uri, 
                                                      workspace=workspace,
                                                      model_name=model_name,
                                                      image_name=image_name,
                                                      description=image_description,
                                                      synchronous=False)

  model_image.wait_for_creation(show_output=True)

def deploy_aci(endpoint_name, image_name):
  model_image_id = workspace.images[image_name].id
  print("Model Image ID:", model_image_id)

  model_image = Image(workspace, id=model_image_id)

  dev_webservice_deployment_config = AciWebservice.deploy_configuration()

  dev_webservice = Webservice.deploy_from_image(name=endpoint_name,
                                                image=model_image,
                                                deployment_config=dev_webservice_deployment_config,
                                                workspace=workspace,
                                                deployment_target=None,
                                                overwrite=True)

  dev_webservice.wait_for_deployment(show_output = True)