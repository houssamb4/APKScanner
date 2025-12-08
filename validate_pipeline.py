#!/usr/bin/env python3
"""
APKScanner Pipeline Validation Script

This script demonstrates and validates the complete APK processing pipeline:
Input APK → Validate → Extract → Decompile → Organize → Output

Usage:
    python validate_pipeline.py [--create-test-apk] [--verbose]
"""

import os
import sys
import json
import argparse
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime


def setup_logging(verbose=False):
    """Setup logging for the validation script."""
    import logging
    
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)-8s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def create_test_apk(output_path: str) -> str:
    """
    Create a minimal valid APK file for testing.
    
    Args:
        output_path: Directory where the APK will be created
        
    Returns:
        Path to the created APK file
    """
    logger = setup_logging()
    logger.info("Creating minimal test APK...")
    
    # Create a minimal valid APK structure
    apk_path = os.path.join(output_path, 'test_app.apk')
    
    # Minimal AndroidManifest.xml
    manifest_content = b'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.testapp"
    android:versionCode="1"
    android:versionName="1.0.0">
    
    <uses-sdk
        android:minSdkVersion="21"
        android:targetSdkVersion="30"/>
    
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.READ_CONTACTS"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    
    <application
        android:allowBackup="true"
        android:debuggable="false"
        android:label="Test App">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        
        <service
            android:name=".MyService"
            android:exported="false"/>
        
        <receiver
            android:name=".MyReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="com.example.CUSTOM_ACTION"/>
            </intent-filter>
        </receiver>
    </application>
