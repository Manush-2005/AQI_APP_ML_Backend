import requests
import xml.etree.ElementTree as ET
from math import radians, sin, cos, sqrt, atan2
import math
import numpy as np


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

CPCB_API_URL = "https://airquality.cpcb.gov.in/caaqms/rss_feed"
REQUIRED_POLLUTANTS = {}


url = "https://api.open-meteo.com/v1/forecast"

def get_weather_features(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wind_speed_10m,wind_direction_10m,temperature_2m",
        "timezone": "Asia/Kolkata"
    }
    response = requests.get(url, params=params)
    weather_data = response.json()

    result = {
        
        "wind_speed": weather_data.get("current", {}).get("wind_speed_10m"),
        "wind_direction": weather_data.get("current", {}).get("wind_direction_10m"),
        "temperature": weather_data.get("current", {}).get("temperature_2m"),
    }
    return result


def calculate_ruralAQI(lat: float, lon: float):
    nearest_stations = get_nearest_five_stations(lat, lon)
    aqi_values = [station['NearestAQI'] for station in nearest_stations]
    distances = [station['Distance'] for station in nearest_stations]

    for aqi, dist in zip(aqi_values, distances):
        if dist == 0:
            return aqi
        
    power = 2
    weights = [1 / (d ** power) for d in distances]

    weighted_sum = sum(w * aqi for w, aqi in zip(weights, aqi_values))
    weights_sum = sum(weights)

    interpolated_aqi = weighted_sum / weights_sum
    
    
    return interpolated_aqi







   
   









def get_nearest_five_stations(lat: float, lon: float):
   
    response = requests.get(CPCB_API_URL)
    
    
    if response.status_code != 200:
        raise Exception("Failed to fetch CPCB XML feed")

    root = ET.fromstring(response.content)
    print(response.content)
    stations_data = []
    for station in root.findall(".//Station"):
        
        
        
        
        try:
            station_lat = float(station.attrib["latitude"])
            station_lon = float(station.attrib["longitude"])
        except (KeyError, ValueError):
            continue

        dist = haversine(lat, lon, station_lat, station_lon)
        aqi_tag = station.find("Air_Quality_Index")
        if aqi_tag is not None and "Value" in aqi_tag.attrib:
            aqi = float(aqi_tag.attrib["Value"])
            stations_data.append({
                "NearestAQI": aqi,
                "Distance": dist,
                "lat": station_lat,
                "lon": station_lon
            })

        
        


    return sorted(stations_data, key=lambda x: x["Distance"])[:5]









def get_all_stations_data():
    response = requests.get(CPCB_API_URL)
    if response.status_code != 200:
        raise Exception("Failed to fetch CPCB XML feed")

    root = ET.fromstring(response.content)
    stations_data = []
    for station in root.findall(".//Station"):
       try:
        station_lat = float(station.attrib["latitude"])
        station_lon = float(station.attrib["longitude"])
       except (KeyError, ValueError):
        continue

       aqi_tag = station.find("Air_Quality_Index")
       if aqi_tag is not None and "Value" in aqi_tag.attrib:
        aqi = float(aqi_tag.attrib["Value"])
        stations_data.append({
            "lat": station_lat,
            "lon": station_lon,
            "AQI": aqi
        })

    



   

    return stations_data








        
        


def get_nearest_pollutant_levels(lat: float, lon: float):
    response = requests.get(CPCB_API_URL)
    if response.status_code != 200:
        raise Exception("Failed to fetch CPCB XML feed")

    root = ET.fromstring(response.content)
    # print(response.content)
   
  
    stations_data = []
    for station in root.findall(".//Station"):
        try:
            station_lat = float(station.attrib["latitude"])
            station_lon = float(station.attrib["longitude"])
            name = station.attrib["id"]
        except (KeyError, ValueError):
            continue

        dist = haversine(lat, lon, station_lat, station_lon)
        pollutants = {
            "PM2.5": None,
            "PM10": None,
            "NO2": None,
            "SO2": None,
            "CO": None,
            "OZONE": None,
            "NH3": None
        }
        for pollutant in station.findall("Pollutant_Index"):
            pid = pollutant.attrib["id"].upper().replace(" ", "")
            avg_val = pollutant.attrib.get("Avg", "NA")
            if pid in pollutants and avg_val != 'NA':
                try:
                    pollutants[pid] = float(avg_val)
                except ValueError:
                    continue
        
        
        stations_data.append({
            "Distance": dist,
            "lat": station_lat,
            "lon": station_lon,
            "Name": name,
            **pollutants
        })
    result = {}
    for key in ["PM2.5", "PM10", "NO2", "SO2", "CO", "OZONE", "NH3"]:
        filtered = [s for s in stations_data if s[key] is not None]
        sorted_stations = sorted(filtered, key=lambda x: x["Distance"])[:5]
        result[key] = [{
                "Distance": s["Distance"],
                "Value": s[key],
                "lat": s["lat"],
                "lon": s["lon"],
                "Name": s["Name"]
            }for s in sorted_stations]

    return result

