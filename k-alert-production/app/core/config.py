from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    app_name: str = Field(default="K Alert Production API", alias="APP_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")

    line_channel_secret: str = Field(default="", alias="LINE_CHANNEL_SECRET")
    line_channel_access_token: str = Field(default="", alias="LINE_CHANNEL_ACCESS_TOKEN")

    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="", alias="OPENAI_MODEL")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="", alias="ANTHROPIC_MODEL")

    chatwork_api_token: str = Field(default="", alias="CHATWORK_API_TOKEN")
    chatwork_room_id: str = Field(default="", alias="CHATWORK_ROOM_ID")

    admin_api_key: str = Field(default="", alias="ADMIN_API_KEY")
    google_sheet_id: str = Field(default="", alias="GOOGLE_SHEET_ID")
    k_alert_liff_url: str = Field(default="", alias="K_ALERT_LIFF_URL")
    liff_report_api_key: str = Field(default="", alias="LIFF_REPORT_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
