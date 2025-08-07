
from datetime import datetime, timedelta
from Rural_Predection import calculate_pollutants_from_indices


import requests

url = "https://air-quality-api.open-meteo.com/v1/air-quality"

def get_weather_features(lat, lon):
    today = datetime.now().date()
    start_date = today - timedelta(days=7)
    end_date = today - timedelta(days=1)
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
         "start_date": start_date,
        "end_date": end_date
    }
    response = requests.get(url, params=params)
    weather_data = response.json()

    hourly_data = weather_data.get("hourly", {})
    times = hourly_data.get("time", [])

    pollutants = [
        "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone"
    ]

    daily_averages = {}

    for pollutant in pollutants:
        hourly_values = hourly_data.get(pollutant, [])
        daily_values = {}
        for t, v in zip(times, hourly_values):
            date_str = t.split("T")[0]
            daily_values.setdefault(date_str, []).append(v)
     
        daily_averages[pollutant] = {
            d: round(sum(vals)/len(vals), 1) for d, vals in daily_values.items() if vals
        }

  
    return daily_averages

def calculate_daily_aqi_from_averages(lat: float, lon: float) -> dict:

    daily_averages = get_weather_features(lat, lon)
    pollutant_map = {
        "pm2_5": "PM2.5",
        "pm10": "PM10",
        "nitrogen_dioxide": "NO2",
        "sulphur_dioxide": "SO2",
        "ozone": "O3",
        "carbon_monoxide": "CO",
        "ammonia": "NH3"
    }

    
    all_dates = set()
    for vals in daily_averages.values():
        all_dates.update(vals.keys())

    results = {}
    for date in sorted(all_dates):
        pollutants_for_day = {}
        for api_key, aqi_key in pollutant_map.items():
            if api_key in daily_averages and date in daily_averages[api_key]:
                pollutants_for_day[aqi_key] = daily_averages[api_key][date]
        if pollutants_for_day:
            aqi_info = calculate_pollutants_from_indices(lat, lon, pollutants_for_day)
            results[date] = {
                "AQI": aqi_info["overall_aqi"],
                "dominant_pollutant": aqi_info["dominant_pollutant"],
                "individual_aqis": aqi_info["individual_aqis"],
                "pollutants": pollutants_for_day
            }
    return results

# res = calculate_daily_aqi_from_averages(30.6989, 76.6898)
# print(res)

# Example usage:
# daily_averages = get_weather_features(lat, lon)  # Your function that returns daily pollutant averages
# daily_aqi = calculate_daily_aqi_from_averages(lat, lon, daily_averages)
# print(daily_aqi)






