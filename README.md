# project-data-engineering
 
 ## Description
 This project was created as part of my Data Science M.Sc. program at International University. The task was to create a real-time backend for the processing of streaming data that is reliable, scalable and maintainable. It uses Python, Kafka, Pyspark, Apache Druid and Docker. Details regarding architecture see "architecture-sketch.png". A script simulates sensor data from a lot of IoT devices (vehicles).
 
 ## How to use (in short)
The project can be deployed as is with docker compose. The default values should work even on low-end host systems. The data sources in druid are connected automatically through the container "supervisor-specs" which happens after ~30s. After that, the container will shut down and is no longer relevant. Data should be visible in the Druid GUI, which is available via http://localhost:8888/unified-console.html (default ports). For the aggregated data from PySpark this can take a couple of minutes, as the watermark duration is set to three Minutes. The script (sensor data generator) will run approx. 15 minutes and thereby generate well over 30,000 data sets (json) and records in the database (sensor-data-raw). This is of course lower for the aggregated data contained in "sensor-data-aggregated".

## Detailed setup
1. Download repository
1. Configuration of /sensor-data-generator/producer.py
   * Adjust value of "num_entities" --> number of vehicles that are simulated and send data each iteration, the higher the number the more performance impact. Should be >=1 
   * Adjust value of "sensor_interval" --> how long to wait after an iteration and send new data, can be set to 0
   * Adjust value of "script_duration" --> how long the script runs and generates data
   * Setup kafka broker/topic correctly and to your preference under "Kafka configuration"
1. Configuration of /pyspark/pyspark.py
   * Setup Kafka and Spark to your preference under "Kafka configuration" and "Spark configuration"
   * Values that can be played around with are window and watermark duration ("watermark_duration", "window_duration")
   * Different aggregation and group functions can be used
1. Configuration of docker compose file
   * Adjust ports and container names if necessary
   * Make further adjustments (e. g. add kafka brokers)
1. Build and then deploy/start through "docker compose up"
1. Once data is generated and processed, the data sources should already be connected and the supervisors should run in Druid (default access to GUI: http://localhost:8888/unified-console.html)
   * For raw data generated through the sensor data script (default values):
     * Bootstrap servers: kafka0:29092
     * Topic: sensor-data-raw
   * For data aggregated with pyspark (default values):
     * Bootstrap servers: kafka0:29092
     * Topic: sensor-data-aggregated
1. The setup is complete and the data should be visible in Druid after a couple of minutes
   
     
