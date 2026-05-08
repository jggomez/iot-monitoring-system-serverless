# IoT Sensor Data Pipeline & Dashboard

## Project Description
This project implements a real-time IoT sensor data pipeline and visualization architecture. It connects, processes, and streams real-time data from devices to cloud analytics and dynamic dashboards. Massive IoT data is turned into actionable intelligence by routing messages through a unified MQTT platform to Google Cloud and Firebase services for both real-time monitoring and historical analysis.

## Architecture

The system follows an event-driven architecture, capturing sensor data via MQTT and processing it through scalable cloud services.

```mermaid
flowchart TD
    A[IoT Devices] -->|MQTT| B[EMQX Platform]
    B -->|Flow| C[GCP Pub/Sub]
    
    C -->|Subscription| D[Cloud Run Service]
    C -->|Subscription| E[GCP BigQuery]
    
    D -->|Stores Data| F[(Firestore)]
    
    F -->|Real-time Sync| G[Firebase Hosting Web App]
    E -->|Historical Data| H[Looker Studio]
```

### Components Explanation

* **IoT Layer (ESP32 Nodes)**: Distributed edge devices collecting environmental and acoustic data. They stream data using lightweight JSON payloads over MQTT. The "edge" of this system is powered by the ESP32, a powerful microcontroller with integrated Wi-Fi. In this project, it acts as a telemetry producer, sampling sensors and pushing structured data to the cloud. The C++ code for the ESP32 is located in the `device-iot/` directory.
  * **Hardware Components**: To replicate the physical setup, the following components are used:
    * **MCU**: ESP32 (NodeMCU or similar).
    * **Environment Sensor**: DHT22 (High-accuracy temperature and humidity).
    * **Acoustic Sensor**: Analog Microphone (MAX9814 or similar) connected to an Analog-to-Digital Converter (ADC) pin.
    * **Connectivity**: 2.4GHz Wi-Fi.
* **EMQX (The Unified MQTT Platform for Robotics)**: Connects, processes, and streams real-time data from millions of devices to any cloud, AI, and analytics. It turns massive IoT data into actionable intelligence. EMQX acts as the entry point, receiving messages on specific topics and routing the flow to the cloud.
* **GCP Pub/Sub**: A highly scalable messaging service that ingests the data stream from EMQX. It acts as a central hub, decoupling the ingestion layer from the storage and processing layers.
* **Pub/Sub Subscriptions**:
  * **BigQuery Subscription**: Routes raw sensor data directly into BigQuery for long-term storage and complex data analysis.
  * **Cloud Run Subscription**: Routes data to a backend service for real-time processing.
* **Cloud Run**: A serverless compute environment that runs the backend service. It processes the incoming Pub/Sub messages and writes the structured data to the Firestore database.
* **Firestore**: A flexible, scalable NoSQL cloud database. It stores the latest processed sensor readings, enabling real-time synchronization with the frontend application.
* **Firebase Hosting (Web App)**: Hosts the frontend web application. The application reads data in real-time directly from Firestore and provides a live dashboard visualization of the sensors.
* **Looker Studio**: A business intelligence tool connected directly to GCP BigQuery. It fetches historical data to visualize long-term trends and metrics across the sensor network.

---

## EMQX Data Flow

![EMQX Data Flow](docs/images/media__1778207916296.png)

**Flow Explanation:**
1. **Device Connection**: IoT sensors publish telemetry data (such as temperature, humidity, and status) to specific MQTT topics on the EMQX broker.
2. **Rule Engine**: EMQX utilizes its built-in rule engine to filter and format the incoming JSON payloads in real-time.
3. **Data Bridge / Sink**: The processed messages are securely bridged via an outbound webhook/sink directly into the **GCP Pub/Sub** topic, ensuring high throughput and decoupled delivery to Google Cloud.

---

## Dashboards

### 1. Real-time Web App
A dynamic, responsive dashboard hosted on Firebase. It provides live updates of current temperature, humidity, and status indicators directly from Firestore.
![Web App Dashboard](docs/images/media__1778207916357.png)

### 2. Looker Studio Analytics
A comprehensive reporting interface pulling historical and aggregated data from BigQuery to uncover deeper insights.
![Looker Studio Analytics 1](docs/images/media__1778207660664.png)
![Looker Studio Analytics 2](docs/images/media__1778207660614.png)

---

## Conclusions
* **Scalability**: By leveraging serverless components (Cloud Run, Firestore, Firebase, BigQuery), the system scales automatically from a few devices to millions without manual infrastructure intervention.
* **Real-time vs Historical**: The dual-path architecture ensures ultra-low latency updates for operational dashboards (via Firestore) while independently preserving robust historical datasets for deep business intelligence (via BigQuery).
* **Decoupling**: The usage of EMQX as a dedicated MQTT broker and GCP Pub/Sub as the main messaging hub prevents tight coupling between the devices and the application logic, increasing system fault tolerance.

---

## References
* [EMQX MQTT Platform](https://www.emqx.com/en)
* [Google Cloud Pub/Sub](https://cloud.google.com/pubsub)
* [Google Cloud Run](https://cloud.google.com/run)
* [Firebase Firestore & Hosting](https://firebase.google.com/)
* [Google Cloud BigQuery](https://cloud.google.com/bigquery)
* [Looker Studio](https://lookerstudio.google.com/)
