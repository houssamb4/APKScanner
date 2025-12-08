#!/usr/bin/env python3
"""Create a minimal test APK for endpoint testing."""

import zipfile
import os

# Create a minimal valid APK file for testing
test_apk_path = 'temp/test.apk'
os.makedirs('temp', exist_ok=True)

# Create a ZIP file with minimum APK structure
with zipfile.ZipFile(test_apk_path, 'w') as zf:
    # Add minimal AndroidManifest.xml
    manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.test">
    <uses-permission android:name="android.permission.INTERNET" />
    <application
        android:label="TestApp">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
    zf.writestr('AndroidManifest.xml', manifest)
    
    # Add a minimal classes.dex file (actually just a dummy file)
    zf.writestr('classes.dex', b'dex\n\x00\x00\x00\x00')

print(f'Test APK created: {test_apk_path}')
print(f'File size: {os.path.getsize(test_apk_path)} bytes')
