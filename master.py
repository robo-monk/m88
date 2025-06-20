from enum import Enum
from threading import Thread
import time
from components.stethoscope import run as run_stethoscope
from dataclasses import dataclass
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import CallbackAPIVersion

BROKER_HOST = "192.168.1.235"
BROKER_PORT = 1883


# netherlands spain bulgaria
# Year = Enum("Year", ["_2025", "_2026", "_2027"])
Country = Enum("Country", ["NL", "ES", "BG"])
Bacteria = Enum("Bacteria", ["STAPH", "SALMONELLA", "ECOLI"])

@dataclass
class State:
    year: int | None = None
    country: Country | None = None
    bacteria: Bacteria | None = None


state = State()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#")

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")


def on_message(client, userdata, message):
    print(f"Received message: {message.topic} {message.payload}")

    try:
        data = message.payload.decode()
        match message.topic:
            case "setvar/year":
                state.year = int(data)
            case "setvar/country":
                if len(data) < 2:
                    state.country = None
                else:
                    state.country = Country(data)
            case "setvar/bacteria":
                state.bacteria = Bacteria(data)
            case "event/start":
                print("Start EVENT")
            case "event/stop-installation":
                print("Stop INSTALLATION")
    except:
        print("Error unpacking message")            


client = mqtt_client.Client(CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_forever()

# try:
#     client.connect(BROKER_HOST, BROKER_PORT, 60)
#     client.loop_start()

#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     client.loop_stop()
#     client.disconnect()
# finally:
#     client.loop_stop()
#     client.disconnect()