def compute_weight(distance, weather_diff, alpha=1.0, beta=1.0):
   
    return np.exp(-alpha * distance**2 - beta * weather_diff**2)


def calculate_pollutant_levels(lat: float, lon: float):
    nearest_levels = get_nearest_pollutant_levels(lat, lon)
    # print(nearest_levels)
    user_weather = get_weather_features(lat, lon)

    distance_threshold = 10.0 
   
    
   
    result = {}
 
    for pollutant, stations in nearest_levels.items():
        values = [s['Value'] for s in stations]
        distances = [s['Distance'] for s in stations]
        weather_diffs = []

        for s in stations:
            station_weather = get_weather_features(s["lat"], s["lon"])
            weather_diff = (
                abs(user_weather['temperature'] - station_weather['temperature']) +
                abs(user_weather['wind_speed'] - station_weather['wind_speed']) +
                abs(user_weather['wind_direction'] - station_weather['wind_direction']) / 180
            )
            weather_diffs.append(weather_diff)
        max_dist = max(distances) if distances else 1
        max_weather_diff = max(weather_diffs) if weather_diffs else 1
        

       
        for value, dist in zip(values, distances):
            if dist <= distance_threshold:
                result[pollutant] = value
                break
        else:
            weights = []
            for s, value, dist, weather_diff in zip(stations, values, distances, weather_diffs):
              scaled_dist = dist / max_dist if max_dist != 0 else 0
              scaled_weather_diff = weather_diff / max_weather_diff if max_weather_diff != 0 else 0
              weight = compute_weight(scaled_dist, scaled_weather_diff, alpha=1.0, beta=1.0)
              weights.append(weight)


                

            weighted_sum = sum(w * v for w, v in zip(weights, values))
            weights_sum = sum(weights)
            interpolated_value = weighted_sum / weights_sum if weights_sum != 0 else None
            result[pollutant] = round(interpolated_value) if interpolated_value is not None else None

    return result



# res = calculate_ruralAQI(22.319258159974734, 73.21655888438862)

# pollutant_units = {
#     "PM25 ": "ug/m3",
#     "PM10": "ug/m3",
#     "NO2": "ug/m3",
#     "SO2": "ug/m3",
#     "CO": "ug/m3",      
#     "OZONE": "ug/m3",
#     "NH3": "ug/m3"
# }
# aqi_results = {}
# print(res2)
# for pollutant, value in res2.items():
#     unit = pollutant_units.get(pollutant, "ug/m3")
#     try:
#         aqi = calculate_aqi('IN', pollutant, value, unit)
#         aqi_results[pollutant] = aqi
#     except Exception as e:
#         aqi_results[pollutant] = None

# print("aqi",aqi_results)




# def normalize_weather_vectors(vec1, vec2):
#     scaler = MinMaxScaler()
#     scaler.fit(np.array([
#         [-10, 0, 0, 0, 950, 0, 0],
#         [50, 20, 360, 100, 1050, 100, 100]
#     ]))
#     return scaler.transform([vec1, vec2])

# def gaussian_kernel(vec1, vec2, sigma):
#     vecs = normalize_weather_vectors(vec1, vec2)
#     diff = np.array(vecs[0]) - np.array(vecs[1])
#     return math.exp(-np.dot(diff, diff) / (2 * sigma ** 2))

# def get_ruralAQI_with_weather(lat,lon):
#     nearest_stations = get_nearest_five_stations(lat, lon)
#     weather_features = ['temperature', 'wind_speed', 'wind_direction', 'relative_humidity', 'surface_pressure', 'cloud_cover', 'precipitation_probability']

