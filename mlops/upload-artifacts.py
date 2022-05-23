import mlflow

mlflow.tracking.set_tracking_uri('databricks')

experiment_name = '/churn-prediction'

if(not(mlflow.get_experiment_by_name(experiment_name))):
  mlflow.create_experiment(experiment_name)

mlflow.set_experiment(experiment_name)

model_path = './Model'
with mlflow.start_run():
    mlflow.log_artifacts(model_path, artifact_path="model")
