from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

import httpx

from app.core.config import Settings


@dataclass(frozen=True)
class AiChatResult:
    reply_text: str
    emergency: bool = False


class AiChatClient(Protocol):
    async def generate_consultation_reply(
        self,
        *,
        user_text: str,
        turn_count: int,
        emergency_hint: bool,
    ) -> AiChatResult:
        """Generate a short supportive LINE reply."""


@dataclass(frozen=True)
class NullAiChatClient:
    async def generate_consultation_reply(
        self,
        *,
        user_text: str,
        turn_count: int,
        emergency_hint: bool,
    ) -> AiChatResult:
        if emergency_hint:
            return AiChatResult(reply_text="", emergency=True)
        return AiChatResult(reply_text="")


@dataclass(frozen=True)
class OpenAiChatClient:
    api_key: str
    model: str

    async def generate_consultation_reply(
        self,
        *,
        user_text: str,
        turn_count: int,
        emergency_hint: bool,
    ) -> AiChatResult:
        payload = {
            "model": self.model,
            "input": _build_prompt(
                user_text=user_text,
                turn_count=turn_count,
                emergency_hint=emergency_hint,
            ),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "k_alert_consultation_reply",
                    "strict": True,
                    "schema": _reply_schema(),
                }
            },
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return _parse_result(_parse_openai_response(response.json()))


@dataclass(frozen=True)
class AnthropicChatClient:
    api_key: str
    model: str

    async def generate_consultation_reply(
        self,
        *,
        user_text: str,
        turn_count: int,
        emergency_hint: bool,
    ) -> AiChatResult:
        payload = {
            "model": self.model,
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": _build_prompt(
                        user_text=user_text,
                        turn_count=turn_count,
                        emergency_hint=emergency_hint,
                    ),
                }
            ],
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return _parse_result(_parse_anthropic_response(response.json()))


def create_ai_chat_client(settings: Settings) -> AiChatClient:
    provider = settings.llm_provider.lower().strip()
    if provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicChatClient(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model or "claude-haiku-4-5",
        )
    if provider == "openai" and settings.openai_api_key:
        return OpenAiChatClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model or "gpt-4.1-mini",
        )
    return NullAiChatClient()


def _build_prompt(*, user_text: str, turn_count: int, emergency_hint: bool) -> str:
    return "\n".join(
        [
            "あなたはKアラート公式LINEの初期相談AIです。",
            "相談者はコンプライアンス、パワハラ、職場トラブル等を匿名で相談しています。",
            "返答は日本語で、LINEの短いチャットに向く長さにしてください。",
            "相談者を責めず、断定しすぎず、まず同調し、話を続けやすくしてください。",
            "医療・法律の断定的助言はしないでください。",
            "生命・身体・財産に危険がある可能性、110番/119番/救急/警察/暴力/脅迫/"
            "自殺/殺害/強い身体症状があれば emergency=true にしてください。",
            "turn_count が2以上なら、匿名で会社に報告するか、報告せず調査官に"
            "チャット相談できることへ自然に誘導してください。",
            "返答は JSON だけで返してください。",
            '形式: {"reply_text":"...","emergency":false}',
            "",
            f"turn_count: {turn_count}",
            f"emergency_hint: {str(emergency_hint).lower()}",
            "相談者の発言:",
            user_text,
        ]
    )


def _reply_schema() -> dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["reply_text", "emergency"],
        "properties": {
            "reply_text": {"type": "string"},
            "emergency": {"type": "boolean"},
        },
    }


def _parse_openai_response(response: dict[str, object]) -> dict[str, object]:
    parsed = response.get("output_parsed")
    if isinstance(parsed, dict):
        return parsed
    output_text = response.get("output_text")
    if isinstance(output_text, str) and output_text:
        return _loads_json_object(output_text)
    output = response.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if isinstance(part.get("parsed"), dict):
                    return part["parsed"]
                text = part.get("text")
                if isinstance(text, str) and text:
                    return _loads_json_object(text)
    raise ValueError("OpenAI structured output was not found.")


def _parse_anthropic_response(response: dict[str, object]) -> dict[str, object]:
    content = response.get("content")
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                return _loads_json_object(item["text"])
    raise ValueError("Anthropic structured output was not found.")


def _loads_json_object(text: str) -> dict[str, object]:
    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(stripped[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("AI response JSON was not an object.")
    return parsed


def _parse_result(payload: dict[str, object]) -> AiChatResult:
    reply_text = payload.get("reply_text")
    emergency = payload.get("emergency")
    return AiChatResult(
        reply_text=reply_text.strip() if isinstance(reply_text, str) else "",
        emergency=bool(emergency),
    )
