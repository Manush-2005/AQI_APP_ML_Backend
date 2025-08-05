
import pandas as pd
import requests
import joblib

model_pm25 = joblib.load("./models/PM25Model.pkl")
model_pm10 = joblib.load("./models/PM10Model.pkl")
model_NO2 = joblib.load("./models/NO2Model.pkl")
model_SO2 = joblib.load("./models/SO2Model.pkl")
model_O3 = joblib.load("./models/O3Model.pkl")

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
        "current": "wind_speed_10m,wind_direction_10m,relative_humidity_2m,temperature_2m,surface_pressure",
        "daily": "shortwave_radiation_sum,precipitation_sum",
    }
    response = requests.get(url, params=params)
    weather_data = response.json()
    

    result = {
        
        "wind_speed": weather_data.get("current", {}).get("wind_speed_10m"),
        "wind_direction": weather_data.get("current", {}).get("wind_direction_10m"),
        "relative_humidity": weather_data.get("current", {}).get("relative_humidity_2m"),
        "temperature": weather_data.get("current", {}).get("temperature_2m"),
        "precipitation": weather_data.get("daily", {}).get("precipitation_sum", [None])[0],
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
    
    
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER]], columns=FEATURE_ORDER)

   
    prediction = model_pm25.predict(input_df)
    return round(prediction[0])


def predict_pm25_next_3_days(initial_PM25, lat, lon):
    predictions = []
    current_PM25 = initial_PM25
    for _ in range(3):
        next_PM25 = predict_pm25(current_PM25, lat, lon)
        predictions.append(next_PM25)
        current_PM25 = next_PM25  
    return predictions



def predict_pm10(PM10:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)
    FEATURE_ORDER_PM10 = [
    "PM10",
    "temperature",
    "precipitation",
    "wind_speed",
    "wind_direction",
    "temperature_t+1",
    "precipitation_t+1",
    "wind_speed_t+1",
    "wind_direction_t+1",
]

    input_features = {
        "PM10": PM10,
        "temperature": weather_features["temperature"],
        "precipitation": weather_features["precipitation"],
        "wind_speed": weather_features["wind_speed"],
        "wind_direction": weather_features["wind_direction"],
        "temperature_t+1": forecasted_features["temperature"],
        "precipitation_t+1": forecasted_features["precipitation"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "wind_direction_t+1": forecasted_features["wind_direction"]
    }
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER_PM10]], columns=FEATURE_ORDER_PM10)

   
    prediction = model_pm10.predict(input_df)
    return round(prediction[0])



def predict_pm10_next_3_days(initial_PM10, lat, lon):
    predictions = []
    current_PM10 = initial_PM10
    for _ in range(3):
        next_PM10 = predict_pm10(current_PM10, lat, lon)
        predictions.append(next_PM10)
        current_PM10 = next_PM10
    return predictions



def predict_NO2(NO2:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)
    FEATURE_ORDER_NO2 = [
        "NO2",
        "temperature",
        "humidity",
        "wind_speed",
        "solar radiation",
        "temperature_t+1",
        "humidity_t+1",
        "wind_speed_t+1",
        "solar radiation_t+1"
    ]

    input_features = {
        "NO2": NO2,
        "temperature": weather_features["temperature"],
        "humidity": weather_features["relative_humidity"],
        "wind_speed": weather_features["wind_speed"],
        "solar radiation": weather_features.get("shortwave_radiation_sum"),
        "temperature_t+1": forecasted_features["temperature"],
        "humidity_t+1": forecasted_features["relative_humidity"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "solar radiation_t+1": forecasted_features.get("shortwave_radiation_sum")
    }
    

    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER_NO2]], columns=FEATURE_ORDER_NO2)

   
    prediction = model_NO2.predict(input_df)
    return round(prediction[0])



def predict_NO2_next_3_days(initial_NO2, lat, lon):
    predictions = []
    current_NO2 = initial_NO2
    for _ in range(3):
        next_NO2 = predict_NO2(current_NO2, lat, lon)
        predictions.append(next_NO2)
        current_NO2 = next_NO2
    return predictions


def predict_SO2(SO2:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)

    FEATURE_ORDER_SO2 = [
        "SO2",
        "temperature",
        "precipitation",
        "wind_speed",
        "surface pressure",
        "temperature_t+1",
        "precipitation_t+1",
        "wind_speed_t+1",
        "surface pressure_t+1"
    ]

    input_features = {
        "SO2": SO2,
        "temperature": weather_features["temperature"],
        "precipitation": weather_features["precipitation"],
        "wind_speed": weather_features["wind_speed"],
        "surface pressure": weather_features.get("surface_pressure"),
        "temperature_t+1": forecasted_features["temperature"],
        "precipitation_t+1": forecasted_features["precipitation"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "surface pressure_t+1": forecasted_features.get("surface_pressure")
    }
    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER_SO2]], columns=FEATURE_ORDER_SO2)
    prediction = model_SO2.predict(input_df)
    return round(prediction[0])


def predict_SO2_next_3_days(initial_SO2, lat, lon):
    predictions = []
    current_SO2 = initial_SO2
    for _ in range(3):
        next_SO2 = predict_SO2(current_SO2, lat, lon)
        predictions.append(next_SO2)
        current_SO2 = next_SO2
    return predictions




def predict_O3(O3:float,lat:float,lon:float) -> float:
    weather_features = get_weather_features(lat, lon)
    forecasted_features = get_forecasted_features(lat, lon)

    FEATURE_ORDER_O3 = [
        "O3",
        "temperature",
        "humidity",
        "wind_speed",
        "solar radiation",
        "temperature_t+1",
        "humidity_t+1",
        "wind_speed_t+1",
        "solar radiation_t+1"
    ]

    input_features = {
        "O3": O3,
        "temperature": weather_features["temperature"],
        "humidity": weather_features["relative_humidity"],
        "wind_speed": weather_features["wind_speed"],
        "solar radiation": weather_features.get("shortwave_radiation_sum"),
        "temperature_t+1": forecasted_features["temperature"],
        "humidity_t+1": forecasted_features["relative_humidity"],
        "wind_speed_t+1": forecasted_features["wind_speed"],
        "solar radiation_t+1": forecasted_features.get("shortwave_radiation_sum")
    }

    

    input_df = pd.DataFrame([[input_features[col] for col in FEATURE_ORDER_O3]], columns=FEATURE_ORDER_O3)

   
    prediction = model_O3.predict(input_df)
    return round(prediction[0])

def predict_O3_next_3_days(initial_O3, lat, lon):
    predictions = []
    current_O3 = initial_O3
    for _ in range(3):
        next_O3 = predict_O3(current_O3, lat, lon)
        predictions.append(next_O3)
        current_O3 = next_O3
    return predictions










