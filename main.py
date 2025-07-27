from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from Rural_Predection import calculate_ruralAQI,calculate_pollutant_levels
import requests
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
    data: List[dataResponseItem]


class HealthAdviceRequest(BaseModel):
    rural_aqi: float
    data: List[dataResponseItem]

class HealthAdviceResponse(BaseModel):
    advice: str
    precautions: List[str]


    
# Endpoint to hit for rural AQI data

@app.post("/rural_aqi", response_model=RuralAQIResponse)
async def get_rural_aqi(request: RuralAQIRequest):

    lat = request.lat
    lon = request.lon

    print(f"Received request for coordinates: lat={lat}, lon={lon}")

    rural_aqi  = calculate_ruralAQI(lat=lat,lon=lon)
    pollutant_levels = calculate_pollutant_levels(lat,lon)
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
        rural_aqi=rural_aqi,  
        data=data_items
    )



@app.post("/health_advice", response_model=HealthAdviceResponse)
async def get_health_advice(request: HealthAdviceRequest):
    current_aqi = request.rural_aqi
    data = request.data

    return HealthAdviceResponse(
        advice="The air quality is good. You can go outside without any concerns.",
        precautions=[
            "Enjoy outdoor activities.",
            "No need for masks or special precautions."
        ]
    )


