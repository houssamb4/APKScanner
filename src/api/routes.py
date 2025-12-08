from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import os
from ..database.session import get_db
from ..core.pipeline import APKPipeline
from ..database.crud import get_apk, get_apks, get_endpoints_by_apk
from .schemas import AnalysisResult, ErrorResponse
from ..utils.logger import logger
from ..core.config import settings

router = APIRouter()
pipeline = APKPipeline()

@router.post("/analyze", response_model=Dict)
async def analyze_apk(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze APK file through the complete pipeline.
    
    Pipeline stages: Input APK → Validate → Extract → Decompile → Organize → Output
    """
    apk_file_path = None
    try:
        # Validate file extension
        if not file.filename.endswith('.apk'):
            logger.error(f"Invalid file extension: {file.filename}")
            raise HTTPException(status_code=400, detail="File must be an APK")
        
        # Save uploaded file
        os.makedirs(settings.temp_dir, exist_ok=True)
        apk_file_path = os.path.join(settings.temp_dir, file.filename)
        
        with open(apk_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"APK uploaded: {file.filename}")
        
        # Process through pipeline
        success, result = pipeline.process_apk(apk_file_path, db)
        
        if not success:
            logger.error(f"Pipeline failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get('error', 'Pipeline processing failed'))
        
        logger.info(f"Analysis completed successfully for {file.filename}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if apk_file_path and os.path.exists(apk_file_path):
            try:
                os.remove(apk_file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {apk_file_path}: {str(e)}")

@router.get("/apks", response_model=List[Dict])
async def get_all_apks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of analyzed APKs"""
    try:
        apks = get_apks(db, skip=skip, limit=limit)
        return [
            {
                'id': apk.id,
                'filename': apk.filename,
                'package_name': apk.package_name,
                'version_code': apk.version_code,
                'version_name': apk.version_name,
            }
            for apk in apks
        ]
    except Exception as e:
        logger.error(f"Error fetching APKs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/apks/{apk_id}", response_model=Dict)
async def get_apk_details(
    apk_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed analysis for a specific APK"""
    try:
        apk = get_apk(db, apk_id)
        if not apk:
            raise HTTPException(status_code=404, detail="APK not found")

        endpoints = get_endpoints_by_apk(db, apk_id)

        return {
            'id': apk.id,
            'filename': apk.filename,
            'package_name': apk.package_name,
            'version_code': apk.version_code,
            'version_name': apk.version_name,
            'min_sdk': apk.min_sdk,
            'target_sdk': apk.target_sdk,
            'permissions': [{'name': p.name, 'level': p.protection_level} for p in apk.permissions],
            'components': [{'type': c.type, 'name': c.name, 'exported': c.exported} for c in apk.components],
            'endpoints': [{'url': e.url, 'type': e.type} for e in endpoints],
            'security_flags': {
                'debuggable': apk.debuggable,
                'allow_backup': apk.allow_backup,
                'uses_cleartext_traffic': apk.uses_cleartext_traffic,
                'network_security_config': apk.network_security_config
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching APK details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "APKScanner API"}