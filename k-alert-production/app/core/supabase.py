from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import Settings, get_settings


class SupabaseConfigError(RuntimeError):
    """Raised when Supabase server-side configuration is incomplete."""


@dataclass(frozen=True)
class SupabaseRestClient:
    url: str
    service_role_key: str

    def _headers(self, *, prefer: str = "return=representation") -> dict[str, str]:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    async def insert(self, table: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        endpoint = f"{self.url.rstrip('/')}/rest/v1/{table}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(endpoint, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    async def select_by_eq(
        self,
        table: str,
        column: str,
        value: str,
        *,
        select: str = "*",
        limit: int = 1,
    ) -> list[dict[str, Any]]:
        endpoint = f"{self.url.rstrip('/')}/rest/v1/{table}"
        params = {
            "select": select,
            column: f"eq.{quote(value, safe='')}",
            "limit": str(limit),
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(endpoint, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    async def select(
        self,
        table: str,
        *,
        select: str = "*",
        filters: dict[str, str] | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        endpoint = f"{self.url.rstrip('/')}/rest/v1/{table}"
        params: dict[str, str] = {"select": select}
        if filters:
            params.update(filters)
        if order:
            params["order"] = order
        if limit is not None:
            params["limit"] = str(limit)
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(endpoint, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json()

    async def update_by_eq(
        self,
        table: str,
        column: str,
        value: str,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        endpoint = f"{self.url.rstrip('/')}/rest/v1/{table}"
        params = {column: f"eq.{quote(value, safe='')}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.patch(
                endpoint,
                headers=self._headers(),
                params=params,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def upsert(
        self,
        table: str,
        payload: dict[str, Any],
        *,
        on_conflict: str,
    ) -> list[dict[str, Any]]:
        endpoint = f"{self.url.rstrip('/')}/rest/v1/{table}"
        params = {"on_conflict": on_conflict}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                endpoint,
                headers=self._headers(prefer="resolution=merge-duplicates,return=representation"),
                params=params,
                json=payload,
            )
            response.raise_for_status()
            return response.json()


def create_supabase_client(settings: Settings | None = None) -> SupabaseRestClient:
    resolved = settings or get_settings()
    if not resolved.supabase_url or not resolved.supabase_service_role_key:
        raise SupabaseConfigError("Supabase URL or service role key is not configured.")
    return SupabaseRestClient(
        url=resolved.supabase_url,
        service_role_key=resolved.supabase_service_role_key,
    )
