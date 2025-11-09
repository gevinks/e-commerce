from pydantic import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):

    #application metadata
    app_name: str = "E-Commerce API"
    app_description:str = "API for managing products"
    app_version: str = "1.0.0"

    #database config
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")

    #API config
    api_prefix: str = "/api/v1"
    docs_url: Optional[str] = "/docs"
    redocs_url: Optional[str] = "/redoc"

    #pagination settings
    default_page_size: int = 10
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True

class DatabaseSettings(BaseSettings):

    #SQLite Configuration
    sqlite_echo: bool = True
    sqlite_check_same_thread: bool = False

    #Postgres config (to be added later)

    class Config:
        env_file = ".env"
        env_prefix = "DB_"

#global settings instance
settings = Settings()
db_settings = DatabaseSettings()

def get_db_url() -> str:
    return settings.database_url

def get_app_settings() -> Settings:
    return settings