from typing import List, Union
from pydantic import model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Aapnu Parivar"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    DEMO_MODE: bool = True
    AUTO_CREATE_SCHEMA: bool = True

    DATABASE_URL: str = "sqlite:///./aapnu_parivar.db"

    JWT_SECRET: str = "super-secret-key-change-in-production-1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    AADHAAR_HASH_KEY: str = "aadhaar-hmac-secret-key-aapnu-parivar-2026"

    ALLOWED_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    @model_validator(mode="after")
    def require_real_secrets_in_production(self) -> "Settings":
        insecure = {"", "super-secret-key-change-in-production-1234567890", "aadhaar-hmac-secret-key-aapnu-parivar-2026"}
        if self.ENV.lower() in {"production", "prod"}:
            if self.DEMO_MODE or self.AUTO_CREATE_SCHEMA:
                raise ValueError("Production requires DEMO_MODE=false and AUTO_CREATE_SCHEMA=false.")
            if self.JWT_SECRET in insecure or self.AADHAAR_HASH_KEY in insecure:
                raise ValueError("Production requires non-default JWT_SECRET and AADHAAR_HASH_KEY values.")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
