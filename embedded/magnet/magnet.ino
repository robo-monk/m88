#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "pana";
const char* password = "bingbong8202";

// MQTT broker settings
const char* mqtt_server = "192.168.1.235";
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_password = "";

// MQTT topics
const char* MAGNET_ON = "event/magnet-on";
const char* MAGNET_OFF = "event/magnet-off";

// Client objects
WiFiClient espClient;
PubSubClient client(espClient);

// Variables
unsigned long lastMsg = 0;
int sensorValue = 0;

int magnetPin = 26;
int value = 2;

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  setup_wifi();
  
  // Configure MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  switch (topic) {
    case MAGNET_ON:
      Serial.println("MAGNET_ON");
      magnetValue = 0;
      break;
    case MAGNET_OFF:
      Serial.println("MAGNET_OFF");
      magnetValue = 1;
      break;
  }
  
  
  Serial.println(message);
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Create a random client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      
      // Subscribe to control topic
      client.subscribe(MAGNET_ON);
      client.subscribe(MAGNET_OFF);

      Serial.print("Subscribed to: ");
      Serial.println(MAGNET_ON);
      Serial.println(MAGNET_OFF);
      
      // Publish connection message
      client.publish("event/connected", "magnet esp");
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Publish sensor data every 10 seconds
  unsigned long now = millis();


//   if (now - lastMsg > 10000) {
    // lastMsg = now;
    
    // Simulate sensor reading
    // sensorValue = random(0, 100);
    
    // Create JSON message
    // String message = "{\"sensor\":\"temperature\",\"value\":" + String(sensorValue) + ",\"unit\":\"C\"}";
    
    // Serial.print("Publishing: ");
    // Serial.println(message);
    
    // client.publish(topic_publish, message.c_str());
    
//   }
  if (magnetValue == 0) {
    analogWrite(magnetPin, 70);
  }
  else if (magnetValue == 1) {
    analogWrite(magnetPin, 150);
  }
  if (magnetValue == 2) {
    analogWrite(magnetPin, 255);
  }
}

