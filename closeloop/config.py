from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./closeloop.db"
    secret_key: str = "dev-secret-change-me"
    app_name: str = "CloseLoop"
    app_base_url: str = "http://127.0.0.1:8000"

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    # WhatsApp-enabled Twilio sender, e.g. whatsapp:+14155238886
    twilio_whatsapp_from: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "followups@closeloop.local"

    seed_demo: bool = True
    # Public share path clients open to register
    register_path: str = "/register"


@lru_cache
def get_settings() -> Settings:
    return Settings()