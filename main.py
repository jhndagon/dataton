from fastapi import FastAPI

from src.schema.predict import PredictRequest, PredictResponse

app = FastAPI()





@app.post(
    '/predict',
    response_model=PredictResponse
)
async def predict(
    body: PredictRequest
):
    return PredictResponse(
        length=26,
        width=27,
        height=29,
        n_boxes=3
    )