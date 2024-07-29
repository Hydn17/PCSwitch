import time
import gc
import machine
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Setup the onboard LED so we can turn it on/off
signal = Pin(0, Pin.OUT)
PLED = Pin("LED", Pin.OUT)
YLED = Pin(17, Pin.OUT)
RLED = Pin(16,Pin.OUT)

PLED.value(1)

# Fill in your WiFi network name (ssid) and password here:
wifi_ssid = ""
wifi_password = ""

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)

count = 0

while wlan.isconnected() == False:
    print('Waiting for connection...')
    RLED.toggle()
    time.sleep(1)
    count += 1
    if count == 180:
        machine.reset()
print("Connected to WiFi")

# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "io.adafruit.com"
mqtt_username = ""  # Your Adafruit IO username
mqtt_password = ""  # Adafruit IO Key
mqtt_receive_topic = ""  # The MQTT topic for your Adafruit IO Feed

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = ""

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
    client_id=mqtt_client_id,
    server=mqtt_host,
    user=mqtt_username,
    password=mqtt_password)


# So that we can respond to messages on an MQTT topic, we need a callback
# function that will handle the messages.
def mqtt_subscription_callback(topic, message):
    print(f'Topic {topic} received message {message}')  # Debug print out of what was received over MQTT
    if message == b'on':
        print("PC ON")
        signal.value(1)
        time.sleep(0.5)
        signal.value(0)
        mqtt_client.publish(mqtt_receive_topic, "off")


# Before connecting, tell the MQTT client to use the callback
mqtt_client.set_callback(mqtt_subscription_callback)
mqtt_client.set_last_will(mqtt_receive_topic, "I died.")
mqtt_client.connect()

# Once connected, subscribe to the MQTT topic
mqtt_client.subscribe(mqtt_receive_topic)
print("Connected and subscribed")

YLED.value(0)
RLED.value(0)
fourHrCheck = time.ticks_ms()
start = fourHrCheck
try:
    while True:
        # Infinitely wait for messages on the topic.
        # Note wait_msg() is a blocking call, if you're doing multiple things
        # on the Pico you may want to look at putting this on another thread.
        time.sleep(2)
        print(f'Waiting for messages on {mqtt_receive_topic} ', time.ticks_diff(time.ticks_ms(), start))
        if wlan.isconnected():
            YLED.value(1)
        else:
            YLED.value(0)
        mqtt_client.check_msg()
        if time.ticks_diff(time.ticks_ms(), start) > 200000:
            mqtt_client.ping()
            start = time.ticks_ms()
            print("pinged client")
        elif time.ticks_diff(time.ticks_ms(), fourHrCheck) > 43200000:
            machine.reset()

        #mqtt_client.wait_msg()
except Exception as e:
    print(f'Failed to wait for MQTT messages: {e}')
finally:
    mqtt_client.disconnect()
    print("Free memory: ", gc.mem_free())
    machine.reset()
