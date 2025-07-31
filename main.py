from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from Forecasting import predict_pm25, predict_pm10, predict_O3, predict_NO2, predict_SO2
from Rural_Predection import calculate_pollutant_levels,calculate_indian_aqi
import requests
from HealthAdvice import get_health_advice
url = "https://api.open-meteo.com/v1/forecast"


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class dataResponseItem(BaseModel):
    key: str
    value: float

class RuralAQIRequest(BaseModel):
    lat:float
    lon:float


class RuralAQIResponse(BaseModel):
    rural_aqi: float
    dominant_pollutant: str
    data: List[dataResponseItem]


class HealthAdviceRequest(BaseModel):
    rural_aqi: float
    dominant_pollutant: str
    data: List[dataResponseItem]

class HealthAdviceOutput(BaseModel):
    general_overview: str
    childeren_advice: str
    elderly_advice: str
    adult_advice: str


class AQIForecastingRequest(BaseModel):
    lat: float
    lon: float
    PM25: float
    PM10: float
    NO2: float
    SO2: float
    O3: float


class AQIForecastingResponse(BaseModel):
    PM25_pred:float
    PM10_pred:float
    NO2_pred:float
    SO2_pred:float
    O3_pred:float


    
# Endpoint to hit for rural AQI data

@app.post("/rural_aqi", response_model=RuralAQIResponse)
async def get_rural_aqi(request: RuralAQIRequest):

    lat = request.lat
    lon = request.lon

   

   
    pollutant_levels = calculate_pollutant_levels(lat,lon)
    data = calculate_indian_aqi(lat,lon,pollutants=pollutant_levels)
   
    
    data_items = [
        dataResponseItem(key=k, value=v)
        for k, v in pollutant_levels.items()
    ]

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m,relative_humidity_2m,surface_pressure,cloud_cover,precipitation_probability",
    }
    response = requests.get(url, params=params)
    weather_data = response.json()
    result = {}
    result["temperature"] = weather_data.get("current", {}).get("temperature_2m")
    result["wind_speed"] = weather_data.get("current", {}).get("wind_speed_10m")
    result["wind_direction"] = weather_data.get("current", {}).get("wind_direction_10m")
    result["relative_humidity"] = weather_data.get("current", {}).get("relative_humidity_2m")
    result["surface_pressure"] = weather_data.get("current", {}).get("surface_pressure")
    result["cloud_cover"] = weather_data.get("current", {}).get("cloud_cover")
    result["precipitation_probability"] = weather_data.get("current", {}).get("precipitation_probability")

    data_items += [
        dataResponseItem(key=k, value=v)
        for k, v in result.items()
    ]



    return RuralAQIResponse(
        rural_aqi=data["overall_aqi"], 
        dominant_pollutant=data["dominant_pollutant"],
        data=data_items
    )


@app.post("/aqi_forecasting", response_model=AQIForecastingResponse)
async def get_aqi_forecasting(request: AQIForecastingRequest):

    lat = request.lat
    lon = request.lon
    PM25 = request.PM25

    PM25_pred = predict_pm25(PM25, lat, lon)
    PM10_pred = predict_pm10(request.PM10, lat, lon)
    NO2_pred = predict_NO2(request.NO2, lat, lon)
    SO2_pred = predict_SO2(request.SO2, lat, lon)
    O3_pred = predict_O3(request.O3, lat, lon)

    

    return AQIForecastingResponse(PM25_pred=PM25_pred, PM10_pred=PM10_pred, NO2_pred=NO2_pred, SO2_pred=SO2_pred, O3_pred=O3_pred)

@app.post("/health_advice", response_model=HealthAdviceOutput)
async def get_health_advice_route(request: HealthAdviceRequest):

    res = get_health_advice(request)
    return res


