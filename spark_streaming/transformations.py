from pyspark.sql.functions import *

def transform_weather(df):

    transformed = df \
        .withColumn("temperature_c", col("temperature")) \
        .withColumn("temperature_f", col("temperature") * 9/5 + 32) \
        .withColumn("event_time", from_unixtime(col("timestamp")))

    return transformed