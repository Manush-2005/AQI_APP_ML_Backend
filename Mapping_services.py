import requests


# nearby hospital using overpass.

def get_nearby_hospitals(lat, lon, radius=10000):
    
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
    try:
        overpass_resp = requests.get(overpass_url, params={'data': query}, timeout=20)
        overpass_data = overpass_resp.json()
        hospitals = overpass_data.get("elements", [])
       
        return hospitals[:5]
    except Exception as e:
        print(f"Overpass API failed: {e}")
        return []


lat = 22.319258159974734
lon = 73.21655888438862
hospitals = get_nearby_hospitals(lat, lon, radius=10000)
for hospital in hospitals:
    print(hospital)