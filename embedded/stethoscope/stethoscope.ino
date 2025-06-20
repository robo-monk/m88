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
  Serial.print("Initializing with %d sensors : ");
  Serial.println(COUNT_OF(photoPins));
  Serial.println("---");
}

void loop() {
  for (int i = 0; i < COUNT_OF(photoPins); i++) {
    int lightValue = analogRead(photoPins[i]);
    float voltage = lightValue * (3.3 / 4095.0);
    Serial.printf("%d:%f\n", i, voltage);
    delay(5);
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
  // Serial.println("---");

}
