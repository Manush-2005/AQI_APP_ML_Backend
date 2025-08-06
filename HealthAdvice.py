
from pydantic import BaseModel
from typing import List
import json

class dataResponseItem(BaseModel):
    key: str
    value: float

class HealthAdviceInput(BaseModel):
    rural_aqi: float
    dominant_pollutant: str
    data: List[dataResponseItem]

class HealthAdviceOutput(BaseModel):
    advice: str


import requests

def query_ollama_model(text, port=11434):
    url = f"http://localhost:{port}/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "model": "AQIModel", 
        "messages": [
            {"role": "user", "content": text}
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
      
        message = result['choices'][0]['message']['content']
        return message
    else:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")


def get_aqi_band(aqi_value, all_info):
    for cat in all_info["AQI_categories"]:
        range_str = cat.get("range")
        if not range_str:
            continue
        if "-" in range_str:
            low, high = map(int, range_str.split("-"))
            if low <= aqi_value <= high:
                return cat.get("level", "Unknown")
        elif ">" in range_str:
            low = int(range_str.replace(">", ""))
            if aqi_value > low:
                return cat.get("level", "Unknown")
    return "Unknown"

def get_pollutant_band(pollutant: str, value: float) -> str:
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
    bands = ["Low", "Moderate", "High", "Very High", "Very High", "Very High"]

    if pollutant not in breakpoints:
        return "Unknown"

    for idx, (bp_lo, bp_hi, _, _) in enumerate(breakpoints[pollutant]):
        if bp_lo <= value <= bp_hi:
            return bands[idx]
    return "Unknown"

def get_health_advice(input_json: HealthAdviceInput) -> dict:
    with open("All_Pollutants_Info.json", "r", encoding="utf-8") as f:
        all_info = json.load(f)
    rural_aqi = input_json.rural_aqi
    dominant_pollutant = input_json.dominant_pollutant
    dominant_level = next((item for item in input_json.data if item.key == dominant_pollutant), None)

    rural_aqi_band = get_aqi_band(rural_aqi, all_info)
    
    dominant_band = get_pollutant_band(dominant_level.key,dominant_level.value) if dominant_level.value is not None else "Unknown"
    

    dy_prompt = f"('AQI: {rural_aqi_band}, Dominant Pollutant: {dominant_pollutant}, Level: {dominant_band}',)"
    print(dy_prompt)
    reply = query_ollama_model(dy_prompt)

    


    return {
        "advice": reply.strip()
    }



# def get_health_advice(input_json: HealthAdviceInput) -> dict:

#     dominant_pollutant = input_json.dominant_pollutant
    dominant_level = next((item for item in input_json.data if item.key == dominant_pollutant), None)
    

input = {
  "rural_aqi": 73,
  "dominant_pollutant": "PM2.5",
  "data": [
    { "key": "PM2.5", "value": 44 },
    { "key": "PM10", "value": 59 },
    { "key": "NO2", "value": 38 },
    { "key": "SO2", "value": 30 },
    { "key": "CO", "value": 23 },
    { "key": "OZONE", "value": 28 },
    { "key": "NH3", "value": 4 }
  ]
}
ans = get_health_advice(input_json=HealthAdviceInput(**input))
print(ans)
#     response = client.chat.completions.create(
#         model="moonshotai/kimi-k2-instruct",
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are an expert air quality and environmental health assistant. "
#                     "You will receive current pollutant levels and weather data. "
#                     "You have knowledge of the dominant pollutant and its health effects. "
#                     f"This is your data : {all_info}\n"
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": (
#                     "Here is the current air quality data:\n"

#                     f"This is the dominant pollutant: {dominant_pollutant}\n"
#                     f"This is the dominant pollutant level: {dominant_level}\n"
#                     "Return your response as structured JSON as per the expected schema."
#                 )
#             }
#         ],
#         response_format={
#             "type": "json_schema",
#             "json_schema": {
#                 "name": "health_advice",
#                 "schema": HealthAdviceOutput.model_json_schema()
#             }
#         }
#     )

#     review = HealthAdviceOutput.model_validate(json.loads(response.choices[0].message.content))
#     return review.model_dump()



