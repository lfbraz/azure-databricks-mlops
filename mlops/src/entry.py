%%writefile /dbfs/models/churn-prediction/score.py

import mlflow
import json
import pandas as pd
import os
import xgboost as xgb
import time

# Called when the deployed service starts
def init():
    global model
    global train_stats

    # Get the path where the deployed model can be found.
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), './churn-prediction')
    
    # Load model
    model = mlflow.xgboost.load_model(model_path)

# Handle requests to the service
def run(data):
  
  info = {"payload": data}
  print(json.dumps(info))
    
  data = pd.read_json(data, orient = 'split')
  data_xgb = xgb.DMatrix(data)

  # Return the prediction
  prediction = predict(data_xgb)
  print ("Prediction created at: " + time.strftime("%H:%M:%S"))
  
  return prediction

def predict(data):
  prediction = model.predict(data)[0]
  return {"churn-prediction": str(int(prediction))}