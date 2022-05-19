# Databricks notebook source
# MAGIC %run ./utils

# COMMAND ----------

experiment_name = '/churn-prediction'
run_name = 'mlops-train'
model_name = 'churn-model'

result = register_model(experiment_name, run_name, model_name)
print(result)
