import paho.mqtt.client as mqtt
import time
import json
from bme280 import BME280
import logging
import psutil
from smbus2 import SMBus

# Set update interval in seconds
UPDATE_INTERVAL = 5
TEMP_COMPENSATE_FACTOR = 2.25


def compensate_temperature(raw_temp):

    cpu_temp = psutil.sensors_temperatures()["cpu_thermal"][
        0
    ].current  # Access CPU core temperature
    logging.info(f"CPU temperature: {cpu_temp:.2f} °C")

    comp_temp = raw_temp - ((cpu_temp - raw_temp) / TEMP_COMPENSATE_FACTOR)
    return comp_temp


# Function to read sensor values with error handling and compensation
def read_bme280_compensated(bme280):
    try:
        raw_temp = bme280.get_temperature()
        # Implement your temperature compensation logic here (e.g., using sensor functions)
        comp_temp = compensate_temperature(raw_temp)
        values = {
            "temperature": int(comp_temp),
            "pressure": int(bme280.get_pressure()),
            "humidity": int(bme280.get_humidity()),
        }
        return values
    except (IOError, OSError) as e:
        logging.exception(f"Error reading sensor: {e}")
        return None


# Callback for successful connection
def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))


# Callback for received messages (not used in this example)
def on_message(client, userdata, msg):
    logging.info(msg.topic + " " + str(msg.payload))


# Callback for successful message publishing
def on_publish(client, userdata, mid):
    logging.info("Published message ID: " + str(mid))


# Create MQTT client and set callbacks
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.username_pw_set("mosquitto", "mosquitto")

# Connect to MQTT broker
client.connect("homeassistant", 1883, 60)

# Initialize BME280 instance outside the loop
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Start MQTT client loop
client.loop_start()

while True:
    # Read sensor values with error handling and retry logic
    values = read_bme280_compensated(bme280)
    if values:
        client.publish("homeassistant/enviro", json.dumps(values), retain=True)
        logging.info(f"Sensor values published: {values}")
    else:
        # Log error and consider retrying after a delay
        logging.warning("Failed to read sensor values. Retrying in 30 seconds...")
        time.sleep(30)

# Close bus connection before exiting (optional)
bus.close()
