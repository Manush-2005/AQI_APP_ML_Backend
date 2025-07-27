import requests

url = "https://api.openaq.org/v3/locations?coordinates=28.6139,77.2090&radius=5000&limit=2"

headers = {
    "X-API-Key": "455bacaee86e68acc35ab84354d5acd5d2cf3682733b63a714623768c5125e95"  
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error:", response.status_code, response.text)
