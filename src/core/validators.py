"""APK file validators for the pipeline."""

import os
import zipfile
from typing import Tuple
from ..utils.logger import logger


class APKValidator:
    """Validates APK files before processing."""
    
    # Maximum file size (100MB)
    MAX_FILE_SIZE = 104857600
    
    @staticmethod
    def validate_apk_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate APK file.
        
        Args:
            file_path: Path to the APK file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file exists
        if not os.path.exists(file_path):
            error = f"File not found: {file_path}"
            logger.error(error)
            return False, error
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > APKValidator.MAX_FILE_SIZE:
            error = f"File too large: {file_size} bytes (max {APKValidator.MAX_FILE_SIZE})"
            logger.error(error)
            return False, error
        
        if file_size == 0:
            error = "File is empty"
            logger.error(error)
            return False, error
        
        # Check file extension
        if not file_path.lower().endswith('.apk'):
            error = "File is not an APK (wrong extension)"
            logger.error(error)
            return False, error
        
        # Check if it's a valid ZIP file (APKs are ZIPs)
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Check for required APK files
                namelist = zip_file.namelist()
                required_files = ['AndroidManifest.xml', 'classes.dex']
                
                has_manifest = any('AndroidManifest.xml' in name for name in namelist)
                has_dex = any(name.endswith('.dex') for name in namelist)
                
                if not has_manifest:
                    error = "APK missing AndroidManifest.xml"
                    logger.error(error)
                    return False, error
                
                if not has_dex:
                    error = "APK missing DEX files"
                    logger.error(error)
                    return False, error
                
                logger.info(f"APK validation successful: {file_path}")
                return True, ""
                
        except zipfile.BadZipFile:
            error = "Invalid ZIP file (corrupted APK)"
            logger.error(error)
            return False, error
        except Exception as e:
            error = f"Error validating APK: {str(e)}"
            logger.error(error)
            return False, error
    
    @staticmethod
    def validate_apk_structure(file_path: str) -> Tuple[bool, str]:
        """Validate APK internal structure."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Verify we can read all files
                try:
                    zip_file.testzip()
                except RuntimeError as e:
                    return False, f"Corrupted APK: {str(e)}"
                
                logger.info(f"APK structure validation successful: {file_path}")
                return True, ""
        except Exception as e:
            error = f"Structure validation error: {str(e)}"
            logger.error(error)
            return False, error
