import requests
import xml.etree.ElementTree as ET
from math import radians, sin, cos, sqrt, atan2
from AQIPython import calculate_aqi

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

CPCB_API_URL = "https://airquality.cpcb.gov.in/caaqms/rss_feed"
REQUIRED_POLLUTANTS = {}



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


def calculate_pollutant_levels(lat: float, lon: float):
    nearest_levels = get_nearest_pollutant_levels(lat, lon)
    result = {}
    power = 2  
    for pollutant, stations in nearest_levels.items():
        values = [s['Value'] for s in stations]
        distances = [s['Distance'] for s in stations]

       
        for value, dist in zip(values, distances):
            if dist == 0:
                result[pollutant] = value
                break
        else:
            weights = [1 / (d ** power) if d != 0 else 0 for d in distances]
            weighted_sum = sum(w * v for w, v in zip(weights, values))
            weights_sum = sum(weights)
            interpolated_value = weighted_sum / weights_sum if weights_sum != 0 else None
            result[pollutant] = interpolated_value

    return result





   
   









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
            })

        
        


    return sorted(stations_data, key=lambda x: x["Distance"])[:5]






        
        


def get_nearest_pollutant_levels(lat: float, lon: float):
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
            **pollutants
        })

    
    result = {}
    for key in ["PM2.5", "PM10", "NO2", "SO2", "CO", "OZONE", "NH3"]:
        filtered = [s for s in stations_data if s[key] is not None]
        sorted_stations = sorted(filtered, key=lambda x: x["Distance"])[:5]
        result[key] = [{"Distance": s["Distance"], "Value": s[key]} for s in sorted_stations]

    return result


# res = calculate_ruralAQI(22.319258159974734, 73.21655888438862)
# res2 = calculate_pollutant_levels(22.319258159974734, 73.21655888438862)
# pollutant_units = {
#     "PM2.5": "ug/m3",
#     "PM10": "ug/m3",
#     "NO2": "ug/m3",
#     "SO2": "ug/m3",
#     "CO": "ug/m3",      
#     "OZONE": "ug/m3",
#     "NH3": "ug/m3"
# }
# aqi_results = {}
# for pollutant, value in res2.items():
#     unit = pollutant_units.get(pollutant, "ug/m3")
#     try:
#         aqi = calculate_aqi('IN', pollutant, value, unit)
#         aqi_results[pollutant] = aqi
#     except Exception as e:
#         aqi_results[pollutant] = None


