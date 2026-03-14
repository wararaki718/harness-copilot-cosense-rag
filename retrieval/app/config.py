from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RETRIEVAL_", extra="ignore")

    service_name: str = "retrieval-service"
    host: str = "0.0.0.0"
    port: int = 8000

    embedding_api_base_url: str = "http://localhost:8001"
    llm_generation_api_base_url: str = "http://localhost:8002"
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "cosense-rag"
    elasticsearch_timeout_seconds: float = 5.0
    embedding_timeout_seconds: float = 10.0
    embedding_retry_count: int = 1

    default_top_k: int = 5
    default_score_threshold: float = 0.20
    fallback_message: str = "該当情報が見つからないため、回答できませんでした。"

    llm_timeout_seconds: float = 30.0
    llm_retry_count: int = 2
    llm_max_tokens: int = 512

    allowed_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