#     rural_weather = get_weather_features(lat, lon)
#     rural_vector = [rural_weather[feat] for feat in weather_features]

#     aqi_values = []
#     weights = []

#     for station in nearest_stations:
#         dist = station['Distance']
#         aqi = station['NearestAQI']
#         station_weather = get_weather_features(station['lat'], station['lon'])
#         station_vector = [station_weather[feat] for feat in weather_features]

#         power = 2
#         sigma = 1.5
#         if dist == 0:
#             return aqi
#         if any(v is None for v in station_vector + rural_vector):
#             continue

#         spatial_weight = 1 / (dist ** power)
#         feature_weight = gaussian_kernel(station_vector, rural_vector, sigma)
#         total_weight = spatial_weight * feature_weight

#         aqi_values.append(aqi)
#         weights.append(total_weight)

   
#     if not weights:
#         return None  

#     weighted_sum = sum(w * aqi for w, aqi in zip(weights, aqi_values))
#     total_weight = sum(weights)

#     return weighted_sum / total_weight



# aqi = get_ruralAQI_with_weather(22.319258159974734, 73.21655888438862)
# print(f"Calculated Rural AQI: {aqi}")


# url = "https://api.open-meteo.com/v1/forecast"


# def wind_direction_weight(station_bearing, wind_direction, k=4):
    
#     angle_diff = math.radians((station_bearing - wind_direction + 360) % 360)
    
#     weight = (1 + math.cos(angle_diff)) / 2
#     return weight ** k 

# def calculate_bearing(lat1, lon1, lat2, lon2):
#     d_lon = math.radians(lon2 - lon1)
#     lat1 = math.radians(lat1)
#     lat2 = math.radians(lat2)

#     x = math.sin(d_lon) * math.cos(lat2)
#     y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(d_lon)
#     bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
#     return bearing


# def get_ruralAQI_with_weather_with_wind_direction(lat,lon):
#     nearest_stations = get_nearest_five_stations(lat, lon)
#     weather_features = ['temperature', 'wind_speed', 'wind_direction', 'relative_humidity', 'surface_pressure', 'cloud_cover', 'precipitation_probability']

#     rural_weather = get_weather_features(lat, lon)
#     rural_vector = [rural_weather[feat] for feat in weather_features]
#     rural_wind_direction = rural_weather['wind_direction']

#     aqi_values = []
#     weights = []

#     for station in nearest_stations:
#         dist = station['Distance']
#         aqi = station['NearestAQI']
#         station_lat = station['lat']
#         station_lon = station['lon']
#         station_weather = get_weather_features(station['lat'], station['lon'])
#         station_vector = [station_weather[feat] for feat in weather_features]

#         power = 2
#         sigma = 1.5
#         k_direction = 4
#         if dist == 0:
#             return aqi
#         if any(v is None for v in station_vector + rural_vector):
#             continue

#         spatial_weight = 1 / (dist ** power)
#         feature_weight = gaussian_kernel(station_vector, rural_vector, sigma)
#         station_bearing = calculate_bearing(lat, lon, station_lat, station_lon)
#         direction_weight = wind_direction_weight(station_bearing, rural_wind_direction, k=k_direction)
#         total_weight = spatial_weight * feature_weight * direction_weight

#         aqi_values.append(aqi)
#         weights.append(total_weight)

   
#     if not weights:
#         return None  

#     weighted_sum = sum(w * aqi for w, aqi in zip(weights, aqi_values))
#     total_weight = sum(weights)

#     return weighted_sum / total_weight



# def calculate_pollutants_from_indices(lat: float, lon: float,pollutants: dict) -> dict:

 

    
#     breakpoints = {
#         'PM2.5': [
#             (0, 30, 0, 50),
#             (31, 60, 51, 100),
#             (61, 90, 101, 200),
#             (91, 120, 201, 300),
#             (121, 250, 301, 400),
#             (251, 500, 401, 500)
#         ],
#         'PM10': [
#             (0, 50, 0, 50),
#             (51, 100, 51, 100),
#             (101, 250, 101, 200),
#             (251, 350, 201, 300),
#             (351, 430, 301, 400),
#             (431, 1000, 401, 500)
#         ],
#         'SO2': [
#             (0, 40, 0, 50),
#             (41, 80, 51, 100),
#             (81, 380, 101, 200),
#             (381, 800, 201, 300),
#             (801, 1600, 301, 400),
#             (1601, 2000, 401, 500)
#         ],
#         'NO2': [
#             (0, 40, 0, 50),
#             (41, 80, 51, 100),
#             (81, 180, 101, 200),
#             (181, 280, 201, 300),
#             (281, 400, 301, 400),
#             (401, 1000, 401, 500)
#         ],
#         'O3': [
#             (0, 50, 0, 50),
#             (51, 100, 51, 100),
#             (101, 168, 101, 200),
#             (169, 208, 201, 300),
#             (209, 748, 301, 400),
#             (749, 1000, 401, 500)
#         ]
#     }

