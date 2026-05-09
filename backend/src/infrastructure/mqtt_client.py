import logging
import paho.mqtt.client as mqtt
import json
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER")
        self.port = int(os.getenv("MQTT_PORT", "1883"))
        self.username = os.getenv("MQTT_USER")
        self.password = os.getenv("MQTT_PASSWORD")
        self.client_id = os.getenv("MQTT_CLIENT_ID", "iot-backend-api")
        
        if not all([self.broker, self.username, self.password]):
            logger.error("Missing MQTT configuration environment variables")

    def publish(self, topic: str, message: Any):
        """
        Connects, publishes a single message, and disconnects.
        This pattern is more reliable for serverless environments like Cloud Run.
        """
        if not topic:
            logger.error("MQTT Publish failed: No topic provided")
            return False

        if not isinstance(message, str):
            message = json.dumps(message)
        
        import uuid
        instance_id = str(uuid.uuid4())[:8]
        temp_client_id = f"{self.client_id}-{instance_id}"

        # Create a transient client
        client = mqtt.Client(
            client_id=temp_client_id, 
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            protocol=mqtt.MQTTv5
        )
        client.username_pw_set(self.username, self.password)
        
        # Use a local flag to track publication success
        published = False

        def on_publish(client, userdata, mid, reason_code, properties):
            nonlocal published
            published = True
            logger.info(f"Message ID {mid} published successfully")

        client.on_publish = on_publish

        try:
            logger.info(f"Connecting to {self.broker} for on-demand publish...")
            client.connect(self.broker, self.port, keepalive=60)
            
            # Start the loop in a background thread or just use loop()
            # Since we only want to publish one message, we can use loop_start/stop or just loop()
            client.loop_start()
            
            msg_info = client.publish(topic, message, qos=1)
            
            # Wait for the publish to complete (on_publish callback to be called)
            # wait_for_publish() is usually enough but we check our flag too
            msg_info.wait_for_publish(timeout=5.0)
            
            # Small grace period for the loop to process the callback
            start_time = time.time()
            while not published and time.time() - start_time < 2.0:
                time.sleep(0.1)

            if published or msg_info.is_published():
                logger.info(f"Successfully published to topic `{topic}`")
                return True
            else:
                logger.error(f"Failed to confirm publication to topic `{topic}` (timeout)")
                return False

        except Exception as e:
            logger.error(f"Exception during MQTT on-demand publish: {str(e)}", exc_info=True)
            return False
        finally:
            try:
                client.loop_stop()
                client.disconnect()
                logger.info("Transient MQTT client disconnected")
            except:
                pass

# Global instance
mqtt_service = MQTTClient()
