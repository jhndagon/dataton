from typing import Dict, List
import requests
from fastapi import FastAPI, HTTPException, status
from fastapi.datastructures import UploadFile
from fastapi.params import File
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

from src.schema.predict import PredictRequest, PredictResponse, Predict

from src.processor.similarity import get_cosine

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/predict/file"
)
async def predict_file(
    file: UploadFile = File(...)
):
    extention = file.filename.split('.')[1]
    file_data = file.file.read()
    if extention == "csv":
        file_read = pd.read_csv(file_data)
    elif extention == 'xlsx' or extention == 'xls':
        file_read = pd.read_excel(file_data)
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='The file does not have an appropriate extension')

    columns = file_read.columns
    weight = []
    volume = []
    for column in columns:
        if get_cosine(column, "Weight") >= 0.75:
            weight = file_read[column].to_list()
        elif get_cosine(column, "Cubic Feet") >= 0.75:
            volume = file_read[column].to_list()
    
    if not weight or not volume:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='The fields do not have the same quantity of rows')
    
    data =  [
        Predict(
            **requests.post("http://34.74.44.189:8978/predict", json={
                "weight": weig,
                "volume": vol
            }).json()
        )
        for vol, weig in zip(weight, volume)
    ]
    data_ = list(map(lambda x: x.dict(), data))
    data_df = pd.DataFrame(data_)
    
    length = abs(file_read['Length'] - data_df['length'])  /  file_read['Length']
    width = abs(file_read['Width'] - data_df['width'])  /  file_read['Width']
    height = abs(file_read['Height'] - data_df['height'])  /  file_read['Height']
        
    data_df["mape"] = 100 *  (length + width + height) / 3     
    
    
    mape = data_df["mape"].sum() / len(data_df["mape"])
    error_pond = sum(list(map(lambda x: x.error, data))) / len(data)
    
    return PredictResponse(predict=data, volume_error=error_pond, mape=mape)
                


@app.post(
    '/predict',
    response_model=PredictResponse
)
async def predict(
    body: PredictRequest
):
    weights = body.weight.split(',')
    volumes = body.volume.split(',')
    
    weights = map(lambda weight: float(weight), weights)
    volumes = map(lambda volume: float(volume), volumes)
        
    data =  [
        Predict(
            **requests.post("http://34.74.44.189:8978/predict", json={
                "weight": weight,
                "volume": volume
            }).json()
        )
        for weight, volume in zip(weights, volumes)
    ]
    
    error_pond = sum(list(map(lambda x: x.error, data))) / len(data)
    
    return PredictResponse(predict=data, volume_error=error_pond)


