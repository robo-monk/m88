# connect to mqtt 


import paho.mqtt.client as mqtt
import time

# Replace with your Raspberry Pi's IP address
BROKER_HOST = "192.168.1.235"  # Your Pi's IP
BROKER_PORT = 1883

# client.publish("setvar/year", 2006)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        # Subscribe to all topics
        client.subscribe("#")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")

# Create MQTT client
client = mqtt.Client()

# Set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# If using username/password:
# client.username_pw_set("username", "password")

try:
    # Connect to broker
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    
    # Start the loop to process callbacks
    client.loop_start()
    
    # Publish some test messages
    for i in range(5):
        message = f"Hello from Python client - {i}"
        client.publish("bingbong", message)
        print(f"Published: {message}")
        time.sleep(2)
    
    # Keep the script running to receive messages
    print("Listening for messages... Press Ctrl+C to exit")
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.loop_stop()
    client.disconnect()