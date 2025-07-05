from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import core.model_trainer
import core.data_holder
from core.models.multiple_linear_regression import MultipleLinearRegressionModel
from core.data_manager import DataManager, DataType

app = FastAPI(
    title="Football Prediction API",
    description="API for football match predictions using statistical learning",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para requests
class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    date: str  # formato: DD/MM/YY

class PredictionResponse(BaseModel):
    predicted_home_goals: float
    predicted_away_goals: float
    actual_home_goals: Optional[int] = None
    actual_away_goals: Optional[int] = None
    prediction_date: str
    teams: Dict[str, str]

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "Football Prediction API",
        "status": "running",
        "model_loaded": core.model_trainer.model_instance is not None,
        "data_available": core.data_holder.PROCESSED_DATA_JSON != '{"error": "No processed data found."}',
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "test_data": "/test-data",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    model_status = "loaded" if core.model_trainer.model_instance else "not_loaded"
    data_status = "available" if core.data_holder.PROCESSED_DATA_JSON != '{"error": "No processed data found."}' else "not_available"
    
    return {
        "status": "healthy",
        "model_status": model_status,
        "data_status": data_status,
        "test_data_status": "available" if core.data_holder.TEST_DATA_JSON != '{"error": "No test data found."}' else "not_available"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_match(request: PredictionRequest):
    if not core.model_trainer.model_instance:
        raise HTTPException(
            status_code=503, 
            detail="Prediction model is not available. Please load a model first."
        )
    
    try:
        # Llamar al mismo método que usa pywebview
        pred_h, pred_a, real_h, real_a = core.model_trainer.model_instance.predict(
            request.home_team, 
            request.away_team, 
            request.date
        )
        
        if pred_h is None or pred_a is None:
            raise HTTPException(
                status_code=404,
                detail=f"Could not generate prediction for {request.home_team} vs {request.away_team} on {request.date}. No history available for these teams."
            )
        
        response = PredictionResponse(
            predicted_home_goals=float(pred_h),
            predicted_away_goals=float(pred_a),
            prediction_date=request.date,
            teams={
                "home": request.home_team,
                "away": request.away_team
            }
        )
        
        # Agregar resultados reales si están disponibles
        if real_h is not None and real_a is not None:
            response.actual_home_goals = int(real_h)
            response.actual_away_goals = int(real_a)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction_error: {str(e)}"
        )

@app.get("/test-data")
async def get_test_data():
    """Obtener datos de prueba usando los mismos datos que la GUI"""
    try:
        if core.data_holder.TEST_DATA_JSON == '{"error": "No test data found."}':
            raise HTTPException(
                status_code=404,
                detail="Test data not available"
            )
        
        import json
        data = json.loads(core.data_holder.TEST_DATA_JSON)
        return {
            "count": len(data) if isinstance(data, list) else 1,
            "data": data[:10] if isinstance(data, list) else data  # Solo primeros 10
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving test data: {str(e)}"
        )

@app.get("/processed-data")
async def get_processed_data():
    """Obtener datos procesados usando los mismos datos que la GUI"""
    try:
        if core.data_holder.PROCESSED_DATA_JSON == '{"error": "No processed data found."}':
            raise HTTPException(
                status_code=404,
                detail="Processed data not available"
            )
        
        import json
        data = json.loads(core.data_holder.PROCESSED_DATA_JSON)
        return {
            "count": len(data) if isinstance(data, list) else 1,
            "data": data[:10] if isinstance(data, list) else data  # Solo primeros 10
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving processed data: {str(e)}"
        )

def start_api_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Iniciar el servidor de la API"""
    print(f"Starting FastAPI server on http://{host}:{port}")
    print(f"API Documentation available at: http://{host}:{port}/docs")
    print(f"Alternative docs available at: http://{host}:{port}/redoc")
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    start_api_server()
