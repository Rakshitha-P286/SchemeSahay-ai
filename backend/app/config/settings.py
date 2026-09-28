from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_db: str = "schememate"
    jwt_secret: str = "change-this-in-production"
    jwt_expire_minutes: int = 1440
    upload_dir: str = "../uploads"
    ai_enabled: bool = False
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = ""
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self) -> List[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
