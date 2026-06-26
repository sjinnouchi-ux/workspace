from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.core.supabase import SupabaseConfigError, create_supabase_client
from app.services.admin_store import AdminStore

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateAiResponseRuleRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    trigger_type: str = Field(min_length=1, max_length=80)
    instruction: str = Field(min_length=1, max_length=2000)
    trigger_text: str | None = Field(default=None, max_length=500)
    priority: int = Field(default=100, ge=1, le=1000)
    active: bool = False


def require_admin_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_admin_api_key: Annotated[str | None, Header(alias="X-Admin-Api-Key")] = None,
) -> None:
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin API key is not configured.",
        )
    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key.",
        )


def get_admin_store(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AdminStore:
    try:
        return AdminStore(create_supabase_client(settings))
    except SupabaseConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase is not configured.",
        ) from exc


@router.get("/cases", dependencies=[Depends(require_admin_api_key)])
async def list_cases(
    store: Annotated[AdminStore, Depends(get_admin_store)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> dict[str, object]:
    cases = await store.list_cases(limit=limit, status=status_filter)
    return {"ok": True, "cases": cases}


@router.get("/exports/reports", dependencies=[Depends(require_admin_api_key)])
async def export_reports_for_sheet(
    store: Annotated[AdminStore, Depends(get_admin_store)],
    start_date: date | None = None,
    end_date: date | None = None,
    company_name: str = "全社",
    status_filter: Annotated[str, Query(alias="status")] = "すべて",
    limit: Annotated[int, Query(ge=1, le=1000)] = 500,
) -> dict[str, object]:
    rows = await store.export_reports_for_sheet(
        start_date=start_date,
        end_date=end_date,
        company_name=company_name,
        status=status_filter,
        limit=limit,
    )
    return {"ok": True, "rows": rows}


@router.get("/exports/report-companies", dependencies=[Depends(require_admin_api_key)])
async def export_report_company_candidates(
    store: Annotated[AdminStore, Depends(get_admin_store)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 500,
) -> dict[str, object]:
    companies = await store.export_report_company_candidates(limit=limit)
    return {"ok": True, "companies": companies}


@router.get("/exports/ai-responses", dependencies=[Depends(require_admin_api_key)])
async def export_ai_responses_for_sheet(
    store: Annotated[AdminStore, Depends(get_admin_store)],
    start_date: date | None = None,
    end_date: date | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 500,
) -> dict[str, object]:
    rows = await store.export_ai_responses_for_sheet(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return {"ok": True, "rows": rows}


@router.get("/exports/ai-chat-summaries", dependencies=[Depends(require_admin_api_key)])
async def export_ai_chat_summaries_for_sheet(
    store: Annotated[AdminStore, Depends(get_admin_store)],
    start_date: date | None = None,
    end_date: date | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 500,
) -> dict[str, object]:
    rows = await store.export_ai_chat_summaries_for_sheet(
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return {"ok": True, "rows": rows}


@router.get("/cases/{case_id}", dependencies=[Depends(require_admin_api_key)])
async def get_case(
    case_id: str,
    store: Annotated[AdminStore, Depends(get_admin_store)],
) -> dict[str, object]:
    case = await store.get_case(case_id=case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
    return {"ok": True, "case": case}


@router.get("/ai-response-rules", dependencies=[Depends(require_admin_api_key)])
async def list_ai_response_rules(
    store: Annotated[AdminStore, Depends(get_admin_store)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    active: bool | None = None,
) -> dict[str, object]:
    rules = await store.list_ai_response_rules(limit=limit, active=active)
    return {"ok": True, "rules": rules}


@router.post(
    "/ai-response-rules",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_api_key)],
)
async def create_ai_response_rule(
    request: CreateAiResponseRuleRequest,
    store: Annotated[AdminStore, Depends(get_admin_store)],
) -> dict[str, object]:
    rule = await store.create_ai_response_rule(
        title=request.title,
        trigger_type=request.trigger_type,
        trigger_text=request.trigger_text,
        instruction=request.instruction,
        priority=request.priority,
        active=request.active,
    )
    return {"ok": True, "rule": rule}
