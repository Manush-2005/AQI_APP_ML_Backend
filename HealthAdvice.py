from groq import Groq
from pydantic import BaseModel
from typing import List
import json

client = Groq(api_key="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")
with open("All_Pollutants_Info.json", "r", encoding="utf-8") as f:
    all_info = json.load(f)

class dataResponseItem(BaseModel):
    key: str
    value: float

class HealthAdviceInput(BaseModel):
    rural_aqi: float
    dominant_pollutant: str
    data: List[dataResponseItem]

class HealthAdviceOutput(BaseModel):
    general_overview: str
    genral_advice: str

def get_health_advice(input_json: HealthAdviceInput) -> dict:

    dominant_pollutant = input_json.dominant_pollutant
    dominant_level = next((item for item in input_json.data if item.key == dominant_pollutant), None)
    
   

    response = client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert air quality and environmental health assistant. "
                    "You will receive current pollutant levels and weather data. "
                    "You have knowledge of the dominant pollutant and its health effects. "
                    f"This is your data : {all_info}\n"
                )
            },
            {
                "role": "user",
                "content": (
                    "Here is the current air quality data:\n"

                    f"This is the dominant pollutant: {dominant_pollutant}\n"
                    f"This is the dominant pollutant level: {dominant_level}\n"
                    "Return your response as structured JSON as per the expected schema."
                )
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "health_advice",
                "schema": HealthAdviceOutput.model_json_schema()
            }
        }
    )

    review = HealthAdviceOutput.model_validate(json.loads(response.choices[0].message.content))
    return review.model_dump()



