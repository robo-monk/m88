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
const char* topic_subscribe = "event/microbe-on";

WiFiClient espClient;
PubSubClient client(espClient);

// ==== Microbe Buzzing Control ====
struct MicrobeControl {
  int pin;
  int dutyCycle;         // 0–100 (% time buzzing per second)
  unsigned long lastToggleTime = 0;
  bool isOn = false;
};

MicrobeControl microbes[3] = {
  {25, 0, 0, false}, // K
  {26, 0, 0, false}, // P
  {27, 0, 0, false}  // E
};

const int cycleDuration = 1000; // Total cycle duration (ms)

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

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void stimulateMicrobe(char microbe, int resistance) {
  resistance = constrain(resistance, 0, 100); // Clamp to 0–100%

  int activeIndex = -1;
  switch (toupper(microbe)) {
    case 'K': activeIndex = 0; break;
    case 'P': activeIndex = 1; break;
    case 'E': activeIndex = 2; break;
    default:
      Serial.println("Invalid microbe identifier.");
      return;
  }

  // Set the requested microbe's duty cycle
  for (int i = 0; i < 3; i++) {
    if (i == activeIndex) {
      microbes[i].dutyCycle = resistance;
      Serial.print("Microbe ");
      Serial.print(microbe);
      Serial.print(" set to ");
      Serial.print(resistance);
      Serial.println("% buzz time per second");
    } else {
      // Disable all other microbes
      microbes[i].dutyCycle = 0;
      digitalWrite(microbes[i].pin, LOW);
      microbes[i].isOn = false;
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("MQTT message received: ");
  Serial.println(message);

  int sepIndex = message.indexOf(':');
  if (sepIndex == -1) {
    Serial.println("Invalid format. Expected 'Microbe:Resistance' (e.g., K:75)");
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

  for (int i = 0; i < 3; i++) {
    pinMode(microbes[i].pin, OUTPUT);
    digitalWrite(microbes[i].pin, LOW);
  }

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long currentMillis = millis();

  for (int i = 0; i < 3; i++) {
    int value = microbes[i].dutyCycle;

    if (value == 0) {
      digitalWrite(microbes[i].pin, LOW);
      microbes[i].isOn = false;
      continue;
    }

    if (value == 100) {
      digitalWrite(microbes[i].pin, HIGH);
      microbes[i].isOn = true;
      continue;
    }

    unsigned long onTime = value * 10;
    unsigned long offTime = cycleDuration - onTime;

    if (microbes[i].isOn && currentMillis - microbes[i].lastToggleTime >= onTime) {
      digitalWrite(microbes[i].pin, LOW);
      microbes[i].isOn = false;
      microbes[i].lastToggleTime = currentMillis;
    } else if (!microbes[i].isOn && currentMillis - microbes[i].lastToggleTime >= offTime) {
      digitalWrite(microbes[i].pin, HIGH);
      microbes[i].isOn = true;
      microbes[i].lastToggleTime = currentMillis;
    }
  }
}
