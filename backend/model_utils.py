# model_utils.py
import os
import joblib

def load_model(path):
    """Load the sklearn model from path (joblib)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found at {path}")
    model = joblib.load(path)
    return model

def predict_with_model(model, feature_dict):
    """
    Expects feature_dict containing numeric values for the model features.
    Convert to list in the right order expected by your model.
    If you trained model with these features: 
      ['Total_Usage_kWh','month','is_winter','prev_CO2','renewable_share']
    adjust the order below to match your training.
    """
    # Order used in training (adjust if different)
    order = ["Total_Usage_kWh", "month", "is_winter", "prev_CO2", "renewable_share"]
    x = [float(feature_dict.get(k, 0)) for k in order]
    # model.predict expects 2D array
    yhat = model.predict([x])
    # return first value
    return float(yhat[0])
