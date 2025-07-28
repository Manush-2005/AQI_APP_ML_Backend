import xgboost as xgb
import pandas as pd
import requests

model = xgb.XGBRegressor()
model.load_model("PM25Model.json")

FEATURE_ORDER = [
    "PM2.5",
    "temperature",
    "humidity",
    "wind_speed",
    "wind_direction",
    "temperature_t+1",
    "humidity_t+1",
    "wind_speed_t+1",
    "wind_direction_t+1"
]

url = "https://api.open-meteo.com/v1/forecast"

def get_weather_features(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wind_speed_10m,wind_direction_10m,relative_humidity_2m,temperature_2m,precipitation,surface_pressure",
        "daily": "shortwave_radiation_sum",
    }
    response = requests.get(url, params=params)
    weather_data = response.json()
    

    result = {
        
        "wind_speed": weather_data.get("current", {}).get("wind_speed_10m"),
        "wind_direction": weather_data.get("current", {}).get("wind_direction_10m"),
        "relative_humidity": weather_data.get("current", {}).get("relative_humidity_2m"),
        "temperature": weather_data.get("current", {}).get("temperature_2m"),
        "precipitation": weather_data.get("current", {}).get("precipitation"),
        "surface_pressure": weather_data.get("current", {}).get("surface_pressure"),
        "shortwave_radiation_sum": weather_data.get("daily", {}).get("shortwave_radiation_sum", [None])[0]
    }
    return result

def get_forecasted_features(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_mean,relative_humidity_2m_mean,wind_speed_10m_mean,winddirection_10m_dominant,precipitation_sum,shortwave_radiation_sum,surface_pressure_mean",
        "forecast_days": 3
    }
    response = requests.get(url, params=params)
    weather_data = response.json()
   

    daily = weather_data.get("daily", {})
    result = {
        "temperature": daily.get("temperature_2m_mean", [None, None])[1],
        "relative_humidity": daily.get("relative_humidity_2m_mean", [None, None])[1],
        "wind_speed": daily.get("wind_speed_10m_mean", [None, None])[1],
        "wind_direction": daily.get("winddirection_10m_dominant", [None, None])[1],
        "precipitation": daily.get("precipitation_sum", [None, None])[1],
        "shortwave_radiation_sum": daily.get("shortwave_radiation_sum",
            [None, None])[1],
        "surface_pressure": daily.get("surface_pressure_mean", [None, None])[1]
    }
    return result



def predict_pm25(PM25:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)

    input_features = {

        "PM2.5": PM25,
        "temperature": weather_features["temperature"],
        "humidity": weather_features["relative_humidity"],
        "wind_speed": weather_features["wind_speed"],
        "wind_direction": weather_features["wind_direction"],
        "temperature_t+1": forecasted_features["temperature"],
        "humidity_t+1": forecasted_features["relative_humidity"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "wind_direction_t+1": forecasted_features["wind_direction"]
    }
    print(input_features)
    
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER]], columns=FEATURE_ORDER)

   
    prediction = model.predict(input_df)
    return round(prediction[0])


def predict_pm10(PM25:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)

    input_features = {

        "PM2.5": PM25,
        "temperature": weather_features["temperature"],
        "humidity": weather_features["relative_humidity"],
        "wind_speed": weather_features["wind_speed"],
        "wind_direction": weather_features["wind_direction"],
        "temperature_t+1": forecasted_features["temperature"],
        "humidity_t+1": forecasted_features["relative_humidity"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "wind_direction_t+1": forecasted_features["wind_direction"]
    }
    print(input_features)
    
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER]], columns=FEATURE_ORDER)

   
    prediction = model.predict(input_df)
    return round(prediction[0])


def predict_NO2(PM25:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)

    input_features = {

        "PM2.5": PM25,
        "temperature": weather_features["temperature"],
        "humidity": weather_features["relative_humidity"],
        "wind_speed": weather_features["wind_speed"],
        "wind_direction": weather_features["wind_direction"],
        "temperature_t+1": forecasted_features["temperature"],
        "humidity_t+1": forecasted_features["relative_humidity"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "wind_direction_t+1": forecasted_features["wind_direction"]
    }
    print(input_features)
    
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER]], columns=FEATURE_ORDER)

   
    prediction = model.predict(input_df)
    return round(prediction[0])


def predict_SO2(PM25:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)

    input_features = {

        "PM2.5": PM25,
        "temperature": weather_features["temperature"],
        "humidity": weather_features["relative_humidity"],
        "wind_speed": weather_features["wind_speed"],
        "wind_direction": weather_features["wind_direction"],
        "temperature_t+1": forecasted_features["temperature"],
        "humidity_t+1": forecasted_features["relative_humidity"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "wind_direction_t+1": forecasted_features["wind_direction"]
    }
    print(input_features)
    
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER]], columns=FEATURE_ORDER)

   
    prediction = model.predict(input_df)
    return round(prediction[0])


def predict_O3(PM25:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)

    input_features = {

        "PM2.5": PM25,
        "temperature": weather_features["temperature"],
        "humidity": weather_features["relative_humidity"],
        "wind_speed": weather_features["wind_speed"],
        "wind_direction": weather_features["wind_direction"],
        "temperature_t+1": forecasted_features["temperature"],
        "humidity_t+1": forecasted_features["relative_humidity"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "wind_direction_t+1": forecasted_features["wind_direction"]
    }
    print(input_features)
    
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER]], columns=FEATURE_ORDER)

   
    prediction = model.predict(input_df)
    return round(prediction[0])







