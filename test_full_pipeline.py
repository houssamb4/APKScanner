#!/usr/bin/env python3
"""Test analyze endpoint with androguard enabled."""

import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"
APK_FILE = "temp/valid_test.apk"

print("="*80)
print("APKScanner Full Pipeline Test with Androguard")
print("="*80)

try:
    print("\n[1] Testing health endpoint...")
    health = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health: {health.json()}")
    
    print("\n[2] Uploading APK and running complete pipeline...")
    with open(APK_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/analyze", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"\nPipeline Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Error: {result.get('error')}")
    
    if 'stages' in result:
        print(f"\nStage Results:")
        for stage_name, stage_result in result['stages'].items():
            status = "✓ PASS" if stage_result.get('success') else "✗ FAIL"
            print(f"  {stage_name.upper():15} {status}")
            if not stage_result.get('success'):
                print(f"    Message: {stage_result.get('message')}")
    
    if result.get('data'):
        print(f"\nAnalysis Data:")
        data = result['data']
        if isinstance(data, dict):
            for key, value in data.items():
                if key != 'analysis':
                    print(f"  {key}: {value}")
        print(f"\n[3] Checking database persistence...")
        apks_response = requests.get(f"{BASE_URL}/apks")
        apks = apks_response.json()
        print(f"✓ Total APKs in database: {len(apks)}")
        if apks:
            print(f"  Latest APK: {apks[-1].get('filename') if isinstance(apks[-1], dict) else apks[-1]}")
    
    print("\n" + "="*80)
    print("✓ FULL PIPELINE TEST COMPLETED SUCCESSFULLY")
    print("="*80)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
