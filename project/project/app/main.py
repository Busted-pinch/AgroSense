from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import os, joblib
from dotenv import load_dotenv
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np


# ==============================
# Model Loading
# ==============================
# Load all models once at application startup to improve performance
def encode_input(value, column, encoders):
    if value not in encoders[column]:
        raise ValueError(f"Unknown category '{value}' for column '{column}'")
    return encoders[column].index(value)
def decode_output(value,column, decoders):
    categories=decoders[column]
    if value<0 or value>len(categories):
        raise ValueError(f"Unknown category code '{value}' for column '{column}'")
    return categories[value]
try:
    load_dotenv()
    Yield_model_path = os.getenv("Yield_model", "models/Yield_model.pkl")
    Yield_model_artifacts = joblib.load(Yield_model_path)
    Yield_model=Yield_model_artifacts["Yield_model"]
    Yield_input_categories =Yield_model_artifacts["Yield_categories"]

    Best_time_path = os.getenv("Best_time", "models/Best_time.pkl")
    Best_time_artifacts = joblib.load(Best_time_path)
    Best_time_model = Best_time_artifacts["Best_time_model"]
    Best_time_input_categories = Best_time_artifacts["Best_time_input_categories"]
    Best_time_output_encoders=Best_time_artifacts["Best_time_output_encoders"]

    Soil_model_path = os.getenv("Soil_model", "models/Soil_model.pkl")
    Soil_model_artifacts = joblib.load(Soil_model_path)
    Soil_model= Soil_model_artifacts["Soil_model"]
    Soil_input_categories =Soil_model_artifacts["Soil_categories"]
    

except FileNotFoundError as e:
    print(f"Warning: Model file not found. Prediction functionality may be limited. Error: {e}")
    Yield_model, Best_time_model, Soil_model = None, None, None
    Yield_input_categories,Best_time_output_encoders,Best_time_input_categories,Soil_input_encoders= None, None, None, None

# Import all routers
# NOTE: This assumes the routers are correctly structured in the app/routers directory
from app.routers import (
    auth,
    market,
    guidelines,
    voice_input,
    image_processing,
)

app = FastAPI(title="AgroSense - Unified Backend")

# ==============================
# CORS setup
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Routers
# ==============================
app.include_router(auth.router)
app.include_router(market.router, prefix="/market", tags=["Market"])
app.include_router(guidelines.router, prefix="/guidelines", tags=["Guidelines"])
app.include_router(voice_input.router, prefix="/voice", tags=["Voice Input"])
app.include_router(image_processing.router, prefix="/image", tags=["Image Processing"])

# ==============================
# Models
# ==============================
class PredictionRequest(BaseModel):
    crop: str
    state: str
    area: float              # hectares
    fertilizer_used: float   # kg/hectare

class GPSRequest(BaseModel):
    lat: float
    lon: float

class SoilRequest(BaseModel):
    soil_type: str
    location: str
    has_npk: bool
    N_ppm: Optional[float] = None
    P_ppm: Optional[float] = None
    K_ppm: Optional[float] = None

# ==============================
# Yield Prediction Logic
# ==============================
def predict_yield(crop: str, state: str, area: float, fertilizer_used: float):
    if Yield_model is None:
        raise RuntimeError("Yield prediction model not loaded.")

    # Normalize
    crop = crop.capitalize()       # "rice" -> "Rice"
    state = state.title()          # "maharashtra" -> "Maharashtra"

    # Encode
    x_reg_input = pd.DataFrame([[
        encode_input(crop, "Crop", Yield_input_categories),
        encode_input(state, "State", Yield_input_categories),
        fertilizer_used
    ]], columns=["Crop", "State", "Fertilizer"])
    y_reg_pred=Yield_model.predict(x_reg_input)
    # Assuming the model returns yield_per_ha and optimum_fertilizer
    yield_per_ha, optimum_fertilizer = y_reg_pred[0]
    
    # Calculate predicted yield based on area and fertilizer used
    if fertilizer_used == 0:
        predicted_yield = 0.6 * yield_per_ha * area
    else:
        predicted_yield = yield_per_ha * area

    # Use max() to ensure extra_fertilizer is never negative
    extra_fertilizer = max(0, optimum_fertilizer - fertilizer_used)
    
    # Call the best_time prediction function
    best_time_name= predict_best_time(crop, state)
    
    return {
        "yield_tons": round(predicted_yield, 2),
        "extra_needed_fertilizer_per_ha": round(extra_fertilizer, 2),
        "best_time": best_time_name,
    }

