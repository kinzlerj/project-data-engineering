from confluent_kafka import Producer
from datetime import datetime
import sys
import pytz
import threading
import time
import random
import json


# Script configuration
num_entities = 200  # number of simulated entities ("vehicles")
sensor_interval = 5  # waiting time for next iteration
script_duration = 60 * 15  # duration in seconds

# Kafka configuration
KAFKA_BROKER = "kafka0:29092"
KAFKA_TOPIC = "sensor-data-raw"

config = {
    'bootstrap.servers': KAFKA_BROKER,
}

producer = Producer(config)


# Function to get current timestamp in desired format
def get_time():
    germany_tz = pytz.timezone('Europe/Berlin')
    timestamp = datetime.now(germany_tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # timestamp with milliseconds
    return timestamp


# Function that stops script after specified duration (see "Script configuration") and prints message
def stop_script():
    print(f"\n\nEnding script, specified duration of {script_duration}s reached or exceeded.")
    global is_running
    is_running = False


# Timer to stop the script
is_running = True

timer = threading.Timer(script_duration, stop_script)
timer.start()

# Generating sensor data
try:

    iteration = 0

    # Stop script, if set duration is reached or exceeded
    while is_running:

        # Optional: Setting timestamps to calculate processing time of iterations
        start_time = time.time()
        start_timestamp = get_time()
        
        # Iterate over specified number of entities per iteration
        for entity in range(1, num_entities + 1):
            
            # Simulate Sensor Data
            temperature = round(random.gauss(20, 1), 2)  # random temperature
            humidity = round(random.gauss(35, 5), 2)     # random humidity

            # Aggregate Sensor Data ("IoT Gateway") per entity
            sensor_data = {
                "time": get_time(),
                "entity": entity,
                "temp": temperature,
                "humidity": humidity
            }
            sensor_data = json.dumps(sensor_data)  # Convert dictionary to JSON

            # Publish json to kafka
            producer.produce(KAFKA_TOPIC, sensor_data)
            producer.flush()

        # Print current iteration and starting timestamp
        iteration += 1
        print(f"\nIteration: {iteration}, starting time: {start_timestamp}")

        # Print processing time of current iteration and specified waiting time for next iteration
        processing_time = int(round(time.time() - start_time, 3)*1000)
        print(f"Processing time of iteration: {processing_time}ms, now waiting {sensor_interval}s")

        # Flush to show information in docker log/terminal
        sys.stdout.flush()

        # Wait x seconds to generate new data & start new iteration (see script config)
        time.sleep(sensor_interval)

except KeyboardInterrupt:
    pass

# Optional: Print final value of iterations and generated data
print("Number of iterations:", iteration, "\nNumber of generated data sets (json):", iteration*num_entities)