import paho.mqtt.client as mqtt
from paho.mqtt import enums
from paho.mqtt import reasoncodes
import time
import json
from subprocess import PIPE, Popen, check_output
from bme280 import BME280
import logging
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

# Set an initial update time
update_time = time.time()
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logging.info(msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid):
    logging.info("mid: " + str(mid))

client = mqtt.Client(callback_api_version=enums.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("mosquitto", "mosquitto")
client.connect("homeassistant", 1883, 60)



def read_bme280(bme280):
    values = {}
    raw_temp = bme280.get_temperature()  # float
    #TODO: temperature should be compensated due to proximity to cpu
    comp_temp = raw_temp 
    values["temperature"] = int(comp_temp)
    values["temperature_has_been_compensated"] = False
    values["pressure"] =  int(bme280.get_pressure())
    values["humidity"] = int(bme280.get_humidity())
    return values

client.loop_start()
while True:
    try:
        bus = SMBus(1)
        # Create BME280 instance
        bme280 = BME280(i2c_dev=bus)
        values = read_bme280(bme280)
        
        time_since_update = time.time() - update_time
        if time_since_update >= 5:
            update_time = time.time()
            logging.info(values)
            client.publish("homeassistant/enviro", json.dumps(values), retain=True)
    except Exception as e:
        logging.exception(e)

