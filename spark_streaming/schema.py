from pyspark.sql.types import *

weather_schema=StructType([
StructField("region",StringType()),
StructField("city",StringType()),
StructField("temperature",DoubleType()),
StructField("humidity",IntegerType()),
StructField("wind_speed",DoubleType()),
StructField("weather",StringType()),
StructField("timestamp",LongType())
])