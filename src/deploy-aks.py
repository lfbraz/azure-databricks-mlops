# Databricks notebook source
# MAGIC %run /Shared/utils

# COMMAND ----------

# Workspace parameters
workspace_name = dbutils.secrets.get(scope = "azure-key-vault", key = "workspace-name")
workspace_location = dbutils.secrets.get(scope = "azure-key-vault", key = "location")
resource_group = dbutils.secrets.get(scope = "azure-key-vault", key = "resource-group")
subscription_id = dbutils.secrets.get(scope = "azure-key-vault", key = "subscription-id")

# Image parameters
image_name = 'churn-model-image'

# Prod instance parameters
endpoint_name_prod = 'api-churn-prod'
aks_target = 'aks-cluster-1'

workspace = get_workspace(workspace_name, workspace_location, resource_group, subscription_id)

deploy_aks(workspace, endpoint_name_prod, image_name, aks_target)