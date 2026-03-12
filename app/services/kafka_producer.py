"""
Kafka Producer - Sends messages to Kafka topics
"""
import json
import os
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

logger = logging.getLogger(__name__)

class KafkaProducerService:
    def __init__(self):
        self.producer = None
        self.enabled = False
        
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[kafka_servers],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            self.enabled = True
            logger.info(f"Kafka producer connected to {kafka_servers}")
        except Exception as e:
            logger.warning(f"Kafka producer not available: {e}")
            self.enabled = False
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None):
        """Send message to Kafka topic"""
        if not self.enabled:
            logger.debug(f"Kafka disabled, skipping message to {topic}")
            return False
        
        try:
            future = self.producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            logger.debug(
                f"Message sent to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False
    
    def send_customer_message(self, message_data: Dict[str, Any]):
        """Send customer message event"""
        return self.send_message(
            topic="customer-messages",
            message=message_data,
            key=message_data.get("ticket_id", "unknown")
        )
    
    def send_ai_response(self, response_data: Dict[str, Any]):
        """Send AI response event"""
        return self.send_message(
            topic="ai-responses",
            message=response_data,
            key=response_data.get("ticket_id", "unknown")
        )
    
    def send_escalation(self, escalation_data: Dict[str, Any]):
        """Send escalation event"""
        return self.send_message(
            topic="escalations",
            message=escalation_data,
            key=escalation_data.get("ticket_id", "unknown")
        )
    
    def send_metrics(self, metrics_data: Dict[str, Any]):
        """Send metrics event"""
        return self.send_message(
            topic="agent-metrics",
            message=metrics_data
        )
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.flush()
            self.producer.close()


# Global instance
kafka_producer = KafkaProducerService()
