# Python receiver script for continuous hit monitoring
import argparse
import serial
import serial.tools.list_ports
import time
import os
from time import sleep
import threading
import numpy as np
import json
import pygame
from paho.mqtt import client as mqtt_client
import pandas as pd
from state import Bacteria, Country, state

OUTPUT_DIR = "components/stethoscope/thresholds"

df = pd.read_csv("components/stethoscope/body_sounds.csv")

def user_select_port():
    port = ""
    ports = list(serial.tools.list_ports.comports())
    print("Available ports:")
    for i, p in enumerate(ports):
        print(f"{i}: {p.device} - {p.description}")
    if ports:
        idx = int(input("Select port: "))
        port = ports[idx].device
    else:
        port = input("Enter port manually: ")

    print("Using port :: ", port)
    return port

 # Create output directory if it doesn't exist
 # os.makedirs(output_dir, exist_ok=True)

 # # Configure serial connection
 # ser = serial.Serial(port, 921600, timeout=10)
 # print(f"Connected to {port} at 921600 baud")

 # # Wait for initial message
 # print("Waiting for ESP32...")
 # while True:
 #     line = ser.readline().decode('utf-8', errors='ignore').strip()
 #     print(f"Received: {line}")
 #     if "MPU6050 initialized" in line:
 #         break

 # hit_count = 0
 #


BUFFERS_LEN = 25
sensor_values = {}
sensor_baselines = {}
sensor_thresholds = {}
sensor_mappings = {}
sensor_positions = {}
sensor_counts = {}

# Global level variable (1-4)
# level = 4

# Sound management
pygame.mixer.init()
current_sound = None
current_sound_channel = None
last_active_sensor = None

