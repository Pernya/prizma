from prometheus_client import start_http_server

from prizma_backend.config import get_settings
from prizma_backend.messaging import RabbitMQConsumer
from prizma_backend.service import build_job_service


def main() -> None:
    settings = get_settings()
    start_http_server(settings.worker_metrics_port)
    service = build_job_service(settings)
    consumer = RabbitMQConsumer(settings)
    consumer.consume(service.process_job)


if __name__ == "__main__":
    main()
