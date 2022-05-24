# Databricks notebook source
# MAGIC %run ./utils

# COMMAND ----------

model_name = 'churn-model'
stage = 'Production'
transition_model(model_name, stage)
