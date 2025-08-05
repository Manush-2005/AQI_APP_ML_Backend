import requests
import json
from geopy.distance import geodesic

#This gets the nearby hospitals using Overpass API

def get_nearby_hospitals(lat, lon, radius):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
        node(around:{radius},{lat},{lon})["amenity"="hospital"];
        way(around:{radius},{lat},{lon})["amenity"="hospital"];
        relation(around:{radius},{lat},{lon})["amenity"="hospital"];
    );
    out center 5;
    """
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()
    return data["elements"]


lat = 22.319258159974734
lon = 73.21655888438862 
radius = 2000

hospitals = get_nearby_hospitals(lat, lon, radius)
for hospital in hospitals:
    print(hospital)



# This gets the nearby industries using Overpass API
def get_nearby_industries(lat, lon, radius):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
        node(around:{radius},{lat},{lon})["industrial"~"factory|manufacture|chemical|plant|heavy_industry"];
        way(around:{radius},{lat},{lon})["industrial"~"factory|manufacture|chemical|plant|heavy_industry"];
        relation(around:{radius},{lat},{lon})["industrial"~"factory|manufacture|chemical|plant|heavy_industry"];
        node(around:{radius},{lat},{lon})["landuse"="industrial"];
        way(around:{radius},{lat},{lon})["landuse"="industrial"];
        relation(around:{radius},{lat},{lon})["landuse"="industrial"];
        node(around:{radius},{lat},{lon})["building"="industrial"];
        way(around:{radius},{lat},{lon})["building"="industrial"];
        relation(around:{radius},{lat},{lon})["building"="industrial"];
    );
    out center 10;
    """
    response = requests.get(overpass_url, params={'data': query})
    data = response.json()
    return data.get('elements', [])





def get_nearest_factories_json(lat, lon, limit=5):
    factories = get_nearby_industries(lat, lon, 5000)
    factories_with_distance = []
    for el in factories:
        if 'center' in el:
            el_lat = el['center']['lat']
            el_lon = el['center']['lon']
        else:
            el_lat = el.get('lat')
            el_lon = el.get('lon')
        if el_lat is None or el_lon is None:
            continue
        distance = geodesic((lat, lon), (el_lat, el_lon)).km
        factories_with_distance.append({
            'id': el.get('id'),
            'type': el.get('type'),
            'latitude': el_lat,
            'longitude': el_lon,
            'distance_km': round(distance),
        })
    factories_with_distance.sort(key=lambda x: x['distance_km'])
    nearest = factories_with_distance[:limit]
    return json.dumps(nearest, indent=2)




