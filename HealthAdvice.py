
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


# if __name__ == "__main__":
#     prompt = "('AQI: Moderate, Dominant Pollutant: PM10, Level: High',)"
#     try:
#         reply = query_ollama_model(prompt)
#         print("Response from model:", reply)
#     except Exception as e:
#         print("Error:", e)

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


def get_health_advice(input_json: HealthAdviceInput) -> dict:
    with open("All_Pollutants_Info.json", "r", encoding="utf-8") as f:
        all_info = json.load(f)
    rural_aqi = input_json.rural_aqi
    dominant_pollutant = input_json.dominant_pollutant
    dominant_level = next((item for item in input_json.data if item.key == dominant_pollutant), None)

    rural_aqi_band = get_aqi_band(rural_aqi, all_info)
    dominant_band = get_aqi_band(dominant_level, all_info) if dominant_value is not None else "Unknown"
    

    dy_prompt = f"('AQI: {rural_aqi_band}, Dominant Pollutant: {dominant_pollutant}, Level: {dominant_band}',)"
    reply = query_ollama_model(dy_prompt)

    


    return {
        "advice": reply.strip()
    }



# def get_health_advice(input_json: HealthAdviceInput) -> dict:

#     dominant_pollutant = input_json.dominant_pollutant
    dominant_level = next((item for item in input_json.data if item.key == dominant_pollutant), None)
    
   

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