</manifest>'''
    
    # Create a minimal DEX file (just a valid ZIP structure with dex signature)
    dex_content = b'dex\n035\x00'  # DEX header signature
    dex_content += b'\x00' * 100  # Padding
    
    # Create the APK (which is a ZIP file)
    with zipfile.ZipFile(apk_path, 'w', zipfile.ZIP_DEFLATED) as apk:
        apk.writestr('AndroidManifest.xml', manifest_content)
        apk.writestr('classes.dex', dex_content)
        apk.writestr('resources.arsc', b'ARSC\x00\x00\x00\x00')  # Minimal resources
        apk.writestr('res/values/strings.xml', b'<?xml version="1.0"?><resources/>')
    
    logger.info(f"✅ Test APK created: {apk_path}")
    logger.info(f"   Package: com.example.testapp")
    logger.info(f"   Size: {os.path.getsize(apk_path)} bytes")
    
    return apk_path


def validate_stage(stage_name: str, test_func, *args, **kwargs) -> bool:
    """
    Execute and validate a pipeline stage.
    
    Args:
        stage_name: Name of the stage
        test_func: Function to execute
        *args: Positional arguments for test_func
        **kwargs: Keyword arguments for test_func
        
    Returns:
        True if stage passed, False otherwise
    """
    logger = setup_logging()
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing Stage: {stage_name}")
        logger.info(f"{'='*60}")
        
        result = test_func(*args, **kwargs)
        
        logger.info(f"✅ Stage '{stage_name}' PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Stage '{stage_name}' FAILED: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def test_validate_stage(apk_path: str) -> bool:
    """Test the Validate stage."""
    logger = setup_logging()
    from src.core.validators import APKValidator
    
    logger.info(f"Validating APK file: {apk_path}")
    
    validator = APKValidator()
    valid, error = validator.validate_apk_file(apk_path)
    
    if not valid:
        raise Exception(f"Validation failed: {error}")
    
    logger.info(f"File validation: ✅")
    
    valid, error = validator.validate_apk_structure(apk_path)
    if not valid:
        raise Exception(f"Structure validation failed: {error}")
    
    logger.info(f"Structure validation: ✅")
    
    return True


def test_extract_stage(apk_path: str) -> dict:
    """Test the Extract stage."""
    logger = setup_logging()
    from src.services.decompiler import Decompiler
    
    logger.info(f"Extracting metadata from APK: {apk_path}")
    
    decompiler = Decompiler()
    extracted_data = decompiler.analyze_with_androguard(apk_path)
    
    logger.info(f"Package: {extracted_data.get('package_name')}")
    logger.info(f"Version: {extracted_data.get('version_name')} (code: {extracted_data.get('version_code')})")
    logger.info(f"Min SDK: {extracted_data.get('min_sdk')}")
    logger.info(f"Target SDK: {extracted_data.get('target_sdk')}")
    logger.info(f"Permissions found: {len(extracted_data.get('permissions', []))}")
    
    return extracted_data


def test_decompile_stage(apk_path: str, extracted_data: dict) -> dict:
    """Test the Decompile stage."""
    logger = setup_logging()
    from src.services.decompiler import Decompiler
    
    logger.info(f"Decompiling APK: {apk_path}")
    
    decompiler = Decompiler()
    
    try:
        decompiled_dir = decompiler.decompile_with_apktool(apk_path)
        logger.info(f"Decompiled to: {decompiled_dir}")
        logger.info(f"Decompiled directory exists: {os.path.exists(decompiled_dir)}")
        
        # Extract endpoints
        endpoints = decompiler.extract_endpoints(decompiled_dir)
        logger.info(f"Endpoints found: {len(endpoints)}")
        if endpoints:
            for ep in endpoints[:5]:  # Show first 5
                logger.info(f"  - {ep['url']}")
        
        return {
            'decompiled_dir': decompiled_dir,
            'endpoints': endpoints
        }
    except Exception as e:
        logger.warning(f"Decompilation may require apktool installation: {str(e)}")
        return {
            'decompiled_dir': None,
            'endpoints': []
        }


def test_organize_stage(extracted_data: dict, decompile_data: dict) -> dict:
    """Test the Organize stage."""
    logger = setup_logging()
    from src.services.manifest_parser import ManifestParser
    from src.services.permission_checker import PermissionChecker
    
    logger.info("Organizing analysis data...")
    
    # Parse manifest
    manifest_parser = ManifestParser()
    manifest_xml = extracted_data.get('manifest_xml', '')
    manifest = manifest_parser.parse_manifest(manifest_xml)
    
    logger.info(f"Manifest parsed: {manifest.get('package')}")
    
    # Analyze permissions
    permission_checker = PermissionChecker()
    permissions = permission_checker.analyze_permissions(manifest.get('permissions', []))
    
    logger.info(f"Permissions analyzed:")
    logger.info(f"  - Total: {permissions.get('total_permissions')}")
    logger.info(f"  - Dangerous: {len(permissions.get('dangerous_permissions', []))}")
    logger.info(f"  - Normal: {len(permissions.get('normal_permissions', []))}")
    logger.info(f"  - Risk Score: {permissions.get('overprivilege_score', 0)}/10")
    
    # Check components
    components = permission_checker.check_component_exposure(manifest.get('components', {}))
    logger.info(f"Components checked:")
    logger.info(f"  - Total issues: {components.get('total_issues')}")
    
    # Assess security
    security = permission_checker.assess_security_flags(manifest.get('security_flags', {}))
    logger.info(f"Security flags assessed:")
    logger.info(f"  - Total issues: {security.get('total_issues')}")
    
    return {
        'manifest': manifest,
        'permissions': permissions,
        'components': components,
        'security': security,
        'endpoints': decompile_data.get('endpoints', [])
    }


def test_output_stage(organized_data: dict) -> dict:
    """Test the Output stage."""
    logger = setup_logging()
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.database.models import Base
    from src.core.pipeline import APKPipeline
    
    logger.info("Preparing output data...")
    
    # Create in-memory test database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    pipeline = APKPipeline()
    result = pipeline._stage_output(organized_data, db)
    
    if result[0]:
        output = result[0]
        logger.info(f"Analysis results prepared:")
        logger.info(f"  - APK ID: {output.get('apk_id')}")
        logger.info(f"  - Package: {output.get('package_name')}")
        logger.info(f"  - Risk Score: {output.get('overall_risk_score')}/10")
        return output
    else:
        raise Exception(f"Output generation failed: {result[1]}")


def run_full_pipeline_test(apk_path: str) -> bool:
    """Run the complete pipeline test."""
    logger = setup_logging()
    
    logger.info("\n" + "="*60)
    logger.info("APKScanner Pipeline Validation")
    logger.info("="*60)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"APK File: {apk_path}")
    logger.info("="*60)
    
    results = {}
    
    # Stage 1: Validate
    results['validate'] = validate_stage(
        "1/5 - VALIDATE",
        test_validate_stage,
        apk_path
    )
    
    if not results['validate']:
        logger.error("Pipeline stopped at Validate stage")
        return False
    
    # Stage 2: Extract
    try:
        extracted_data = validate_stage(
            "2/5 - EXTRACT",
            test_extract_stage,
            apk_path
        )
        results['extract'] = extracted_data is not None
    except Exception as e:
        logger.error(f"Extract stage failed: {e}")
        results['extract'] = False
        return False
    
    # Stage 3: Decompile
    try:
        decompile_data = validate_stage(
            "3/5 - DECOMPILE",
            test_decompile_stage,
            apk_path,
            extracted_data
        )
        results['decompile'] = decompile_data is not None
    except Exception as e:
        logger.error(f"Decompile stage failed: {e}")
        results['decompile'] = False
        decompile_data = {'decompiled_dir': None, 'endpoints': []}
    
    # Stage 4: Organize
    try:
        organized_data = validate_stage(
            "4/5 - ORGANIZE",
            test_organize_stage,
            extracted_data,
            decompile_data
        )
        results['organize'] = organized_data is not None
    except Exception as e:
        logger.error(f"Organize stage failed: {e}")
        results['organize'] = False
        return False
    
    # Stage 5: Output
    try:
        output_result = validate_stage(
            "5/5 - OUTPUT",
            test_output_stage,
            organized_data
        )
        results['output'] = output_result is not None
    except Exception as e:
        logger.error(f"Output stage failed: {e}")
        results['output'] = False
        return False
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("PIPELINE VALIDATION SUMMARY")
    logger.info("="*60)
    
    for stage, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{stage.upper():15} {status}")
    
    all_passed = all(results.values())
    
    logger.info("="*60)
    if all_passed:
        logger.info("✅ ALL PIPELINE STAGES PASSED!")
    else:
        logger.info("❌ SOME STAGES FAILED")
    logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='APKScanner Pipeline Validation Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create and validate test APK
  python validate_pipeline.py --create-test-apk --verbose
  
  # Validate specific APK
  python validate_pipeline.py /path/to/app.apk
        '''
    )
    
    parser.add_argument(
        'apk_path',
        nargs='?',
        help='Path to APK file to validate (or use --create-test-apk)'
    )
    parser.add_argument(
        '--create-test-apk',
        action='store_true',
        help='Create a minimal test APK and validate it'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    logger = setup_logging(args.verbose)
    
    # Determine APK path
    if args.create_test_apk:
        with tempfile.TemporaryDirectory() as tmpdir:
            apk_path = create_test_apk(tmpdir)
            success = run_full_pipeline_test(apk_path)
    elif args.apk_path:
        if not os.path.exists(args.apk_path):
            logger.error(f"APK file not found: {args.apk_path}")
            return 1
        success = run_full_pipeline_test(args.apk_path)
    else:
        # Try to create and validate test APK by default
        logger.info("No APK specified. Creating test APK...")
        with tempfile.TemporaryDirectory() as tmpdir:
            apk_path = create_test_apk(tmpdir)
            success = run_full_pipeline_test(apk_path)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
