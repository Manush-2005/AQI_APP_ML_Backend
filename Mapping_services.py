import requests


# nearby hospital using overpass.

def get_nearby_hospitals(lat, lon, radius=10000):
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = query = f"""
[out:json];
(
  node(around:{radius},{lat},{lon})["amenity"="hospital"]["name"];
  way(around:{radius},{lat},{lon})["amenity"="hospital"];
  relation(around:{radius},{lat},{lon})["amenity"="hospital"];
);
out center 3;
"""

    try:
        overpass_resp = requests.get(overpass_url, params={'data': query}, timeout=20)
        overpass_data = overpass_resp.json()
        hospitals = overpass_data.get("elements", [])
       
        return hospitals[:3]
    except Exception as e:
        print(f"Overpass API failed: {e}")
        return []


lat = 30.6989
lon = 76.6898
hospitals = get_nearby_hospitals(lat, lon)
print(hospitals)