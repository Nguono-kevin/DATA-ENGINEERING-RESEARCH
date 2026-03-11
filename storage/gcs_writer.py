weather_df.writeStream \
.format("parquet") \
.option("path","gs://kenya-weather-data/processed") \
.option("checkpointLocation","gs://kenya-weather-data/checkpoints") \
.outputMode("append") \
.start()