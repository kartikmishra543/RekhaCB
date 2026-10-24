from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4.1-mini"
    ai_embedding_api_key: str = ""
    ai_embedding_base_url: str = ""
    ai_embedding_model: str = "text-embedding-3-small"
    policy_retrieval_mode: Literal["auto", "semantic", "tfidf"] = "auto"
    policy_similarity_threshold: float = Field(default=0.30, ge=0, le=1)
    policy_vector_db: str = "./storage/policy_vectors.db"

    app_name: str = "Mock HRMS API"
    environment: str = "dev"
    app_timezone: str = "Asia/Kolkata"
    database_url: str = "sqlite+aiosqlite:///./storage/rekhacb.db"

    jwt_secret_key: str = ""

    @field_validator("jwt_secret_key", mode="after")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        if value.strip().lower() == "change_me" or len(value.strip()) < 32:
            raise ValueError("Set JWT_SECRET_KEY to a unique random secret of at least 32 characters in backend/.env.")
        return value

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    policy_upload_dir: str = "/app/storage/hr-policies"
    profile_photo_upload_dir: str = "/app/storage/profile-photos"
    employee_document_upload_dir: str = "/app/storage/employee-documents"


settings = Settings()
