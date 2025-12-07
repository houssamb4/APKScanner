from fastapi import APIRouter, UploadFile, File
from src.services.apk_analyzer import APKAnalyzer

router = APIRouter()
analyzer = APKAnalyzer()

@router.post("/analyze")
async def analyze_apk(file: UploadFile = File(...)):
    """Upload and analyze APK file"""
    return await analyzer.analyze(file)

@router.get("/results/{scan_id}")
async def get_results(scan_id: str):
    """Retrieve analysis results"""
    return analyzer.get_results(scan_id)