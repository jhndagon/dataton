from typing import List
from pydantic import BaseModel


class PredictRequest(BaseModel):
    weight: str
    volume: str
    

class Predict(BaseModel):
    length: float
    height: float
    width: float
    n_boxes: int
    error: float
    mape: float = 0
    

class PredictResponse(BaseModel):
    predict: List[Predict]
    volume_error: float
    mape: float = 0