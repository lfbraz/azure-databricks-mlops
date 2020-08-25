# Databricks notebook source
# MAGIC %run /Shared/utils

# COMMAND ----------

# Workspace parameters
workspace_name = 'wp-ml-db'
workspace_location = 'East US 2'
resource_group = 'RG-Databricks'
subscription_id = 'f56912be-98e5-44e3-9e64-54bc52cef4a7'

# Image parameters
image_name = 'churn-model-image'

# Prod instance parameters
endpoint_name_prod = 'api-churn-prod'
aks_target = 'aks-cluster-1'

workspace = get_workspace(workspace_name, workspace_location, resource_group, subscription_id)

deploy_aks(workspace, endpoint_name_prod, image_name, aks_target)