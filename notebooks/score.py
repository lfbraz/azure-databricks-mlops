# Databricks notebook source
# MAGIC %run ./utils

# COMMAND ----------

from mlflow.tracking.client import MlflowClient

client = MlflowClient()
model_name = 'churn-model'

model = client.search_model_versions(f"name='{model_name}'")[0]

# COMMAND ----------

loaded_model = mlflow.pyfunc.spark_udf(spark, model_uri=f'runs:/{model.run_id}/model')

dataset = get_dataset('/dbfs/Dataset/Customer')
dataset, numeric_columns = preprocessing(dataset)
train_dataset, test_dataset = split_dataset(dataset, 2022)
X_train, X_test, y_train, y_test = get_X_y(train_dataset, test_dataset, 'Churn', numeric_columns, ['Churn', 'CodigoCliente'])

prediction_df = spark.createDataFrame(data = X_test)

# COMMAND ----------

columns = list(prediction_df.columns)
prediction_df = spark.createDataFrame(prediction_df.withColumn('predictions', loaded_model(*columns)).collect())

# COMMAND ----------

prediction_df.write.format("delta").saveAsTable("Prod.ChurnPredictions")
