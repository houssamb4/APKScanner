#!/usr/bin/env python3
"""Test the analyze endpoint with a test APK."""

import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1"
APK_FILE = "temp/test.apk"

try:
    with open(APK_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/analyze", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
