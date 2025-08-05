
import pandas as pd

import requests
from geopy.distance import geodesic

def get_fires_nearby(lat, lon, radius_km, map_key):
   
    # NASA FIRMS endpoint for VIIRS SNPP 24-hour global fire data
    url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/VIIRS_SNPP_24h/{lat},{lon},{radius_km}?key={map_key}'

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return f'API error: {response.status_code} {response.reason}'

        data = response.text.strip().split('\n')
        print(data)
        if len(data) < 2:
            return "No fire data available in the area"

        fires = []
        headers = data[0].split(',')
        idx_lat = headers.index('latitude')
        idx_lon = headers.index('longitude')
        idx_acq_date = headers.index('acq_date')
        idx_acq_time = headers.index('acq_time')

        for line in data[1:]:
            parts = line.split(',')
            fire_lat = float(parts[idx_lat])
            fire_lon = float(parts[idx_lon])
            fire_distance = geodesic((lat, lon), (fire_lat, fire_lon)).km
            if fire_distance <= radius_km:
                fire = {
                    'latitude': fire_lat,
                    'longitude': fire_lon,
                    'distance_km': round(fire_distance, 2),
                    'acq_date': parts[idx_acq_date],
                    'acq_time': parts[idx_acq_time]
                }
                fires.append(fire)

        if not fires:
            return "No fires detected within the radius"
        return fires

    except Exception as e:
        return f'Error: {str(e)}'


fires = get_fires_nearby(28.7041, 77.1025, 5, '00260cc053bc6632b3eb14915c316264')
print(fires)
