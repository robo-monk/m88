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

WiFiClient espClient;
PubSubClient client(espClient);

#define COUNT_OF(x)                                                            \
  ((sizeof(x) / sizeof(0 [x])) / ((size_t)(!(sizeof(x) % sizeof(0 [x])))))

// Body location to GPIO numbers
typedef enum {
  CHEST = 34,
  THROAT = 35,
  LEFT_RIB = 32,
  RIGHT_RIB = 33,
} BodyPart;

BodyPart photoPins[] = {CHEST, THROAT, LEFT_RIB, RIGHT_RIB};

void setup() {
  Serial.begin(115200);
  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);

  Serial.print("Initializing with %d sensors : ");
  Serial.println(COUNT_OF(photoPins));
  Serial.println("---");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  String message = "";
  for (int i = 0; i < COUNT_OF(photoPins); i++) {
    int lightValue = analogRead(photoPins[i]);
    float voltage = lightValue * (3.3 / 4095.0);
    Serial.printf("%d:%f\n", i, voltage);

    message += String(voltage) + ",";

    // hell

    // Serial.print("Sensor ");
    // Serial.print(i + 1);
    // Serial.print(" (GPIO");
    // Serial.print(photoPins[i]);
    // Serial.print("): ");
    // Serial.print(lightValue);
    // Serial.print(" | ");
    // Serial.print(voltage);
    // Serial.println("V");
  }

  client.publish("setvar/light-value", message.c_str());
  delay(50);
  // Serial.println("---");

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
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESPClient-" + String(random(0xffff), HEX);

    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      // client.subscribe(topic_microbe_on);
      client.publish("stethoscope/connected", "ESP connected and listening");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" — retrying in 5s");
      delay(5000);
    }
  }
}