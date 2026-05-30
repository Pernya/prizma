from __future__ import annotations

import json
import time
from collections.abc import Callable

import pika
from pika.exceptions import AMQPConnectionError

from prizma_backend.config import Settings


class RabbitMQPublisher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def publish(self, job_id: str) -> None:
        parameters = pika.URLParameters(self.settings.rabbitmq_url)
        connection = pika.BlockingConnection(parameters)

        try:
            channel = connection.channel()
            channel.queue_declare(queue=self.settings.rabbitmq_queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=self.settings.rabbitmq_queue,
                body=json.dumps({"job_id": job_id}).encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2),
            )
        finally:
            connection.close()


class RabbitMQConsumer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def consume(self, handler: Callable[[str], None]) -> None:
        while True:
            try:
                self._consume_forever(handler)
            except AMQPConnectionError as exc:
                print(f"RabbitMQ connection failed: {exc}. Retrying in 5 seconds.")
                time.sleep(5)

    def _consume_forever(self, handler: Callable[[str], None]) -> None:
        parameters = pika.URLParameters(self.settings.rabbitmq_url)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=self.settings.rabbitmq_queue, durable=True)
        channel.basic_qos(prefetch_count=1)

        def callback(ch: pika.adapters.blocking_connection.BlockingChannel, method, _, body: bytes):
            payload = json.loads(body.decode("utf-8"))
            try:
                handler(str(payload["job_id"]))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as exc:
                print(f"Job processing failed: {exc}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_consume(queue=self.settings.rabbitmq_queue, on_message_callback=callback)

        try:
            channel.start_consuming()
        finally:
            connection.close()
