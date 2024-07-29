# PCSwitch
Simple relay to turn on a pc remotely via a command sent over MQTT
Scans an MQTT topic for a command and once received, briefly switches a signal pin on and then off, simulating a power button press.

My implementation used a raspberry pi pico w but any micro-contoller with WIFI and micropython support would suffice. 

Before implementation rename the file to main.py for it to be executed on boot of pico.
This project is dependent on umqtt.simple for the mqtt connection and made use of code from Core Electronics: getting started with MQTT on Pico guide.
