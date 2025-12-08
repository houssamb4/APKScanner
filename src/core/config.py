import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra='ignore')
    
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./apkscanner.db")
    temp_dir: str = os.getenv("TEMP_DIR", "./temp")
    logs_dir: str = os.getenv("LOGS_DIR", "./logs")
    apktool_path: str = os.getenv("APKTOOL_PATH", "apktool")  # Path to apktool jar or command


settings = Settings()