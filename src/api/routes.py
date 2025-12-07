from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from ..database.session import get_db
from ..services.apk_analyzer import APKAnalyzer
from ..database.crud import create_apk, get_apk, get_apks, get_endpoints_by_apk
from .schemas import AnalysisResult, ErrorResponse
from ..utils.logger import logger

router = APIRouter()
analyzer = APKAnalyzer()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_apk(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and analyze APK file"""
    try:
        if not file.filename.endswith('.apk'):
            raise HTTPException(status_code=400, detail="File must be an APK")

        result = await analyzer.analyze_apk(file, db)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/apks", response_model=List[Dict])
async def get_apks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of analyzed APKs"""
    apks = get_apks(db, skip=skip, limit=limit)
    return [
        {
            'id': apk.id,
            'filename': apk.filename,
            'package_name': apk.package_name,
            'analyzed_at': apk.id  # Using id as proxy for timestamp
        }
        for apk in apks
    ]

@router.get("/apks/{apk_id}", response_model=Dict)
async def get_apk_details(
    apk_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed analysis for a specific APK"""
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
        'permissions': [{'name': p.name, 'level': p.protection_level} for p in apk.permissions],
        'components': [{'type': c.type, 'name': c.name, 'exported': c.exported} for c in apk.components],
        'endpoints': [{'url': e.url, 'type': e.type} for e in endpoints],
        'security_flags': {
            'debuggable': apk.debuggable,
            'allow_backup': apk.allow_backup,
            'uses_cleartext_traffic': apk.uses_cleartext_traffic
        }
    }