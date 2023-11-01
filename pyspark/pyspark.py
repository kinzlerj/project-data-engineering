import findspark
findspark.init('/usr/local/lib/python3.11/site-packages/pyspark')

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *


# Kafka configuration
KAFKA_BROKER = "kafka0:29092"
KAFKA_TOPIC_SOURCE = "sensor-data-raw"
KAFKA_TOPIC_TARGET = "sensor-data-aggregated"

# Spark configuration
spark = SparkSession.builder.appName('kafka-sensor')\
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0')\
    .getOrCreate()

# Define schema of sensor data
message_schema = (
    StructType()
    .add("time", TimestampType())
    .add("entity", StringType())
    .add("temp", DoubleType())
    .add("humidity", DoubleType())
)

# Reading streaming data
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka0:29092") \
    .option("subscribe", KAFKA_TOPIC_SOURCE) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# Decoding data from Kafka messages
decoded_df = df.selectExpr("CAST(value AS STRING)").select(from_json("value", message_schema).alias("sensor_data"))
decoded_df = decoded_df.select("sensor_data.*")

# Defining watermark and window duration
watermark_duration = "3 minutes"
window_duration = "1 minute"

# Add watermark
decoded_df = decoded_df.withWatermark("time", watermark_duration)

# Aggregate data by defined time window
aggregated_df = decoded_df \
    .groupBy(window(decoded_df.time, window_duration), decoded_df.entity) \
    .agg(round(avg(decoded_df.temp), 2).alias("avg_temp"), last(decoded_df.humidity).alias("last_humidity"))

aggregated_df = aggregated_df.withColumn(
    "window", 
    concat_ws("-", col("window.start").cast("string"), col("window.end").cast("string"))
)

# Format data for usage in kafka message
aggregated_df = aggregated_df.withColumn(
    "value",
    struct(
        col("window").alias("window"),
        col("entity").alias("entity"),
        col("avg_temp").alias("avg_temp"),
        col("last_humidity").alias("last_humidity")
    )
)

# Publish message to kafka
query = aggregated_df \
    .selectExpr("CAST(to_json(value) AS STRING) AS value") \
    .writeStream \
    .outputMode("append") \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("topic", KAFKA_TOPIC_TARGET) \
    .option("checkpointLocation", "/app/streaming-checkpoint") \
    .start()

query.awaitTermination()