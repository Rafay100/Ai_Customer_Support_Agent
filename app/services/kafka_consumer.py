"""
Kafka Consumer - Listens to Kafka topics and processes messages
"""
import json
import os
from typing import Callable, Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self):
        self.consumer = None
        self.enabled = False
        self.running = False
        self.consumers = {}
        
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        
        try:
            self.consumer = KafkaConsumer(
                bootstrap_servers=[kafka_servers],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='ai-support-agent',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000
            )
            self.enabled = True
            logger.info(f"Kafka consumer connected to {kafka_servers}")
        except Exception as e:
            logger.warning(f"Kafka consumer not available: {e}")
            self.enabled = False
    
    def subscribe(self, topics: list):
        """Subscribe to Kafka topics"""
        if self.enabled and self.consumer:
            self.consumer.subscribe(topics)
            logger.info(f"Subscribed to topics: {topics}")
    
    def start_consuming(self, message_handler: Callable[[str, Dict[str, Any]], None]):
        """Start consuming messages"""
        if not self.enabled:
            logger.info("Kafka consumer disabled, running in direct mode")
            return
        
        self.running = True
        
        def consume():
            while self.running:
                try:
                    messages = self.consumer.poll(timeout_ms=1000)
                    for topic_partition, records in messages.items():
                        for record in records:
                            topic = record.topic
                            message = record.value
                            logger.debug(f"Received message from {topic}: {message}")
                            message_handler(topic, message)
                except Exception as e:
                    logger.error(f"Error consuming message: {e}")
        
        consumer_thread = threading.Thread(target=consume, daemon=True)
        consumer_thread.start()
        logger.info("Kafka consumer started")
    
    def stop(self):
        """Stop consuming messages"""
        self.running = False
        if self.consumer:
            self.consumer.close()
    
    def process_message(self, topic: str, message: Dict[str, Any], handler: Callable):
        """Process a single message (for non-Kafka mode)"""
        logger.info(f"Processing message directly (Kafka disabled): {topic}")
        handler(topic, message)


# Global instance
kafka_consumer = KafkaConsumerService()
