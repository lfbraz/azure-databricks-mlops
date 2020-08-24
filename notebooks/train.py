# Databricks notebook source
# MAGIC %run /Shared/utils

# COMMAND ----------

SEED = 2020
TARGET = 'Churn'

drop_columns = [TARGET, 'CodigoCliente']

# Get the Train Dataset
dataset = get_dataset('dados_clientes.csv')

# Preprocessing Features
dataset, numeric_columns = preprocessing(dataset)

# Split train and test
train_dataset, test_dataset = split_dataset(dataset, SEED)

# Get X, y
X_train, X_test, y_train, y_test = get_X_y(train_dataset, test_dataset, TARGET, numeric_columns, drop_columns)

# Train model
model_uri = train_model(X_train, y_train, 20, SEED)
print(f'model_uri: {model_uri}')