from state import State
from paho.mqtt import client as mqtt_client
import pandas as pd


data = pd.read_csv("components/bottles/data.csv")

def run_bottles(state: State, client: mqtt_client.Client):
    selected_data = data[(data["year"] == state.year) & (data["country"] == state.country.to_camelcase())]
    if not selected_data.empty:
        magnet_strength = selected_data["magnet_strength"].values[0]
        client.publish("setvar/magnet-strength", str(magnet_strength))
    else:
        print(f"[!] No data found for year {state.year} and country {state.country.name}")
