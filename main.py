from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from Forecasting import predict_pm25_next_3_days, predict_pm10_next_3_days, predict_O3_next_3_days, predict_NO2_next_3_days, predict_SO2_next_3_days
from Rural_Predection import calculate_pollutant_levels,calculate_levels_from_subindices,get_all_stations_data
import requests
from HealthAdvice import get_health_advice
import json
from geopy.distance import geodesic
from Mapping_services import get_nearby_hospitals
from History import calculate_daily_aqi_from_averages,get_monthly_aqi_from_averages

from redis_client import r
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
    genral_advice: str


class AQIForecastingRequest(BaseModel):
    lat: float
    lon: float
    PM25: float
    PM10: float
    NO2: float
    SO2: float
    O3: float


class AQIForecastingResponse(BaseModel):
    PM25_pred:List[float]
    PM10_pred:List[float]
    NO2_pred:List[float]
    SO2_pred:List[float]
    O3_pred:List[float]

# Caching function using redis

CACHE_RADIUS_KM = 10 
CACHE_TTL_SECONDS = 1800  

def is_within_radius(coord1, coord2, radius_km=3):
    return geodesic(coord1, coord2).km <= radius_km

def find_nearby_cached_key(lat, lon):
    all_keys = r.keys("rural_aqi:*")
    for key in all_keys:
        try:
            _, k_lat, k_lon = key.split(":")
            k_lat = float(k_lat)
            k_lon = float(k_lon)
            if is_within_radius((lat, lon), (k_lat, k_lon)):
                return key
        except:
            continue
    return None



    
# Endpoint to hit for rural AQI data

@app.post("/rural_aqi", response_model=RuralAQIResponse)
async def get_rural_aqi(request: RuralAQIRequest):

    lat = request.lat
    lon = request.lon

    cached_key = find_nearby_cached_key(lat, lon)
    if cached_key:
        cached_data = r.get(cached_key)
        if cached_data:
            print("Returning from cache.")
            return json.loads(cached_data)


   

   
    pollutant_levels = calculate_pollutant_levels(lat,lon)
    print(pollutant_levels)
  
    data = calculate_levels_from_subindices(subindices=pollutant_levels)
    dominant_pollutant = max(pollutant_levels, key=pollutant_levels.get)
    rural_aqi = pollutant_levels[dominant_pollutant]
   
    
    data_items = [
        dataResponseItem(key=k, value=v)
        for k, v in data.items()
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

    final_response = RuralAQIResponse(
        rural_aqi=rural_aqi,
        dominant_pollutant=dominant_pollutant,
        data=data_items
    )

    cache_key = f"rural_aqi:{lat}:{lon}"
    r.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(final_response.model_dump()))



    return final_response


@app.post("/aqi_forecasting", response_model=AQIForecastingResponse)
async def get_aqi_forecasting(request: AQIForecastingRequest):

    lat = request.lat
    lon = request.lon
    PM25 = request.PM25

    PM25_pred = predict_pm25_next_3_days(PM25, lat, lon)
    PM10_pred = predict_pm10_next_3_days(request.PM10, lat, lon)
    NO2_pred = predict_NO2_next_3_days(request.NO2, lat, lon)
    SO2_pred = predict_SO2_next_3_days(request.SO2, lat, lon)
    O3_pred = predict_O3_next_3_days(request.O3, lat, lon)


    return AQIForecastingResponse(PM25_pred=PM25_pred, PM10_pred=PM10_pred, NO2_pred=NO2_pred, SO2_pred=SO2_pred, O3_pred=O3_pred)

@app.post("/health_advice", response_model=HealthAdviceOutput)
async def get_health_advice_route(request: HealthAdviceRequest):

    res = get_health_advice(request)
    return res


@app.get("/getallstations")
async def get_all_stations():
    return get_all_stations_data()


@app.get("/getnearesthospitals")
async def get_nearest_hospitals(lat: float, lon: float):

    hospitals = get_nearby_hospitals(lat, lon, radius=20000)
    return hospitals


@app.get("/HistoryAQIData")
async def get_history_aqi_data(lat: float, lon: float):
    
    res = calculate_daily_aqi_from_averages(lat,lon)
    
    
    return res

@app.get("/HistoryAQIDataMonthly")
async def get_history_aqi_data_monthly(lat: float, lon: float):

    res = get_monthly_aqi_from_averages(lat,lon)
    return res



# Endpoint to get hospitals for area beyond a level 

# @app.get("/hospitals")
# async def get_nearest_hospitals(lat: float, lon: float):
#     get_nearest_hospital = 


# 

