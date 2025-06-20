#include <WiFi.h>
#include <PubSubClient.h>
#include <stdlib.h>

// WiFi credentials
const char* ssid = "pana";
const char* password = "bingbong8202";

// MQTT broker settings
const char* mqtt_server = "192.168.1.235";
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_password = "";

// MQTT topics
// const char* topic_subscribe = "esp32/control";

// Client objects
WiFiClient espClient;
PubSubClient client(espClient);

int sliderPin = 13;
int year;
int NL_button = 17;
int ES_button = 16;
int BG_button = 4;
String country;
int NL_LED = 12;
int ES_LED = 14;
int BG_LED = 27;
void setup() {

  Serial.begin(115200);
  // Connect to WiFi
  setup_wifi();
  // Configure MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // put your setup code here, to run once:
  pinMode(sliderPin, INPUT);
  pinMode(NL_button, INPUT_PULLUP);
  pinMode(ES_button, INPUT_PULLUP);
  pinMode(BG_button, INPUT_PULLUP);
  pinMode(NL_LED, OUTPUT);
  pinMode(ES_LED, OUTPUT);
  pinMode(BG_LED, OUTPUT);
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
      // client.subscribe(topic_subscribe);
      // Serial.print("Subscribed to: ");
      // Serial.println(topic_subscribe);

      // Publish connection message

      client.publish("event/connected", "slider esp");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

const int RATE_LIMIT_MS = 1000;
int lastMsgMs = -1;

void publish_state() {
  unsigned long now = millis();
  if (lastMsgMs != -1 && now - lastMsgMs < RATE_LIMIT_MS) {
    return;
  }
  lastMsgMs = now;

  Serial.print("Publishing state: ");
  Serial.print(year);
  Serial.print(',');
  Serial.println(country);

  char yearStr[6];
  itoa(year, yearStr, 10); // convert int year to C-string
  client.publish("setvar/year", yearStr);

  client.publish("setvar/country", country.c_str());
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  float voltage = analogRead(sliderPin);
  // voltage = voltage * 5 / 4095;
  if (voltage <= 0.35) {
    year = 2006;
  }
  if (voltage > 0.35 && voltage <= 1.20) {
    year = 2011;
  }
  if (voltage > 1.20 && voltage <= 3.00) {
    year = 2016;
  }
  if (voltage > 3.0) {
    year = 2021;
  }
  if (digitalRead(NL_button) == LOW) {
    country = "NL";
    digitalWrite(NL_LED, HIGH);
    digitalWrite(ES_LED, LOW);
    digitalWrite(BG_LED, LOW);
  }
  if (digitalRead(ES_button) == LOW) {
    country = "ES";
    digitalWrite(NL_LED, LOW);
    digitalWrite(ES_LED, HIGH);
    digitalWrite(BG_LED, LOW);
  }
  if (digitalRead(BG_button) == LOW) {
    country = "BG";
    digitalWrite(NL_LED, LOW);
    digitalWrite(ES_LED, LOW);
    digitalWrite(BG_LED, HIGH);
  }

  Serial.print(voltage);
  Serial.print(',');
  Serial.print(year);
  Serial.print(',');
  Serial.println(country);

  publish_state();
}
