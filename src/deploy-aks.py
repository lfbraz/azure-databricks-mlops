# Databricks notebook source
# MAGIC %run /Shared/utils

# COMMAND ----------

# Experiment parameters
experiment_name = '/churn-prediction'
run_name = 'mlops-train'

model_name = 'churn-model'

# Workspace parameters
workspace_name = dbutils.secrets.get(scope = "azure-key-vault", key = "workspace-name")
workspace_location = dbutils.secrets.get(scope = "azure-key-vault", key = "location")
resource_group = dbutils.secrets.get(scope = "azure-key-vault", key = "resource-group")
subscription_id = dbutils.secrets.get(scope = "azure-key-vault", key = "subscription-id")

# Prod instance parameters
endpoint_name_prod = 'api-churn-prod'
aks_target = 'aks-cluster-1'

model_uri = get_model_uri(experiment_name, run_name)
workspace = get_workspace(workspace_name, workspace_location, resource_group, subscription_id)

deploy_aks(workspace, model_uri, endpoint_name_prod, model_name, aks_target)