from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PneumoniaPredictionResponse(BaseModel):
    prediction: str
    confidence: float
    probability_normal: float
    probability_pneumonia: float

class AiAnalysisResultResponse(BaseModel):
    id: int
    record_id: int
    is_pneumonia: bool
    confidence: float
    heatmap_url: str
    ai_model: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
