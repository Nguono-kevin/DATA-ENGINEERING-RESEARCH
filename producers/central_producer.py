import requests
import time

from configs.kafka_config import create_producer
from configs.api_config import API_KEY, BASE_URL
from configs.cities_by_region import central

producer=create_producer()

def get_weather(city):

    url=f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"

    data=requests.get(url).json()

    return{
        "region":"central",
        "city":city,
        "temperature":data["main"]["temp"],
        "humidity":data["main"]["humidity"],
        "wind_speed":data["wind"]["speed"],
        "weather":data["weather"][0]["main"],
        "timestamp":int(time.time())
    }

while True:

    for city in central:

        weather=get_weather(city)

        producer.send("kenya_weather",weather)

        print(weather)

    time.sleep(60)