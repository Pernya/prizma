# Матрица покрытия требований Prizma

Источник: `/Users/sanalpernyaev/Downloads/Prizma,команда 1.docx`.

Матрица показывает, насколько репозиторий покрывает целевой процесс, архитектуру и
эксплуатационные требования из отчета по кейсу.

| Область требований | Раздел в документе | Покрытие в репозитории | Статус |
| --- | --- | --- | --- |
| Пользовательский B2C-сценарий: загрузка изображения, выбор стиля, обработка, сохранение/шаринг | Разделы 2, 5; таблица 3 | Адаптивный installable web/PWA-like frontend в `web/`; есть загрузка, выбор стиля, просмотр результата, скачивание и share/copy fallback; нативное мобильное приложение не реализовано | Частично |
| Backend API / API gateway | Раздел 4; таблица 2 | FastAPI backend, валидация, жизненный цикл задач, метрики, статический OpenAPI contract в `docs/api/openapi.json` | Покрыто |
| Quality gate для API-контракта | Таблицы 4, 9 | `make contract` экспортирует OpenAPI; `tests/test_contract.py` блокирует расхождение между приложением и зафиксированной схемой | Покрыто |
| Очередь для тяжелой обработки | Раздел 4; таблица 2 | RabbitMQ publisher/consumer, worker service, Docker Compose и Helm-манифесты | Покрыто |
| S3-compatible storage для артефактов | Раздел 4; таблица 2 | MinIO/S3 backend, retention cleanup job, Docker Compose и Helm-манифесты | Покрыто |
| Triton-compatible inference | Раздел 4; таблица 8 | Triton model repository scaffold и HTTP client integration; production GPU-модель пока заменена scaffold-заглушкой | Частично |
| DVC / воспроизводимость датасета | Разделы 6, 8; таблицы 4, 7, 8 | `dvc.yaml`, детерминированная генерация golden set, сгенерированные датасеты вынесены из Git для DVC remote tracking | Покрыто |
| Data validation gate | Таблицы 7, 9 | `scripts/mlops/validate_dataset.py` и отчет `reports/mlops/data-validation.json` встроены в MLOps pipeline | Покрыто |
| MLflow / model registry | Разделы 6, 8; таблица 8 | Опциональное MLflow-логирование в baseline training script и extra `.[mlops]`; удаленный MLflow server не настроен | Частично |
| Model card и benchmark | Разделы 6, 10; таблицы 4, 9 | Генерируемый `docs/mlops/model-card.md`, benchmark report и drift report | Покрыто |
| GitLab CI/CD | Раздел 8; таблица 8 | `.gitlab-ci.yml` сохранен и подготовлен, но GitLab.com runners недоступны из-за блокировки верификации аккаунта | Частично |
| GitHub CI/CD как рабочая альтернатива | Адаптация раздела 8 | GitHub Actions CI, публикация образа в GHCR, ручной Kubernetes deploy, VPS frontend deploy | Покрыто |
| GitOps / Argo CD | Разделы 8, 10 | Argo CD Application manifests и Helm values подготовлены; live GitOps sync не подключен к реальному кластеру | Частично |
| Progressive delivery | Таблицы 8, 9 | Argo Rollouts templates и Prometheus analysis gates | Покрыто как манифесты |
| Kubernetes / Helm | Разделы 4, 8 | Helm chart для API, worker, MinIO, RabbitMQ, Triton, ServiceMonitor, ExternalSecret, CronJob | Покрыто |
| Текущий публичный VPS deployment | Текущая реализация | GitHub Actions SSH deploy на VPS с Docker Compose frontend stack | Покрыто |
| Prometheus/Grafana observability | Раздел 10; таблица 10 | Compose observability, Kubernetes observability manifests, Prometheus rules и Grafana dashboard | Покрыто |
| SLI/SLO/SLA и error budget | Раздел 10; таблица 10 | Русскоязычный документ `docs/sre/slo.md`, Prometheus alerts, dashboard и runbooks | Покрыто |
| Security gates | Раздел 9; таблица 9 | Secret detection, Bandit, pip-audit, image build, upload validation, ExternalSecret support | Покрыто |
| Rollback и incident response | Разделы 10, 11 | Runbooks для rollback, incident response и retraining | Покрыто |
| Нативный mobile release/signing | Таблицы 5, 12 | Не реализовано; вне текущего web/VPS MVP | Не покрыто |

## Итог покрытия

- Сильно покрыто: backend, queue/storage, MLOps baseline, CI quality gates, Helm/Kubernetes
  manifests, observability, SLI/SLO/SLA, security, rollback, VPS CD.
- Частично покрыто: нативный mobile client, production GPU-модель, live GitOps cluster,
  удаленный MLflow registry, отдельный CDN для result files.
- Практический следующий шаг для повышения покрытия: подключить реальный MLflow tracking URI,
  managed Kubernetes cluster или оставить VPS CD как принятый deployment target, а также
  зафиксировать, нужен ли нативный mobile client или достаточно responsive/PWA frontend.
