# Databricks notebook source
# MAGIC %run /Shared/utils

# COMMAND ----------

# Experiment parameters
experiment_name = '/churn-prediction'
run_name = 'mlops-train'
dev_web_service_name = 'api-churn-dev'

# Workspace parameters
workspace_name = dbutils.secrets.get(scope = "azure-key-vault", key = "workspace-name")
workspace_location = dbutils.secrets.get(scope = "azure-key-vault", key = "location")
resource_group = dbutils.secrets.get(scope = "azure-key-vault", key = "resource-group")
subscription_id = dbutils.secrets.get(scope = "azure-key-vault", key = "subscription-id")

# Image parameters
image_name = 'churn-model-image'
image_description = 'ML model to predict churn'
model_name = 'churn-model'

model_uri = get_model_uri(experiment_name, run_name)
workspace = get_workspace(workspace_name, workspace_location, resource_group, subscription_id)

build_image(workspace, model_uri, model_name, image_name, image_description)