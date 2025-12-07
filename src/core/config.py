import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./apkscanner.db")
    temp_dir: str = os.getenv("TEMP_DIR", "./temp")
    logs_dir: str = os.getenv("LOGS_DIR", "./logs")
    apktool_path: str = os.getenv("APKTOOL_PATH", "apktool")  # Path to apktool jar or command

    class Config:
        env_file = ".env"

settings = Settings()