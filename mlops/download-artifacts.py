import mlflow
import os
from mlflow.tracking.client import MlflowClient

mlflow.tracking.set_tracking_uri('databricks')

client = MlflowClient()
model_name='churn-model'
model_path = 'Model'

if not os.path.exists(model_path):
    os.mkdir(model_path)

model = client.search_model_versions(f"name='{model_name}'")[0]
local_path = client.download_artifacts(model.run_id, 'model', model_path)
print(f'Model {model_name} saved at {local_path}')
