import requests
import time

from configs.kafka_config import create_producer
from configs.api_config import API_KEY, BASE_URL
from configs.cities_by_region import western

producer = create_producer()

def get_weather(city):
    url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()

    # Debug: print the full response
    print(city, data)

    # Check if API returned valid weather data
    if "main" not in data:
        print(f"⚠️ Could not get weather for {city}: {data}")
        return None

    return {
        "region": "western",
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "weather": data["weather"][0]["main"],
        "timestamp": int(time.time())
    }

while True:
    for city in western:
        weather = get_weather(city)

        # Skip invalid API responses
        if weather is None:
            continue

        # Send to Kafka safely
        producer.send("kenya_weather", value=weather)
        print(weather)

    # Wait before next round
    time.sleep(60)