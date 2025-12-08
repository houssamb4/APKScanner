#!/usr/bin/env python3
"""Quick validation script to check if all pipeline components are in place."""

import os
import sys
import json
from pathlib import Path


def check_pipeline_structure():
    """Check if all required files for the pipeline exist."""
    
    print("=" * 70)
    print("APKScanner Pipeline Structure Validation")
    print("=" * 70)
    
    required_files = {
        "Core Pipeline": [
            "src/core/pipeline.py",
            "src/core/validators.py",
            "src/core/config.py",
            "src/core/__init__.py",
        ],
        "Services": [
            "src/services/apk_analyzer.py",
            "src/services/decompiler.py",
            "src/services/manifest_parser.py",
            "src/services/permission_checker.py",
            "src/services/__init__.py",
        ],
        "API": [
            "src/api/routes.py",
            "src/api/schemas.py",
            "src/api/__init__.py",
        ],
        "Database": [
            "src/database/models.py",
            "src/database/session.py",
            "src/database/crud.py",
            "src/database/__init__.py",
        ],
        "Utils": [
            "src/utils/logger.py",
            "src/utils/file_handler.py",
            "src/utils/__init__.py",
        ],
        "Tests": [
            "tests/test_analyzer.py",
            "tests/test_api.py",
            "tests/__init__.py",
        ],
        "Configuration": [
            "main.py",
            "requirements.txt",
            ".env",
            "PIPELINE.md",
            "validate_pipeline.py",
        ]
    }
    
    all_present = True
    
    for category, files in required_files.items():
        print(f"\n{category}:")
        print("-" * 70)
        
        for file_path in files:
            exists = os.path.exists(file_path)
            status = "[OK]" if exists else "[FAIL]"
            print(f"  {status} {file_path}")
            if not exists:
                all_present = False
    
    return all_present


def check_imports():
    """Check if critical imports are working."""
    
    print("\n" + "=" * 70)
    print("Import Validation")
    print("=" * 70)
    
    imports_to_check = {
        "FastAPI": "from fastapi import FastAPI",
        "SQLAlchemy": "from sqlalchemy import create_engine",
        "Pydantic": "from pydantic import BaseModel",
        "XML Parser": "import xml.etree.ElementTree as ET",
    }
    
    all_ok = True
    
    for name, import_stmt in imports_to_check.items():
        try:
            exec(import_stmt)
            print(f"[OK] {name:20} - Available")
        except ImportError as e:
            print(f"[FAIL] {name:20} - Missing: {str(e)}")
            all_ok = False
    
    return all_ok


def check_pipeline_components():
    """Check if key pipeline components are defined."""
    
    print("\n" + "=" * 70)
    print("Pipeline Components Check")
    print("=" * 70)
    
    try:
        from src.core.pipeline import APKPipeline, PipelineStage
        print("[OK] APKPipeline - Defined")
        print("[OK] PipelineStage - Defined")
        
        # Check pipeline stages
        print("\nPipeline Stages:")
        stages = [
            PipelineStage.VALIDATE,
            PipelineStage.EXTRACT,
            PipelineStage.DECOMPILE,
            PipelineStage.ORGANIZE,
            PipelineStage.OUTPUT
        ]
        
        for i, stage in enumerate(stages, 1):
            print(f"  {i}. {stage.upper():15} - [OK]")
        
        return True
    except Exception as e:
        print(f"[FAIL] Pipeline components error: {str(e)}")
        return False


def check_validators():
    """Check if APK validator is working."""
    
    print("\n" + "=" * 70)
    print("Validator Check")
    print("=" * 70)
    
    try:
        from src.core.validators import APKValidator
        print("[OK] APKValidator - Imported")
        
        validator = APKValidator()
        print("[OK] APKValidator - Instantiated")
        
        # Test with non-existent file
        valid, error = validator.validate_apk_file("/nonexistent.apk")
        if not valid and error:
            print("[OK] APKValidator - Validation logic working")
            return True
        else:
            print("[FAIL] APKValidator - Validation logic issue")
            return False
    except Exception as e:
        print(f"[FAIL] Validator error: {str(e)}")
        return False