# ==============================
# Best Time setup
# ==============================
def predict_best_time(crop:str,state:str):
    if Best_time_model is None:
        raise RuntimeError("Best time prediction model not loaded.")
    
    crop_code=encode_input(crop,"Crop", Best_time_input_categories)
    state_code=encode_input(state,"State",Best_time_input_categories)
    x_cls_input=pd.DataFrame([[crop_code,state_code]], columns=["Crop","State"])
    y_cls_pred_codes = Best_time_model.predict(x_cls_input)[0]
    Best_time_name=decode_output(y_cls_pred_codes, "Best_time",Best_time_output_encoders)
    return Best_time_name
    
# ==============================
# Soil Health Logic
# ==============================
def Soil_nutrient_predict(state: str, soil_type: str):
    x_reg_input = pd.DataFrame([[
    encode_input(soil_type, "Soil_Type", Soil_input_categories),
    encode_input(state, "State", Soil_input_categories)]],columns=["Soil_Type","State"])
    y_reg_pred=Soil_model.predict(x_reg_input)
    return y_reg_pred


def calculate_soil_requirements(N_ppm: float, P_ppm: float, K_ppm: float):
    needed_N = (max(0, (150 - N_ppm)) * 1.95) / 0.50
    needed_P = (max(0, (15 - P_ppm)) * 1.95) / 0.30
    needed_K = (max(0, (200 - K_ppm)) * 1.95) / 0.60
    
    norm_N = (N_ppm - 50) / 150
    norm_P = (P_ppm - 5) / 15
    norm_K = (K_ppm - 50) / 200

    average = (norm_N + norm_P + norm_K) / 3
    SHI = average * 100
    
    return {
        "SHI": round(SHI, 2),
        "Needed_N_Fertilizer": round(needed_N, 2),
        "Needed_P_Fertilizer": round(needed_P, 2),
        "Needed_K_Fertilizer": round(needed_K, 2),
    }
 

# ==============================
# Endpoints
# ==============================
@app.post("/predict-yield", tags=["Yield Prediction"])
def get_yield_prediction(request: PredictionRequest):
    try:
        result = predict_yield(request.crop, request.state, request.area, request.fertilizer_used)
        return {
            "crop": request.crop,
            "state": request.state,
            "area_ha": request.area,
            "fertilizer_used_kg_per_ha": request.fertilizer_used,
            "yield_metric_tons": result["yield_tons"],
            "extra_needed_fertilizer_kg_per_ha": result["extra_needed_fertilizer_per_ha"],
            "best_time": result["best_time"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-state", tags=["GPS to State"])
def get_state_from_gps(request: GPSRequest):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={request.lat}&lon={request.lon}&format=json"
        response = requests.get(url, headers={"User-Agent": "agrosense-app"})
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch location")
        data = response.json()
        state = data.get("address", {}).get("state", "Unknown")
        return {"lat": request.lat, "lon": request.lon, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import HTTPException

@app.post("/soil-health", tags=["Soil Health"])
def get_soil_health(request: SoilRequest):
    try:
        # ==============================
        # Case 1: Farmer has NPK values
        # ==============================
        if request.has_npk:
            if request.N_ppm is None or request.P_ppm is None or request.K_ppm is None:
                raise HTTPException(
                    status_code=400,
                    detail="N, P, K values must be provided when has_npk=True"
                )
            N, P, K = request.N_ppm, request.P_ppm, request.K_ppm
            used_from_farmer = True

        # ========================================
        # Case 2: Farmer does NOT have NPK values
        # ========================================
        else:
            try:
                # Predict using the Soil model
                y_pred = Soil_nutrient_predict(request.location, request.soil_type)[0]
                N, P, K = y_pred[0], y_pred[1], y_pred[2]
                used_from_farmer = False
            except KeyError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown category provided: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error predicting NPK values: {str(e)}"
                )

        # ========================================
        # Calculate soil requirements & SHI
        # ========================================
        result = calculate_soil_requirements(N, P, K)

        return {
            "soil_type": request.soil_type,
            "location": request.location,
            "used_NPK_from_farmer": used_from_farmer,
            "N_ppm": round(N, 2),
            "P_ppm": round(P, 2),
            "K_ppm": round(K, 2),
            **result
        }

    except HTTPException as e:
        # Re-raise known HTTP exceptions
        raise e
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Root endpoint
# ==============================
@app.get("/")
def root():
    return {"message": "AgroSense Unified Backend is running 🚀"}
