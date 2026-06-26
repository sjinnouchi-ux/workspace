from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.liff_report import router as liff_report_router
from app.api.routes.line_webhook import router as line_webhook_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(admin_router)
    app.include_router(liff_report_router)
    app.include_router(line_webhook_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {
            "ok": "true",
            "service": "k-alert-production",
            "env": settings.app_env,
        }

    return app


app = create_app()