def check_services():
    """Check if all service classes are defined."""
    
    print("\n" + "=" * 70)
    print("Services Check")
    print("=" * 70)
    
    services_to_check = {
        "Decompiler": "from src.services.decompiler import Decompiler",
        "ManifestParser": "from src.services.manifest_parser import ManifestParser",
        "PermissionChecker": "from src.services.permission_checker import PermissionChecker",
        "APKAnalyzer": "from src.services.apk_analyzer import APKAnalyzer",
    }
    
    all_ok = True
    
    for name, import_stmt in services_to_check.items():
        try:
            exec(import_stmt)
            print(f"[OK] {name:25} - Imported and defined")
        except Exception as e:
            print(f"[FAIL] {name:25} - Error: {str(e)}")
            all_ok = False
    
    return all_ok


def check_database():
    """Check if database models and sessions are working."""
    
    print("\n" + "=" * 70)
    print("Database Check")
    print("=" * 70)
    
    try:
        from src.database.models import APK, Permission, Component, Endpoint
        print("[OK] APK Model - Defined")
        print("[OK] Permission Model - Defined")
        print("[OK] Component Model - Defined")
        print("[OK] Endpoint Model - Defined")
        
        from src.database.session import create_tables
        print("[OK] Database session - Configured")
        
        return True
    except Exception as e:
        print(f"[FAIL] Database error: {str(e)}")
        return False


def print_pipeline_flow():
    """Print the pipeline flow diagram."""
    
    print("\n" + "=" * 70)
    print("Pipeline Flow")
    print("=" * 70)
    
    flow = """
    INPUT APK
        |
        v
    [1] VALIDATE
        - Check file existence
        - Check file size (max 100MB)
        - Check file extension (.apk)
        - Validate ZIP structure
        - Verify APK contents (manifest, dex)
        |
        v
    [2] EXTRACT
        - Use Androguard to analyze APK
        - Extract metadata (package, version, SDK)
        - Extract permissions list
        - Extract components (activities, services, etc.)
        - Get Android Manifest XML
        |
        v
    [3] DECOMPILE
        - Use apktool to decompile resources
        - Extract and parse manifest
        - Decompile DEX to SMALI code
        - Extract hardcoded endpoints/URLs
        |
        v
    [4] ORGANIZE
        - Parse manifest XML
        - Analyze permissions for risks
        - Check component exposure
        - Assess security flags
        - Organize endpoints
        |
        v
    [5] OUTPUT
        - Store APK metadata in database
        - Store permissions with relationships
        - Store components
        - Store extracted endpoints
        - Calculate risk scores
        |
        v
    ANALYSIS COMPLETE
        Returns:
        - APK ID
        - Package info
        - Permission analysis
        - Component issues
        - Security assessment
        - Endpoints found
        - Overall risk score (0-10)
    """
    
    print(flow)


def main():
    """Run all validations."""
    
    results = []
    
    # Run all checks
    results.append(("Files Structure", check_pipeline_structure()))
    results.append(("Dependencies", check_imports()))
    results.append(("Services", check_services()))
    results.append(("Database", check_database()))
    results.append(("Pipeline Components", check_pipeline_components()))
    results.append(("Validators", check_validators()))
    
    # Print pipeline flow
    print_pipeline_flow()
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name:30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\nALL VALIDATIONS PASSED - PIPELINE READY!")
        print("\nNext Steps:")
        print("1. Run: python validate_pipeline.py --create-test-apk")
        print("2. Or start server: uvicorn main:app --reload")
        print("3. Test endpoint: curl -F 'file=@test.apk' http://localhost:8001/api/v1/analyze")
        return 0
    else:
        print("\nSOME VALIDATIONS FAILED - FIX ISSUES ABOVE")
        return 1


if __name__ == '__main__':
    sys.exit(main())
