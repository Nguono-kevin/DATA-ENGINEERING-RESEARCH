# weather_consumer.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType,
    LongType
)

# ---------------------------
# 1. Create Spark Session
# ---------------------------

spark = SparkSession.builder \
    .appName("KafkaWeatherConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ---------------------------
# 2. Define Weather Schema
# ---------------------------
weather_schema = StructType([
    StructField("region", StringType(), True),
    StructField("city", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", IntegerType(), True),
    StructField("wind_speed", DoubleType(), True),
    StructField("weather", StringType(), True),
    StructField("timestamp", LongType(), True)
])

# ---------------------------
# 3. Read Kafka Stream
# ---------------------------
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "kenya_weather")
    .option("startingOffsets", "latest")
    .load()
)

# ---------------------------
# 4. Convert Kafka Binary → String
# ---------------------------
json_df = kafka_df.selectExpr("CAST(value AS STRING) as json")

# ---------------------------
# 5. Parse JSON Data
# ---------------------------
weather_df = (
    json_df
    .withColumn("data", from_json(col("json"), weather_schema))
    .select("data.*")
)

# ---------------------------
# 6. Output Stream (Console)
# ---------------------------
query = (
    weather_df.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", False)
    .option("checkpointLocation", "C:/spark_checkpoint/weather")
    .start()
)

query.awaitTermination()