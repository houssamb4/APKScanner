import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra='ignore')

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./apkscanner.db")
    # default to shared backend storage temp folder (Windows absolute path)
    # Use Pydantic Field so BaseSettings reads env vars / .env correctly at runtime
    temp_dir: str = Field(
        default=r"C:\Users\houss\projects\Mobile-Security-Scanner\backend\storage\temp",
        env="TEMP_DIR",
    )
    logs_dir: str = Field(default="./logs", env="LOGS_DIR")
    apktool_path: str = Field(default="apktool", env="APKTOOL_PATH")  # Path to apktool jar or command


settings = Settings()

# Normalize paths and ensure directories exist
try:
    settings.temp_dir = os.path.abspath(os.path.expanduser(str(settings.temp_dir)))
    settings.logs_dir = os.path.abspath(os.path.expanduser(str(settings.logs_dir)))

    Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True)
except Exception:
    # Avoid raising on import; loggers may not be configured yet
    pass