#!/usr/bin/env python3
"""Test the APK analysis with a real APK file."""

import requests
import json
import sys
from pathlib import Path

# Configuration
API_BASE = "http://127.0.0.1:8001/api/v1"
APK_FILE = r"C:\Users\houss\Downloads\com.superproductivity.superproductivity_1604030000.apk"

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_health():
    """Test health endpoint."""
    print_header("1. Testing Health Endpoint")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✓ Server is healthy")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_upload_apk(apk_path):
    """Upload and analyze APK."""
    print_header("2. Uploading APK for Analysis")
    
    if not Path(apk_path).exists():
        print(f"✗ APK file not found: {apk_path}")
        return None
    
    file_size = Path(apk_path).stat().st_size
    print(f"APK File: {Path(apk_path).name}")
    print(f"Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print("\nUploading and processing through pipeline...")
    print("(This may take 1-5 minutes depending on APK size)\n")
    
    try:
        with open(apk_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_BASE}/analyze", files=files, timeout=300)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✓ Pipeline execution completed!")
            return result
        else:
            print(f"✗ Upload failed with status {response.status_code}")
            try:
                print(f"  Error: {response.json().get('detail', response.text)}")
            except:
                print(f"  Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (APK processing took too long)")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def display_pipeline_results(result):
    """Display pipeline execution results."""
    print_header("3. Pipeline Execution Results")
    
    if not result:
        return
    
    # Overall status
    success = result.get('success')
    print(f"Overall Status: {'✓ SUCCESS' if success else '✗ FAILED'}")
    
    if result.get('error'):
        print(f"Error: {result['error']}\n")
    
    # Stage results
    if 'stages' in result:
        print("Pipeline Stages:")
        stages = result['stages']
        for stage_name, stage_result in stages.items():
            status = "✓ PASS" if stage_result.get('success') else "✗ FAIL"
            message = stage_result.get('message', '')
            print(f"  {stage_name.upper():15} {status}")
            if message and not stage_result.get('success'):
                print(f"                 └─ {message}")
    
    print()

def get_apks_list():
    """Get list of all analyzed APKs."""
    print_header("4. Retrieving All Analyzed APKs")
    
    try:
        response = requests.get(f"{API_BASE}/apks")
        if response.status_code == 200:
            apks = response.json()
            print(f"Total APKs in database: {len(apks)}\n")
            
            if apks:
                print("APK List:")
                for apk in apks[-5:]:  # Show last 5
                    apk_id = apk.get('id', 'N/A')
                    filename = apk.get('filename', 'N/A')
                    package = apk.get('package_name', 'N/A')
                    version = apk.get('version_name', 'N/A')
                    print(f"  ID {apk_id}: {filename}")
                    print(f"           Package: {package} v{version}\n")
                return apks
            else:
                print("No APKs in database yet.")
                return []
        else:
            print(f"✗ Failed to retrieve APKs: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def get_apk_details(apk_id):
    """Get detailed analysis for a specific APK."""
    print_header(f"5. Getting Detailed Analysis for APK ID {apk_id}")
    
    try:
        response = requests.get(f"{API_BASE}/apks/{apk_id}")
        if response.status_code == 200:
            details = response.json()
            print(json.dumps(details, indent=2))
            return details
        elif response.status_code == 404:
            print(f"✗ APK with ID {apk_id} not found")
            return None
        else:
            print(f"✗ Failed to retrieve details: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def main():
    """Run all tests."""
    print("\n")
    print("="*80)
    print("APKScanner - Real APK Analysis Test".center(80))
    print("="*80)
    
    # Test health
    if not test_health():
        print("\n✗ Server is not responding. Start the server first:")
        print("  python -m uvicorn main:app --host 127.0.0.1 --port 8001")
        return
    
    # Upload and analyze APK
    result = test_upload_apk(APK_FILE)
    
    if result:
        # Display results
        display_pipeline_results(result)
        
        # Get APK list
        apks = get_apks_list()
        
        if apks:
            # Get details of the most recently added APK
            latest_apk_id = apks[-1].get('id')
            if latest_apk_id:
                get_apk_details(latest_apk_id)
    
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    if result and result.get('success'):
        print("✓ COMPLETE SUCCESS - APK analysis pipeline executed successfully!")
        print("\nThe APK has been analyzed and stored in the database.")
        print("You can now retrieve its analysis data using the API endpoints.")
    else:
        print("✗ Test did not complete successfully.")
        print("\nPossible issues:")
        print("  1. Check if server is running")
        print("  2. Check if APK file is valid")
        print("  3. Review server logs for detailed errors")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
