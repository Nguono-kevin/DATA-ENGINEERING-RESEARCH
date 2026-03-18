def write_stream_to_gcs(df, bucket_name):
    query = df.writeStream \
        .format("parquet") \
        .option("path", f"gs://{bucket_name}/weather-data") \
        .option("checkpointLocation", f"gs://{bucket_name}/checkpoints") \
        .partitionBy("region", "date") \
        .outputMode("append") \
        .start()
    return query