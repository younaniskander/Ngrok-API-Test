import os
import sys
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import time
import joblib

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline import EMGPipeline

pipeline = EMGPipeline()
model = None

# Pydantic schemas for request and response validation
class EMGWindowRequest(BaseModel):
    emg_window: List[List[float]] = Field(
        ..., 
        description="A list of lists containing raw EMG channel values. Shape must be (N_samples, 4) where N_samples >= 200.",
        example=[[0.0] * 4] * 200
    )

class PredictionResponse(BaseModel):
    predicted_knee_angle: float = Field(..., description="The mapped right knee angle in degrees.")
    angle_category: str = Field(..., description="The categorized range of the angle: '0-30', '30-60', or '60-90'.")
    raw_ml_prediction: float = Field(..., description="The original raw prediction from the ML model.")
    latency_ms: float = Field(..., description="The internal processing and inference latency in milliseconds.")
    features_extracted: dict = Field(..., description="A subset of the extracted feature values for verification.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events, loading the PyCaret model."""
    global model
    model_path = os.path.join(os.path.dirname(__file__), 'emg_pipeline.pkl')
    print(f"Loading regression model from '{model_path}'...")
    
    try:
        # Load the pipeline
        bundle = joblib.load(model_path)
        if isinstance(bundle, dict) and "model" in bundle:
            model = bundle
            print("Model loaded successfully (sklearn bundle)!")
        else:
            from pycaret.regression import load_model
            base_name = os.path.join(os.path.dirname(__file__), 'emg_pipeline')
            model = load_model(base_name)
            print("Model loaded successfully (PyCaret)!")
    except Exception as e:
        print(f"CRITICAL: Failed to load model. Please run 'train_model.py' first. Error: {e}")
    yield
    print("Shutting down API server...")

# Initialize FastAPI App
app = FastAPI(
    title="SEMG_DB1 Exoskeleton Control API",
    description="Categorized joint angle prediction utilizing 4-channel EMG signals.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    status = "OK"
    if model is None:
        status = "DEGRADED - Model not loaded"
    return {"status": status}

@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict_joint_angle(request: EMGWindowRequest):
    start_time = time.perf_counter()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Prediction service unavailable: Model not loaded.")
    
    raw_data = np.array(request.emg_window)
    
    # 4 channels!
    if len(raw_data.shape) != 2 or raw_data.shape[1] != 4:
        raise HTTPException(status_code=422, detail=f"Invalid data shape. Expected (N_samples, 4). Got {raw_data.shape}")
        
    if raw_data.shape[0] < 200:
        raise HTTPException(status_code=422, detail=f"EMG window too short. Got {raw_data.shape[0]}")
        
    try:
        dsp_results = pipeline.process_raw_emg(raw_data)
        features = dsp_results['features']
        
        if features is None or features.size == 0:
            raise ValueError("DSP pipeline failed to extract features.")
            
        features_vector = features[-1, :]
        feature_names = pipeline.get_feature_names()
        features_df = pd.DataFrame([features_vector], columns=feature_names)
        
        if isinstance(model, dict) and "model" in model:
            X = model["scaler"].transform(features_df[model["feature_names"]].values)
            predicted_angle = float(model["model"].predict(X)[0])
        else:
            from pycaret.regression import predict_model
            predictions_df = predict_model(model, data=features_df)
            predicted_angle = float(predictions_df['prediction_label'].iloc[0])
            
        # -------------------------------------------------------------
        # Categorization Logic
        # -------------------------------------------------------------
        mapped_angle = predicted_angle
        category = "0-30"
        
        if predicted_angle <= 30:
            mapped_angle = max(0.0, min(30.0, predicted_angle))
            category = "0-30"
        elif predicted_angle <= 60:
            mapped_angle = max(30.0, min(60.0, predicted_angle))
            category = "30-60"
        else:
            mapped_angle = max(60.0, min(90.0, predicted_angle))
            category = "60-90"
            
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000.0
        
        sample_features = {
            "RF_mav": float(features_df["RF_mav"].iloc[0]) if "RF_mav" in features_df else 0.0,
            "ST_rms": float(features_df["ST_rms"].iloc[0]) if "ST_rms" in features_df else 0.0,
        }
        
        return PredictionResponse(
            predicted_knee_angle=mapped_angle,
            angle_category=category,
            raw_ml_prediction=predicted_angle,
            latency_ms=latency_ms,
            features_extracted=sample_features
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")

if __name__ == '__main__':
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting test suite server on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, reload=False)
