# Databricks notebook source
# MAGIC %run /Shared/utils

# COMMAND ----------

# Experiment parameters
experiment_name = '/churn-prediction'
run_name = 'mlops-train'
dev_web_service_name = 'api-churn-dev'

# Workspace parameters
workspace_name = 'wp-ml-db'
workspace_location = 'East US 2'
resource_group = 'RG-Databricks'
subscription_id = 'f56912be-98e5-44e3-9e64-54bc52cef4a7'

# Image parameters
image_name = 'churn-model-image'
image_description = 'ML model to predict churn'
model_name = 'churn-model'

model_uri = get_model_uri(experiment_name, run_name)
workspace = get_workspace(workspace_name, workspace_location, resource_group, subscription_id)

build_image(workspace, model_uri, model_name, image_name, image_description)