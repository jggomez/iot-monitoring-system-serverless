#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include "secrets.h"

#define dhtpin 14
#define dhttype DHT22

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
        } else {
            Serial.printf("FAILED (rc=%d). Retrying in 5s...\n", client.state());
            Serial.flush();
            delay(5000);
        }
    }
}

void publishTelemetry() {
    float temp = dht.readTemperature(); 
    float hum = dht.readHumidity();

    if (isnan(hum) || isnan(temp)) {
        Serial.println("[ERROR] Failed to read from DHT sensor!");
        return;
    }

    StaticJsonDocument<200> doc;
    doc["temperature"] = temp;
    doc["humidity"] = hum;
    doc["status"] = "active";

    char buffer[256];
    serializeJson(doc, buffer);

    Serial.printf("[MQTT] Sending: %s\n", buffer);
    if (client.publish(TOPIC_SENSORS, buffer)) {
        Serial.println("[MQTT] Publish OK");
    } else {
        Serial.println("[MQTT] Publish FAILED");
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n--- SYSTEM STARTING ---");
    Serial.flush();

    dht.begin();

    setupWiFi();

    if (strlen(MQTT_SERVER) > 0) {
        client.setServer(MQTT_SERVER, 1883);
        Serial.println("[SYSTEM] MQTT Server initialized.");
    } else {
        Serial.println("[ERROR] MQTT_SERVER is empty in secrets.h!");
    }
}

void loop() {
    if (!client.connected()) {
        reconnectMQTT();
    }
    client.loop();

    unsigned long currentTime = millis();
    if (currentTime - lastPublishTime > PUBLISH_INTERVAL) {
        lastPublishTime = currentTime;
        publishTelemetry();
    }
}