from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PneumoniaPredictionResponse(BaseModel):
    prediction: str
    confidence: float
    probability_normal: float
    probability_pneumonia: float


