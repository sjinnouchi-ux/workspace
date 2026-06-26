from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field, model_validator

from app.core.config import Settings, get_settings
from app.core.supabase import SupabaseConfigError, create_supabase_client
from app.services.liff_report_store import LiffReportStore, LiffReportSubmission

router = APIRouter(prefix="/liff", tags=["liff-report"])


class LiffReportRequest(BaseModel):
    case_code: str = Field(min_length=1, max_length=80)
    company_name: str = Field(min_length=1, max_length=200)
    reporter_name: str = Field(default="", max_length=200)
    when_text: str = Field(min_length=1, max_length=1000)
    where_text: str = Field(min_length=1, max_length=1000)
    who_text: str = Field(min_length=1, max_length=1000)
    to_whom_text: str = Field(min_length=1, max_length=1000)
    what_how_text: str = Field(default="", max_length=3000)
    what_text: str = Field(default="", max_length=2000)
    how_text: str = Field(default="", max_length=2000)
    free_text: str = Field(default="", max_length=3000)
    consultation_request: str = Field(pattern="^(希望する|希望しない)$")

    @model_validator(mode="after")
    def normalize_what_how(self) -> "LiffReportRequest":
        if not self.what_how_text:
            self.what_how_text = " / ".join(
                value for value in [self.what_text.strip(), self.how_text.strip()] if value
            )
        if not self.what_how_text:
            raise ValueError("what_how_text is required.")
        return self


def require_liff_report_api_key(
    settings: Annotated[Settings, Depends(get_settings)],
    x_liff_report_api_key: Annotated[str | None, Header(alias="X-Liff-Report-Api-Key")] = None,
) -> None:
    if not settings.liff_report_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LIFF report API key is not configured.",
        )
    if x_liff_report_api_key != settings.liff_report_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid LIFF report API key.",
        )


def get_liff_report_store(
    settings: Annotated[Settings, Depends(get_settings)],
) -> LiffReportStore:
    try:
        return LiffReportStore(create_supabase_client(settings))
    except SupabaseConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase is not configured.",
        ) from exc


@router.post("/report", dependencies=[Depends(require_liff_report_api_key)])
async def submit_liff_report(
    request: LiffReportRequest,
    store: Annotated[LiffReportStore, Depends(get_liff_report_store)],
) -> dict[str, object]:
    try:
        result = await store.submit_report(
            LiffReportSubmission(
                case_code=request.case_code,
                company_name=request.company_name,
                reporter_name=request.reporter_name,
                when_text=request.when_text,
                where_text=request.where_text,
                who_text=request.who_text,
                to_whom_text=request.to_whom_text,
                what_how_text=request.what_how_text,
                free_text=request.free_text,
                consultation_request=request.consultation_request,
            )
        )
    except ValueError as exc:
        if str(exc) == "case_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found.",
            ) from exc
        raise
    return {"ok": True, **result}
