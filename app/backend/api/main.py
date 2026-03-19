from __future__ import annotations

from app.backend.models.schemas import SDLRequest
from app.backend.services.sdl_service import SDLService

try:
    from fastapi import FastAPI
except Exception as exc:  # pragma: no cover
    FastAPI = None
    FASTAPI_IMPORT_ERROR = exc
else:
    FASTAPI_IMPORT_ERROR = None


service = SDLService()

if FastAPI is not None:
    app = FastAPI(title="AI Self-Driving Drug Lab API", version="0.1.0")

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "fastapi_available": True,
            "service": "ai-self-driving-drug-lab",
        }

    @app.post("/run")
    def run_closed_loop(request: SDLRequest) -> dict:
        return service.run_closed_loop(request).model_dump()
else:  # pragma: no cover
    class _MissingFastAPIApp:
        def __getattr__(self, name):
            raise RuntimeError(
                "FastAPI is not installed in this environment. "
                "Install requirements.txt and rerun uvicorn."
            ) from FASTAPI_IMPORT_ERROR

    app = _MissingFastAPIApp()

