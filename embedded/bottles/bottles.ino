#include <SPI.h>
#include <MFRC522.h>
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

WiFiClient espClient;
PubSubClient client(espClient);

// NFC
#define SS_PIN 5
#define RST_PIN 21
#define BUTTON_PIN 13

int tag = 0;

// magnets
int magnetPin = 26;
int magnetValue = 2;

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
    // Connect to WiFi
  setup_wifi();
  
  // Configure MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("Scan an RFID tag...");

  pinMode(BUTTON_PIN, INPUT_PULLUP); 
  pinMode(magnetPin, OUTPUT);
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  if (strcmp(topic, MAGNET_ON) == 0) {
    Serial.println("MAGNET_ON");
    // we expect message magnetValue
    magnetValue = message.toInt();
  } else if (strcmp(topic, MAGNET_OFF) == 0) {
    Serial.println("MAGNET_OFF");
    magnetValue = -1; // Set to -1 to indicate off state
  }
  
  Serial.println(message);
}


void loop() {
 if (!client.connected()) {
    reconnect();
  }
  client.loop();

  //magnets
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Read until newline
    magnetValue = input.toInt();
    Serial.println(magnetValue);
  }
  if (magnetValue == 0) {
    analogWrite(magnetPin, 70);
  } else if (magnetValue == 1) {
    analogWrite(magnetPin, 150);
  } else if (magnetValue == 2) {
    analogWrite(magnetPin, 255);
  } else {
    analogWrite(magnetPin, 0); // Turn magnet off for any other value
  }

  //NFC
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  // Tag #1 - 51 - Ecoli
  // Tag #2 - 35 - Pseudo
  // Tag #3 - 83 - Klebsia
  tag = mfrc522.uid.uidByte[0];

  if (tag == 51) {
    // send Ecoli
      client.publish("setvar/bacteria", "ECOLI");
  } else if (tag == 35) {
    // send Pseudo
    client.publish("setvar/bacteria", "PSEUDO");
  } else if (tag == 83) {
    // send Klebsia
    client.publish("setvar/bacteria", "KLEBSIA");
  }

  Serial.print("Tag UID: ");
  Serial.print(mfrc522.uid.uidByte[0]);
  Serial.println();

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  //Button
  if (digitalRead(BUTTON_PIN) == LOW) {
    client.publish("event/start", "");
    delay(500); 
  }
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
