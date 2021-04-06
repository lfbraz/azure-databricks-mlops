# Databricks notebook source
import pandas as pd
import numpy as np

# Azure libs
from azureml.core.webservice import AciWebservice,  AksWebservice, Webservice
from azureml.core.image import Image
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
<<<<<<< HEAD
=======
from azureml.core.compute import AksCompute
from azureml.exceptions import WebserviceException
>>>>>>> 87fd260fb1fc4ef5602bc8afb22e17c450a32115

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

def deploy_aci(workspace, model_uri, endpoint_name, model_name):
  aci_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=1)

  # Remove any existing service under the same name.
  try:
    Webservice(workspace, endpoint_name).delete()
  except WebserviceException:
    pass
  
  (webservice, model) = mlflow.azureml.deploy(model_uri=model_uri,
                                              workspace=workspace,
                                              model_name=model_name,
                                              service_name=endpoint_name,
                                              deployment_config=aci_config)

  print(f"Model : {model_uri} was successfully deployed to ACI")
  print(f"Endpoint : {webservice.scoring_uri} created")
  
def deploy_aks(workspace, model_uri, endpoint_name, model_name, aks_name): 
  aks_target = AksCompute(workspace, aks_name)
  deployment_config = AksWebservice.deploy_configuration(compute_target_name=aks_name)
  
  # Remove any existing service under the same name.
  try:
    Webservice(workspace, endpoint_name).delete()
  except WebserviceException:
    pass
  
  (webservice, model) = mlflow.azureml.deploy(model_uri=model_uri,
                                              workspace=workspace,
                                              model_name=model_name,
                                              service_name=endpoint_name,
                                              deployment_config=deployment_config)
  
  print(f"Model : {model_uri} was successfully deployed to AKS")
  print(f"Endpoint : {webservice.scoring_uri} created")