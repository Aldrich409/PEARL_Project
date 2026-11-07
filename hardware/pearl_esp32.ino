#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h> // ✅ Added missing JSON library

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
// Change this to your laptop's local IPv4 address (e.g., 192.168.1.X)
const char* serverUrl = "http://192.168.69.32:8000/api/telemetry";
const String deviceSN = "PEARL-ESP32-001";

#define ONE_WIRE_BUS 4
#define PH_PIN 34
#define TURB_PIN 35
#define TRIG_PIN 5
#define ECHO_PIN 18

// ✅ Deep Sleep settings (30 minutes)
#define uS_TO_S_FACTOR 1000000ULL
#define TIME_TO_SLEEP  1800 

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  tempSensor.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi Connected!");

  // --- READ SENSORS ---
  tempSensor.requestTemperatures();
  float tempC = tempSensor.getTempCByIndex(0);
  
  int phRaw = analogRead(PH_PIN);
  float phValue = (phRaw * 3.3 / 4095.0) * 3.5; 

  int turbRaw = analogRead(TURB_PIN);
  float turbValue = turbRaw * (100.0 / 4095.0);

  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  float distanceCm = duration * 0.034 / 2;

  // --- SEND DATA ---
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  // Allocate JSON document
  StaticJsonDocument<200> doc;
  doc["device_sn"] = deviceSN;
  doc["temperature"] = tempC;
  doc["ph"] = phValue;
  doc["turbidity"] = turbValue;
  doc["water_level_cm"] = distanceCm;

  String requestBody;
  serializeJson(doc, requestBody);
  int httpResponseCode = http.POST(requestBody);
  
  Serial.print("HTTP POST Status: ");
  Serial.println(httpResponseCode);
  http.end();

  // --- ENTER TRUE DEEP SLEEP ---
  Serial.println("Going to sleep for 30 minutes...");
  WiFi.disconnect(true); // Turn off WiFi to save power
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  esp_deep_sleep_start();
}

void loop() {
  // ✅ Loop remains empty because the ESP32 resets upon waking from deep sleep
}