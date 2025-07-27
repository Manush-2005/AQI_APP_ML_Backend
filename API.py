import requests

url = "https://bhoonidhi-api.nrsc.gov.in/data/search"
headers = {
    "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBdXRoIiwiVXNlcklEIjoiT05MX01hbnVzaCIsIklQQWRkcmVzcyI6Ijo6MSIsIlNlc3Npb25JRCI6NSwiZXhwaXJlc0F0VGltZSI6IjIwMjUtMDctMjcgMTE6MjQ6NTAiLCJpYXQiOjE3NTM1OTIwOTAsImV4cCI6MTc1MzU5NTY5MH0.UANcKIh4pJJLU52iwc71yZx5y3w_Xw4XT62RpZHFhoI",
    "Content-Type": "application/json"
}

payload = {
"collections":["EOS-04_SAR-MRS_L2A","EOS-06_OCM-LAC_L1C"],
"datetime": "2023-11-02T00:00:00Z/2023-11-03T23:59:59Z",
"limit": 2
}


response = requests.post(url, headers=headers, json=payload, timeout=60)
print(response.status_code)
