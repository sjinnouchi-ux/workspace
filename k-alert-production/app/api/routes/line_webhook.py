from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.core.config import Settings, get_settings
from app.services.line_signature import verify_line_signature
from app.services.line_webhook_service import LineWebhookService, get_line_webhook_service

router = APIRouter(prefix="/webhooks", tags=["line-webhook"])


@router.post("/line")
async def receive_line_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    service: Annotated[LineWebhookService, Depends(get_line_webhook_service)],
    x_line_signature: Annotated[str | None, Header(alias="X-Line-Signature")] = None,
) -> dict[str, object]:
    body = await request.body()

    if not settings.line_channel_secret:
        if settings.app_env != "local":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LINE channel secret is not configured.",
            )
    elif not x_line_signature or not verify_line_signature(
        body=body,
        channel_secret=settings.line_channel_secret,
        signature=x_line_signature,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid LINE signature.",
        )

    result = await service.handle_raw_webhook(body)
    return {
        "ok": True,
        "handled": result.handled,
        "event_count": result.event_count,
        "duplicate_count": result.duplicate_count,
        "reply_count": result.reply_count,
    }
