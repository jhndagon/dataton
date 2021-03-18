from pydantic import BaseModel


class PredictRequest(BaseModel):
    weight: float
    volume: float
    

class PredictResponse(BaseModel):
    length: float
    height: float
    width: float
    n_boxes: int