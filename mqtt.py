from threading import Thread
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import CallbackAPIVersion

BROKER_HOST = "192.168.1.235"
BROKER_PORT = 1883


mqtt_client = mqtt_client.Client(CallbackAPIVersion.VERSION2)
mqtt_client.connect(BROKER_HOST, BROKER_PORT, 60)
Thread(target=mqtt_client.loop_forever).start()
