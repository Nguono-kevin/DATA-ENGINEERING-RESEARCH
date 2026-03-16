# weather_consumer.py
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, LongType

# ---------------------------
# 1. Windows Hadoop setup
# ---------------------------
os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["HADOOP_CONF_DIR"] = "C:\\hadoop\\etc\\hadoop"

# ---------------------------
# 2. Define Spark session
# ---------------------------
spark = SparkSession.builder \
    .appName("KafkaWeatherConsumer") \
    .getOrCreate()

# ---------------------------
# 3. Define Kafka topic schema
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
# 4. Read streaming data from Kafka
# ---------------------------
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "kenya_weather") \
    .option("startingOffsets", "latest") \
    .load()

# Kafka message value is in binary, convert to string
df_str = df.selectExpr("CAST(value AS STRING)")

# Parse JSON into structured columns
df_parsed = df_str.withColumn("data", from_json(col("value"), weather_schema)) \
                  .select("data.*")

# ---------------------------
# 5. Output streaming to console
# ---------------------------
query = df_parsed.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", False) \
    .option("checkpointLocation", "C:\\Spark\\checkpoints\\weather") \
    .start()

query.awaitTermination()