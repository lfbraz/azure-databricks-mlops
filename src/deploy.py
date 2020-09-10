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

# Dev instance parameters
endpoint_name_dev = 'api-churn-dev'

workspace = get_workspace(workspace_name, workspace_location, resource_group, subscription_id)

deploy_aci(workspace, endpoint_name_dev, image_name)
print('done')