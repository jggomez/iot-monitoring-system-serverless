#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include "secrets.h"

#define dhtpin 12
#define dhttype DHT22

const int PIN_LED = 32;

DHT dht(dhtpin, dhttype);

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastPublishTime = 0;
const long PUBLISH_INTERVAL = 5000;

void setupWiFi() {
    delay(10);
    Serial.printf("\n[WIFI] Connecting to: %s\n", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int timeout_counter = 0;
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        timeout_counter++;
        if(timeout_counter > 40) ESP.restart();
    }

    Serial.println("\n[WIFI] Connected!");
    Serial.printf("[WIFI] IP: %s\n", WiFi.localIP().toString().c_str());
}

void reconnectMQTT() {
    while (!client.connected()) {
        Serial.print("[MQTT] Attempting connection... ");
        Serial.flush(); 

        if (client.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS)) {
            Serial.println("CONNECTED");
            client.subscribe(TOPIC_COMMANDS);
        } else {
            Serial.printf("FAILED (rc=%d). Retrying in 5s...\n", client.state());
            Serial.flush();
            delay(5000);
        }
    }
}

void publishTelemetry() {
    // 1. Read real data
    float temp = dht.readTemperature(); 
    float hum = dht.readHumidity();

    if (isnan(hum) || isnan(temp)) {
        Serial.println("[ERROR] Failed to read from DHT sensor!");
        return;
    }

    // 2. Build JSON Object
    StaticJsonDocument<200> doc;
    doc["temperature"] = temp;
    doc["humidity"] = hum;
    doc["status"] = "active";

    // 3. Serialize
    char buffer[256];
    serializeJson(doc, buffer);

    // 4. Publish
    Serial.printf("[MQTT] Sending: %s\n", buffer);
    if (client.publish(TOPIC_SENSORS, buffer)) {
        Serial.println("[MQTT] Publish OK");
    } else {
        Serial.println("[MQTT] Publish FAILED");
    }
}

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.printf("\n[MQTT] Topic Callback: %s\n", topic);
    
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload, length);

    if (error) {
        Serial.print("[JSON] Error parsed: ");
        Serial.println(error.f_str());
        return;
    }

    const char* status = doc["status"]; 

    if (status) { 
        Serial.printf("[JSON] Status: %s\n", status);

        if (strcmp(status, "ON") == 0) {
            Serial.println(">>> (LED HIGH)...");
            digitalWrite(PIN_LED, HIGH);
        } 
        else if (strcmp(status, "OFF") == 0) {
            Serial.println(">>> (LED LOW)...");
            digitalWrite(PIN_LED, LOW);
        }
    } else {
        Serial.println("[JSON] 'status' not found");
    }
}

void setup() {
    // Higher baud rate for debugging
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n--- SYSTEM STARTING ---");
    Serial.flush(); 

    pinMode(PIN_LED, OUTPUT);

    for(int i=0; i<3; i++){
        digitalWrite(PIN_LED, HIGH);
        delay(200);
        digitalWrite(PIN_LED, LOW);
        delay(200);
    }

    dht.begin();
    delay(3000);
    setupWiFi();


    // Verify MQTT server string isn't null
    if (strlen(MQTT_SERVER) > 0) {
        client.setServer(MQTT_SERVER, 1883);
        client.setCallback(callback);
        Serial.println("[SYSTEM] MQTT Server initialized.");
    } else {
        Serial.println("[ERROR] MQTT_SERVER is empty in secrets.h!");
    }
}

void loop() {
    // Keep connection alive
    if (!client.connected()) {
        reconnectMQTT();
    }
    client.loop();

    // Non-blocking timer
    unsigned long currentTime = millis();
    if (currentTime - lastPublishTime > PUBLISH_INTERVAL) {
        lastPublishTime = currentTime;
        publishTelemetry();
    }
}
