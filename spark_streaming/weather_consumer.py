from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_date
from schema import weather_schema
from transformations import transform_weather

BUCKET_NAME = "kenya-weather-bucket-1"

# Create Spark session
spark = SparkSession.builder \
    .appName("KenyaWeatherPipeline") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "5") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
    .config("spark.hadoop.google.cloud.auth.type", "APPLICATION_DEFAULT") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("Spark session started")

# Read streaming data from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "kenya_weather") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

print("Connected to Kafka")

# Convert Kafka value to string & parse JSON
json_df = kafka_df.selectExpr("CAST(value AS STRING)")
weather_df = json_df.select(from_json(col("value"), weather_schema).alias("data")).select("data.*")

# Add ingestion date for partitioning
weather_df = weather_df.withColumn("date", current_date())

# Apply transformations
transformed = transform_weather(weather_df)
print("Transformation pipeline ready")

# Debug stream to console (optional)
console_query = transformed.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", "false") \
    .trigger(processingTime="15 seconds") \
    .start()

# Write stream to GCS using ADCbin/
gcs_query = transformed.writeStream \
    .format("parquet") \
    .option("path", f"gs://{BUCKET_NAME}/weather-data") \
    .option("checkpointLocation", f"/tmp/checkpoints/weather") \
    .partitionBy("region", "date") \
    .outputMode("append") \
    .trigger(processingTime="30 seconds") \
    .start()

print("Streaming queries started")

# Keep Spark streaming alive
spark.streams.awaitAnyTermination()