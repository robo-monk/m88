from enum import Enum
from threading import Thread
import time
from components import vibration_microbe
from components.bottles.bottles import run_bottles
from components.stethoscope import run as run_stethoscope
from dataclasses import dataclass
from components.tiny_population import run_tiny_population
from state import Bacteria, Country, state
from mqtt import mqtt_client
from components.stethoscope import run as steth_run



# netherlands spain bulgaria
# Year = Enum("Year", ["_2025", "_2026", "_2027"])
# Country = Enum("Country", ["NL", "ES", "BG"])
# Bacteria = Enum("Bacteria", ["PSEUDO", "KLEBSIA", "ECOLI"])

def sync_state():
    print(f"Syncing state: {state}")
    for component in [
        # vibration_microbe,
        # run_tiny_population,
        run_bottles,
    ]:
        try:
            component(state, mqtt_client)
        except Exception as e:
            print(f"[!] Error running component {component.__name__}: {e}")
    # vibration_microbe(state, mqtt_client)
    # run_tiny_population(state, mqtt_client)
    # run_bottles(state, mqtt_client)

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
                sync_state()

            case "event/stop-installation":
                print("Stop INSTALLATION")
    except:
        print("Error unpacking message")


def test_mqtt():
    import time
    time.sleep(1)
    while True:
        print("-$- PRESS ENTER TO SEND MESSAGE -$-")
        input()
        data = input("Enter MQTT topic and payload: ")
        topic, payload = data, ""
        if data.find(" ") != -1: 
            topic, payload = data.split(" ")

        mqtt_client.publish(topic, payload)
        print("Message published")


# def start_mqtt():
#     mqtt_client.loop_start()

Thread(target=test_mqtt).start()
# Thread(target=start_mqtt).start()
# Thread(target=steth_run, args=(mqtt_client, False)).start()


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect


# test_state = State()
state.bacteria = Bacteria.ECOLI
state.country = Country.ES
state.year = 2016