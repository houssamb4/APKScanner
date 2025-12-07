from fastapi import FastAPI
from src.api.routes import router
from src.database.session import create_tables
from src.utils.logger import logger

# Create database tables on startup
create_tables()
logger.info("Database tables created/verified")

app = FastAPI(
    title="APKScanner API",
    description="APK Security Analysis and Decompilation Service",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")