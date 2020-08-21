# Databricks notebook source
# MAGIC %md
# MAGIC ## Deploy churn prediction model
# MAGIC In this notebook we will demonstrate how to get the model generated [here]() to deploy it. We need to follow these steps:
# MAGIC 
# MAGIC - Get an already trained model
# MAGIC - Instantiate an Azure ML Workspace
# MAGIC - Build an image with the best model packaged
# MAGIC - Deploy the model to ACI (Azure Container Instance)
# MAGIC - Deploy the model to AKS (Azure Kubernetes Services)

# COMMAND ----------

# MAGIC %md
# MAGIC ## First lets get the model
# MAGIC Return the best model from `churn-prediction` experiment. We will use the same notebook **model-churn-prediction** and return the `model_uri`.

# COMMAND ----------

# MAGIC %run ./model-churn-prediction

# COMMAND ----------

# MAGIC %md ## Create/Use Azure Machine Learning Workspace
# MAGIC We will use Azure Machine Learning to deliver the API `endpoints` that will consume the Machine Learning models. To be able to interact with Azure ML we will use [Azure Machine Learning Python SDK](https://docs.microsoft.com/en-us/python/api/overview/azure/ml/?view=azure-ml-py), with it its possible to create new workspaces (or use existing ones) to facilitate the deployment process.
# MAGIC 
# MAGIC Its required to fill the variables `WORKSPACE_NAME`, `WORKSPACE_LOCATION`, `RESOURCE_GROUP` and `SUBSCRIPTION_ID` with your subscription data.
# MAGIC 
# MAGIC As default will be required the `Interactive Login` auth. For production scenarios an app registration with `Service Principal` is required. In the [documentation] (https://docs.microsoft.com/en-us/azure/machine-learning/how-to-setup-authentication#set-up-service-principal-authentication) we have more details about the different kind of authentications.

# COMMAND ----------

import azureml
from azureml.core import Workspace
import mlflow.azureml

WORKSPACE_NAME = 'wp-ml-db'
WORKSPACE_LOCATION = 'East US 2'
RESOURCE_GROUP = 'RG-Databricks'
SUBSCRIPTION_ID = 'f56912be-98e5-44e3-9e64-54bc52cef4a7'

workspace = Workspace.create(name = WORKSPACE_NAME,
                             location = WORKSPACE_LOCATION,
                             resource_group = RESOURCE_GROUP,
                             subscription_id = SUBSCRIPTION_ID,
                             exist_ok=True)

# COMMAND ----------

# MAGIC %md
# MAGIC With the `model_uri` we build an image based on it.

# COMMAND ----------

model_name = 'churn-model'
image_name = 'churn-model-image'
image_description = 'ML model to predict churn'

model_image, azure_model = mlflow.azureml.build_image(model_uri=model_uri, 
                                                      workspace=workspace,
                                                      model_name=model_name,
                                                      image_name=image_name,
                                                      description=image_description,
                                                      synchronous=False)

model_image.wait_for_creation(show_output=True)

# COMMAND ----------

# MAGIC %md #Deploy
# MAGIC Now with the image we can choose between two deployment types: `ACI` (Azure Container Instance) or `AKS` (Azure Kubernetes Service).
# MAGIC 
# MAGIC For development scenarios it is better to use `ACI` and for production `AKS` will have more options related to scalability and security. Please see more details in this [page](https://docs.microsoft.com/en-us/azure/architecture/reference-architectures/ai/mlops-python).

# COMMAND ----------

# MAGIC %md ###ACI - Azure Container Instance
# MAGIC Follow we will demonstrate how to create an `endpoint` using the image created before and delivering with `ACI`.

# COMMAND ----------

from azureml.core.webservice import AciWebservice, Webservice
from azureml.core.image import Image

dev_web_service_name = 'api-churn-dev'

model_image_id = workspace.images[image_name].id
print("Model Image ID:", model_image_id)

model_image = Image(workspace, id=model_image_id)

dev_webservice_deployment_config = AciWebservice.deploy_configuration()
dev_webservice = Webservice.deploy_from_image(name=dev_web_service_name,
                                              image=model_image,
                                              deployment_config=dev_webservice_deployment_config,
                                              workspace=workspace,
                                              deployment_target=None,
                                              overwrite=True)

dev_webservice.wait_for_deployment(show_output = True)

while dev_webservice.state != "Healthy":
  dev_webservice.update_deployment_state()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load some data to test the endpoint
# MAGIC We will use the same dataset used to train the model only for testing purposes.

# COMMAND ----------

sample = X_test.iloc[0:3,]
query_input = sample.to_json(orient="split")
query_input

# COMMAND ----------

# MAGIC %md
# MAGIC ## Call the API
# MAGIC Make a request to the API using `query_input`. The API url can be obtained throught `dev_webservice.scoring_uri` generated from deployment process.

# COMMAND ----------

import requests
import json

def query_endpoint_example(scoring_uri, inputs, service_key=None):
  headers = {
    "Content-Type": "application/json",
  }
  if service_key is not None:
    headers["Authorization"] = "Bearer {service_key}".format(service_key=service_key)
  
  print('URI: {}'.format(scoring_uri))
  print("Sending batch prediction request with inputs: {}".format(inputs))
  response = requests.post(scoring_uri, data=json.loads(json.dumps(inputs)), headers=headers)
  preds = json.loads(response.text)
  print("Received response: {}".format(preds))
  return preds

query_endpoint_example(scoring_uri=dev_webservice.scoring_uri, inputs=query_input)

# COMMAND ----------

# MAGIC %md
# MAGIC It is also possible to use API using any client to make HTTP requests (curl, postman, etc.).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Azure Kubernetes Services (AKS)
# MAGIC For production scenarios it is better to deploy using AKS because we have more benefits about security and scalability.
# MAGIC 
# MAGIC In this scenario is possible to follow two ways: Creating a new AKS cluster or targeting to an existing one. In this tutorial we will use a existing cluster.

# COMMAND ----------

from azureml.core.webservice import Webservice, AksWebservice
from azureml.core.compute import AksCompute

aks_name = 'aks-cluster-1'
aks_target = AksCompute(workspace, aks_name)
deployment_config = AksWebservice.deploy_configuration(cpu_cores = 1, memory_gb = 1)

# Set configuration and service name
prod_webservice_name = 'api-churn-prod'
prod_webservice_deployment_config = AksWebservice.deploy_configuration()

# Deploy from image
prod_webservice = Webservice.deploy_from_image(workspace = workspace, 
                                               name = prod_webservice_name,
                                               image = model_image,
                                               deployment_config = prod_webservice_deployment_config,
                                               deployment_target = aks_target,
                                               overwrite=True)

prod_webservice.wait_for_deployment(show_output = True)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Call the API (with AKS)

# COMMAND ----------

prod_scoring_uri = prod_webservice.scoring_uri
prod_service_key = prod_webservice.get_keys()[0] if len(prod_webservice.get_keys()) > 0 else None

query_endpoint_example(scoring_uri=prod_scoring_uri, service_key=prod_service_key, inputs=query_input)