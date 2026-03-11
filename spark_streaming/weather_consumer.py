from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from schema import weather_schema

spark=SparkSession.builder \
.appName("KenyaWeatherPipeline") \
.getOrCreate()

df=spark.readStream \
.format("kafka") \
.option("kafka.bootstrap.servers","localhost:9092") \
.option("subscribe","kenya_weather") \
.load()

json_df=df.selectExpr("CAST(value AS STRING)")

weather_df=json_df.select(
from_json(col("value"),weather_schema).alias("data")
).select("data.*")