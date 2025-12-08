#!/usr/bin/env python3
"""Quick test script for APKScanner API endpoints."""

import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*70)
    print("Testing Health Endpoint")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_apks():
    """Test GET /apks endpoint."""
    print("\n" + "="*70)
    print("Testing GET /apks Endpoint")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/apks")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_pipeline_validation():
    """Test pipeline structure."""
    print("\n" + "="*70)
    print("Testing Pipeline Structure")
    print("="*70)
    
    from src.core.pipeline import APKPipeline, PipelineStage
    
    try:
        pipeline = APKPipeline()
        stages = [
            PipelineStage.VALIDATE,
            PipelineStage.EXTRACT,
            PipelineStage.DECOMPILE,
            PipelineStage.ORGANIZE,
            PipelineStage.OUTPUT
        ]
        
        print("Pipeline Stages:")
        for i, stage in enumerate(stages, 1):
            print(f"  {i}. {stage.upper()}")
        
        print(f"\nPipeline Orchestrator: OK")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("APKScanner API Test Suite")
    print("="*70)
    
    results = []
    
    results.append(("Health Check", test_health()))
    results.append(("GET /apks", test_get_apks()))
    results.append(("Pipeline", test_pipeline_validation()))
    
    # Summary
    print("\n" + "="*70)
    print("Test Results Summary")
    print("="*70)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:30} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print("="*70)
    if all_passed:
        print("All tests PASSED!")
        print("\nServer is running and ready for APK analysis.")
        print("Endpoint: http://127.0.0.1:8001/api/v1")
    else:
        print("Some tests FAILED")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
