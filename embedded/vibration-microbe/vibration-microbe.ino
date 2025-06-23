#include <WiFi.h>
#include <PubSubClient.h>

// ====== WiFi Credentials ======
const char* ssid = "pana";
const char* password = "bingbong8202";

// ====== MQTT Settings ======
const char* mqtt_server = "192.168.1.235";
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_password = "";

const char* topic_publish = "esp32/sensor";
const char* topic_subscribe = "esp32/control";

WiFiClient espClient;
PubSubClient client(espClient);

// Use GPIO numbers directly for ESP32
const int pinA = 25;  // Microbe A → GPIO5
const int pinB = 26;  // Microbe B → GPIO4
const int pinC = 27;  // Microbe C → GPIO0

int currentPWMpin = -1;

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
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void stimulateMicrobe(char microbe, int resistance) {
  resistance = constrain(resistance, 0, 100); // clamp to 0–100

  // Determine output pin
  int selectedPin = -1;
  switch (toupper(microbe)) {
    case 'A': selectedPin = pinA; break;
    case 'B': selectedPin = pinB; break;
    case 'C': selectedPin = pinC; break;
    default:
      Serial.println("Invalid microbe identifier.");
      return;
  }

  // Reset other PWM pins
  analogWrite(pinA, 0);
  analogWrite(pinB, 0);
  analogWrite(pinC, 0);

  // Convert resistance to PWM duty (0–1023 for ESP8266)
  int duty = map(resistance, 0, 100, 0, 1023);
  analogWrite(selectedPin, duty);

  Serial.print("Microbe ");
  Serial.print(microbe);
  Serial.print(" on pin ");
  Serial.print(selectedPin);
  Serial.print(" stimulated with duty ");
  Serial.println(duty);
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("MQTT message received: ");
  Serial.println(message);

  // Expecting format like "A:75"
  int sepIndex = message.indexOf(':');
  if (sepIndex == -1) {
    Serial.println("Invalid format. Expected 'Microbe:Resistance' (e.g., A:75)");
    return;
  }

  char microbe = message.charAt(0);
  int resistance = message.substring(sepIndex + 1).toInt();

  stimulateMicrobe(microbe, resistance);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESPClient-" + String(random(0xffff), HEX);

    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(topic_subscribe);
      client.publish(topic_publish, "ESP connected and listening");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" — retrying in 5s");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Set pin modes
  pinMode(pinA, OUTPUT);
  pinMode(pinB, OUTPUT);
  pinMode(pinC, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // You could publish sensor data here if desired
}
