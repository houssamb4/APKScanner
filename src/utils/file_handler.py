import os
import shutil
from fastapi import UploadFile
from ..core.config import settings
from .logger import logger

def save_uploaded_apk(file: UploadFile) -> str:
    """Save uploaded APK file to temp directory and return the path."""
    os.makedirs(settings.temp_dir, exist_ok=True)
    file_path = os.path.join(settings.temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"APK saved to {file_path}")
    return file_path

def cleanup_temp_files(file_path: str):
    """Remove temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        # Also remove any decompiled directories if they exist
        decompiled_dir = file_path.replace('.apk', '')
        if os.path.exists(decompiled_dir):
            shutil.rmtree(decompiled_dir)
        logger.info(f"Cleaned up temporary files for {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")

def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0