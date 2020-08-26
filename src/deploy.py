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

# Dev instance parameters
endpoint_name_dev = 'api-churn-dev'

workspace = get_workspace(workspace_name, workspace_location, resource_group, subscription_id)

deploy_aci(workspace, endpoint_name_dev, image_name)
print('done')