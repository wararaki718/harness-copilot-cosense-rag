from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="EMBEDDING_", extra="ignore")

    service_name: str = "embedding-service"
    host: str = "0.0.0.0"
    port: int = 8001

    model_name: str = "japanese-splade-mock"
    max_tokens_per_text: int = 64
    max_batch_size: int = 64


settings = Settings()
