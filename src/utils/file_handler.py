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
        # Also remove any decompiled directories matching the apk base name
        parent = os.path.dirname(file_path) or settings.temp_dir
        base_no_ext = os.path.splitext(os.path.basename(file_path))[0]
        try:
            for name in os.listdir(parent):
                # target directories like '<base>_decompiled' or '<base>_<id>_decompiled' or plain '<base>'
                if name.startswith(base_no_ext) and ('decompiled' in name or name == base_no_ext):
                    path = os.path.join(parent, name)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
        except FileNotFoundError:
            pass
        logger.info(f"Cleaned up temporary files for {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")

def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0