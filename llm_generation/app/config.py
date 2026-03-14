from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="LLM_", extra="ignore")

    service_name: str = "llm-generation-service"
    host: str = "0.0.0.0"
    port: int = 8002

    mode: Literal["mock", "ollama"] = "mock"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3"
    ollama_timeout_seconds: float = 30.0


settings = Settings()
