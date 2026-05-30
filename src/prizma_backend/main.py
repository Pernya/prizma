from time import perf_counter

from fastapi import BackgroundTasks, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from prizma_backend.config import Settings, get_settings
from prizma_backend.metrics import record_request
from prizma_backend.service import build_job_service

STYLE_FORM = Form(...)
UPLOAD_FILE = File(...)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(title="Prizma Backend", version="0.1.0")
    app.state.settings = settings
    app.state.job_service = build_job_service(settings)

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        started_at = perf_counter()
        response = await call_next(request)
        path = request.scope.get("route").path if request.scope.get("route") else request.url.path
        record_request(request.method, path, response.status_code, perf_counter() - started_at)
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz() -> dict[str, str]:
        return {
            "status": "ready",
            "execution_mode": settings.execution_mode,
            "storage_backend": settings.storage_backend,
            "inference_backend": settings.inference_backend,
        }

    @app.get("/api/v1/styles")
    async def list_styles():
        return app.state.job_service.list_styles()

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.post("/api/v1/jobs", status_code=202)
    async def create_job(
        background_tasks: BackgroundTasks,
        style: str = STYLE_FORM,
        file: UploadFile = UPLOAD_FILE,
    ):
        record = app.state.job_service.create_job(file=file, style=style)
        if settings.execution_mode == "broker":
            app.state.job_service.dispatch_job(record.job_id)
        else:
            background_tasks.add_task(app.state.job_service.process_job, record.job_id)
        return app.state.job_service.build_created_response(settings.base_url, record)

    @app.get("/api/v1/jobs/{job_id}")
    async def get_job(job_id: str):
        return app.state.job_service.get_job(job_id)

    @app.get("/api/v1/jobs/{job_id}/result")
    async def get_result(job_id: str) -> Response:
        stored = app.state.job_service.get_result(job_id)
        return Response(content=stored.payload, media_type=stored.content_type)

    return app


app = create_app()
