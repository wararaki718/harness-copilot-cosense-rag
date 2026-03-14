from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BATCH_", extra="ignore")

    service_name: str = "batch-ingestion-service"
    default_limit_pages: int = 50

    cosense_base_url: str = "https://scrapbox.io/api/pages"
    cosense_project: str = ""
    cosense_access_token: str = ""
    cosense_timeout_seconds: float = 10.0

    embedding_api_base_url: str = "http://localhost:8001"
    embedding_timeout_seconds: float = 10.0

    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "cosense-rag"
    elasticsearch_timeout_seconds: float = 5.0

    chunk_size: int = 800
    chunk_overlap: int = 100
    retry_count: int = 2


settings = Settings()
