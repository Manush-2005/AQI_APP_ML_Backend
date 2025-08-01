import requests

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