#     def calculate_individual_aqi(cp, pollutant):
        
#         for (BP_Lo, BP_Hi, I_Lo, I_Hi) in breakpoints[pollutant]:
#             if BP_Lo <= cp <= BP_Hi:
#                 return round(((I_Hi - I_Lo) / (BP_Hi - BP_Lo)) * (cp - BP_Lo) + I_Lo)
#         return None  

#     individual_aqis = {}
#     for pollutant, value in pollutants.items():
#         if pollutant in breakpoints:
#             aqi = calculate_individual_aqi(value, pollutant)
#             if aqi is not None:
#                 individual_aqis[pollutant] = aqi

#     if not individual_aqis:
#         raise ValueError("No valid pollutant values provided for AQI calculation.")

  
#     overall_aqi = max(individual_aqis.values())
#     dominant = max(individual_aqis, key=individual_aqis.get)

#     return {
#         "individual_aqis": individual_aqis,
#         "overall_aqi": overall_aqi,
#         "dominant_pollutant": dominant
#     }


def calculate_levels_from_subindices(subindices: dict) -> dict:
    breakpoints = {
        'PM2.5': [
            (0, 30, 0, 50),
            (31, 60, 51, 100),
            (61, 90, 101, 200),
            (91, 120, 201, 300),
            (121, 250, 301, 400),
            (251, 500, 401, 500)
        ],
        'PM10': [
            (0, 50, 0, 50),
            (51, 100, 51, 100),
            (101, 250, 101, 200),
            (251, 350, 201, 300),
            (351, 430, 301, 400),
            (431, 1000, 401, 500)
        ],
        'SO2': [
            (0, 40, 0, 50),
            (41, 80, 51, 100),
            (81, 380, 101, 200),
            (381, 800, 201, 300),
            (801, 1600, 301, 400),
            (1601, 2000, 401, 500)
        ],
        'NO2': [
            (0, 40, 0, 50),
            (41, 80, 51, 100),
            (81, 180, 101, 200),
            (181, 280, 201, 300),
            (281, 400, 301, 400),
            (401, 1000, 401, 500)
        ],
        'OZONE': [
            (0, 50, 0, 50),
            (51, 100, 51, 100),
            (101, 168, 101, 200),
            (169, 208, 201, 300),
            (209, 748, 301, 400),
            (749, 1000, 401, 500)
        ],
        'CO': [
    (0, 1.0, 0, 50),
    (1.1, 2.0, 51, 100),
    (2.1, 10.0, 101, 200),
    (10.1, 17.0, 201, 300),
    (17.1, 34.0, 301, 400),
    (34.1, 100.0, 401, 500)
],
'NH3': [
    (0, 200, 0, 50),
    (201, 400, 51, 100),
    (401, 800, 101, 200),
    (801, 1200, 201, 300),
    (1201, 1800, 301, 400),
    (1801, 3000, 401, 500)
]
    }

    def invert_aqi(aqi, pollutant):
        for (BP_Lo, BP_Hi, I_Lo, I_Hi) in breakpoints.get(pollutant, []):
            if I_Lo <= aqi <= I_Hi:
                
                cp = ((aqi - I_Lo) * (BP_Hi - BP_Lo) / (I_Hi - I_Lo)) + BP_Lo
                return round(cp)
        return None

    levels = {}
    for pollutant, aqi in subindices.items():
        if pollutant in breakpoints:
            level = invert_aqi(aqi, pollutant)
            if level is not None:
                levels[pollutant] = level

    return levels

# # Example usage:
# subindices = {'PM2.5': 83, 'PM10': 92, 'NO2': 28, 'SO2': 19, 'CO': 29, 'OZONE': 18, 'NH3': 4}
# levels = calculate_levels_from_subindices(subindices)
# print(levels)