def play_sensor_sound(sensor_alias):
    """Play sound for a specific sensor based on current level"""
    global current_sound, current_sound_channel, last_active_sensor

    # If the same sensor is still active and sound is playing, do nothing
    if (last_active_sensor == sensor_alias and
        current_sound_channel and current_sound_channel.get_busy()):
        return

    # Stop any currently playing sound
    if current_sound_channel and current_sound_channel.get_busy():
        current_sound_channel.stop()

    print("finding level for ", state.bacteria, state.year, state.country)
    # find where Pathogen = state.bacteria and Year = state.year and get [sensor_alias] column
    row_df = df.loc[(df["Pathogen"] == state.bacteria.to_capitalized()) & (df["Year"] == state.year) & (df["Location"] == state.country.to_camelcase())]

    if row_df.empty:
        print(f"Warning: no entry found for {state.bacteria}, {state.year}, {state.country.to_camelcase()}")
        return

    raw_level = row_df[sensor_alias].iloc[0]
    
    print(f"Raw level for {sensor_alias}: {raw_level}")

    # if raw_level == 0:
    stop_all_sounds()
        # return

    # The rank is from 1 to 12, we need to map it to a sound level from 1 to 4
    # Level 1: 1-3, Level 2: 4-6, Level 3: 7-9, Level 4: 10-12
    # level = ((raw_level - 1) // 3) + 1
    level = max(min(raw_level // 4, 1), 4)
    print("sound level is: ", level)
    
    assert level in [1, 2, 3, 4], f"Calculated level {level} is not valid"

    # Load and play the new sound
    sound_file = f"components/stethoscope/sounds/{sensor_alias}/{sensor_alias}Level{level}.wav"
    if os.path.exists(sound_file):
        try:
            current_sound = pygame.mixer.Sound(sound_file)
            current_sound_channel = pygame.mixer.Channel(0)
            current_sound_channel.set_volume(2.5)
            current_sound_channel.play(current_sound)
            last_active_sensor = sensor_alias
            print(f"Playing: {sound_file}")
        except pygame.error as e:
            print(f"Error playing sound {sound_file}: {e}")
    else:
        print(f"Sound file not found: {sound_file}")

def stop_all_sounds():
    """Stop all currently playing sounds"""
    global current_sound_channel, last_active_sensor
    if current_sound_channel and current_sound_channel.get_busy():
        current_sound_channel.stop()
    last_active_sensor = None


def add_sensor_value(sensor_index, sensor_value):
    # Initialize sensor if it doesn't exist
    if sensor_index not in sensor_values:
        sensor_values[sensor_index] = np.zeros(BUFFERS_LEN)
        sensor_positions[sensor_index] = 0
        sensor_counts[sensor_index] = 0

    # Add the new value at the current position
    sensor_values[sensor_index][sensor_positions[sensor_index]] = sensor_value

    # Update position (circular buffer)
    sensor_positions[sensor_index] = (sensor_positions[sensor_index] + 1) % BUFFERS_LEN

    # Track how many values we've added (up to BUFFERS_LEN)
    if sensor_counts[sensor_index] < BUFFERS_LEN:
        sensor_counts[sensor_index] += 1

def get_sensor_values(sensor_index):
    """Get the sensor values in chronological order (oldest to newest)"""
    if sensor_index not in sensor_values:
        return np.array([])

    arr = sensor_values[sensor_index]
    pos = sensor_positions[sensor_index]
    count = sensor_counts[sensor_index]

    if count < BUFFERS_LEN:
        # Array not full yet, return only the filled portion
        return arr[:count]
    else:
        # Array is full, return in chronological order
        return np.concatenate([arr[pos:], arr[:pos]])



def mqtt_parser(client: mqtt_client.Client):
    # client.subscribe("setvar/light-value")
    def on_message(client, userdata, message):
        # print("-> stetho message", message)
        if message.topic == "setvar/light-value":
            values = message.payload.decode().split(",")
            for i, value in enumerate(values):
                if len(value) > 0:
                    add_sensor_value(i, float(value))

    client.message_callback_add("setvar/light-value", on_message)
    client.on_message = on_message
    # client.loop_start()

def serial_parser(port, baudrate):
    print("Initialising serial parser with at", port, baudrate)
    ser = serial.Serial(port, baudrate, timeout=10)
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        try:
            sensor_index, value = line.split(":")
            add_sensor_value(int(sensor_index), value)
        except:
            pass;

        # print(line);

def get_current_sensor_state(last_n=4, tolerance=0.7):
    state = {}
    for i, sv in sensor_values.items():
        last_mean = sv[-last_n:].mean()
        # print("i -> ", last_mean)
        state[i] = last_mean < (sensor_baselines[i] - sensor_thresholds[i]*tolerance)

    # print("---")

    return state


STATE_FILE = "sensor_state.json"
def save_sensor_state():
    """Save sensor baselines, thresholds, and mappings to JSON file"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    state = {
        "sensor_baselines": sensor_baselines,
        "sensor_thresholds": sensor_thresholds,
        "sensor_mappings": sensor_mappings
    }

    state_file_path = os.path.join(OUTPUT_DIR, STATE_FILE)
    with open(state_file_path, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"Sensor state saved to {state_file_path}")

def load_sensor_state():
    """Load sensor baselines, thresholds, and mappings from JSON file"""
    global sensor_baselines, sensor_thresholds, sensor_mappings

    state_file_path = os.path.join(OUTPUT_DIR, STATE_FILE)
    if not os.path.exists(state_file_path):
        return False

    try:
        with open(state_file_path, 'r') as f:
            state = json.load(f)

        # Convert string keys back to integers for sensor indices
        sensor_baselines = {int(k): v for k, v in state.get("sensor_baselines", {}).items()}
        sensor_thresholds = {int(k): v for k, v in state.get("sensor_thresholds", {}).items()}
        sensor_mappings = {int(k): v for k, v in state.get("sensor_mappings", {}).items()}

        print(f"Sensor state loaded from {state_file_path}")
        print(f"Loaded {len(sensor_baselines)} baselines, {len(sensor_thresholds)} thresholds, {len(sensor_mappings)} mappings")

        # Display loaded configuration
        print("\nLoaded sensor configuration:")
        for sensor_id in sensor_mappings:
            alias = sensor_mappings.get(sensor_id, f"Sensor_{sensor_id}")
            baseline = sensor_baselines.get(sensor_id, "N/A")
            threshold = sensor_thresholds.get(sensor_id, "N/A")
            print(f"  {alias} (ID: {sensor_id}) - Baseline: {baseline:.2f}, Threshold: {threshold:.2f}")

        return True
    except Exception as e:
        print(f"Error loading sensor state: {e}")
        return False

def wait_for_buffers_to_fill():
    start_time = time.time()
    print("waiting for buffers to fill...")
    sleep(0.25)
    while True:
        if not sensor_values or any(sensor_counts[i] < BUFFERS_LEN for i in sensor_counts):
            continue
        break
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Buffers filled in {elapsed_time:.2f} seconds")
    total_values = len(sensor_counts.values()) * BUFFERS_LEN
    print(f"Got {total_values} values in {elapsed_time:.2f} seconds")
    hz_per_buffer = BUFFERS_LEN / elapsed_time
    print(f"Hz per buffer: {hz_per_buffer:.2f}")

def calibrate():
    print("Calibrating...")
    os.makedirs(OUTPUT_DIR, exist_ok = True)

    sensors_aliases = ["Throat", "Heart", "Lungs", "Bowel"]
    wait_for_buffers_to_fill()

    print("calibrating...")
    # print("Evaluating", alias, "sensor")
    # state = get_current_sensor_state()
    # for i, sv in sensor_values.items():
    for i, sv in sensor_values.items():
        general_mean = sv.mean()
        print(i, "-> GEN MEAN", general_mean)
        sensor_baselines[i] = general_mean

    for alias in sensors_aliases:
        print("Please cover: ", alias, "sensor (and press enter)")

        input()
        # Calculate differences between baselines and current means

        differences = {i: sensor_baselines[i] - get_sensor_values(i)[-10:].mean() for i in sensor_values.keys()}
        print("Differences:", list(differences.values()))

        max_index = max(differences, key=differences.get)
        print(get_sensor_values(max_index)[-10:])

        max_difference = differences[max_index]
        print(f"Largest difference: {max_difference} at sensor index {max_index}")
        # thres = max_difference * tolerance
        print("Using ", max_difference, "as threshold")
        sensor_thresholds[max_index] = max_difference
        sensor_mappings[max_index] = alias

    # Save the calibrated state
    save_sensor_state()
    print("Calibration complete! Sensor state has been saved.")


def run(client, _calibrate=False):
    print("Starting monitoring with loaded sensor state...")
    serial_thread = threading.Thread(target=mqtt_parser(client))
    serial_thread.start()
    wait_for_buffers_to_fill()

    if _calibrate:
        calibrate()

    if not load_sensor_state():
        print("No calibrated sensor state found!")
        print("Please run the calibrate command first:")
        # print(f"python {__file__} calibrate -p {port}")
        exit(1)

    # Validate that we have complete sensor configuration
    if not sensor_baselines or not sensor_thresholds or not sensor_mappings:
        print("Incomplete sensor configuration loaded!")
        print("Please recalibrate by running:")
        # print(f"python {__file__} calibrate -p {port}")
        exit(1)



    # Main monitoring loop
    try:
        while True:
            if sensor_values:
                state = get_current_sensor_state()
                active_sensors = {sensor_mappings.get(i, f"Sensor_{i}"): active
                                for i, active in state.items() if active}

                if active_sensors:
                    # Get the first active sensor
                    active_sensor_alias = list(active_sensors.keys())[0]
                    print(f"Active: {list(active_sensors.keys())}")
                    play_sensor_sound(active_sensor_alias)
                else:
                    # No sensors active, stop all sounds
                    stop_all_sounds()

                # Check if current sound finished and sensor is still active
                if (last_active_sensor and
                    current_sound_channel and not current_sound_channel.get_busy() and
                    active_sensors.get(last_active_sensor, False)):
                    # Restart the sound
                    play_sensor_sound(last_active_sensor)

            sleep(0.1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")




# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Stethoscope simulator")
#     parser.add_argument("command", nargs="?", help="calibrate | run | status")
#     parser.add_argument("-p", "--port", help="Serial port to use (e.g., COM3)")
#     parser.add_argument("-b", "--baudrate", help="Baudrate to use (defaults to 115200)", default=115200)
#     args = parser.parse_args()

#     port = args.port
#     if not port:
#         port = user_select_port()

#     serial_thread = threading.Thread(target=serial_parser, args=(port, args.baudrate))
#     # serial_parser(port, args.baudrate)

#     if args.command == "calibrate":
#         print("Initializing calibrating sequence")
#         serial_thread.start()
#         print("Waiting for baseline values...")
#         calibrate()
#     elif args.command == "run":
#         print("Loading sensor state...")
#         run()
#     elif args.command == "status":
#         print("Checking sensor calibration status...")
#         if load_sensor_state():
#             print("✓ Sensor calibration found and loaded successfully")
#         else:
#             print("✗ No sensor calibration found")
#             print("Please run the calibrate command first:")
#             print(f"python {__file__} calibrate")

#     else:
#         print("Command not supported: ", args.command)
#         parser.print_help()

