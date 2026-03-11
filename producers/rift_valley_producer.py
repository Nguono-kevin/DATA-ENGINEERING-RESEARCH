import requests
import time

from configs.kafka_config import create_producer
from configs.api_config import API_KEY, BASE_URL
from configs.cities_by_region import rift_valley

producer = create_producer()

def get_weather(city):
    url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    # Check if API returned valid data
    if "main" not in data:
        print(f"⚠️ Could not get weather for {city}: {data}")
        return None

    return {
        "region": "rift_valley",
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "weather": data["weather"][0]["main"],
        "timestamp": int(time.time())
    }

while True:
    for city in rift_valley:
        weather = get_weather(city)

        if weather is None:
            continue  # Skip if API failed

        producer.send("kenya_weather", value=weather)
        print(weather)

    time.sleep(60)