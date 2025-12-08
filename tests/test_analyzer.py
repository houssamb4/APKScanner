"""Unit tests for APK analyzer module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import tempfile


# Mock the androguard import if not available
pytest.importorskip("fastapi")


class TestAPKValidator:
    """Test APK file validation."""
    
    def test_validate_apk_file_not_found(self):
        """Test validation of non-existent file."""
        from src.core.validators import APKValidator
        
        validator = APKValidator()
        valid, error = validator.validate_apk_file("/path/to/nonexistent.apk")
        
        assert not valid
        assert "not found" in error.lower()
    
    def test_validate_apk_file_empty(self):
        """Test validation of empty file."""
        from src.core.validators import APKValidator
        
        validator = APKValidator()
        
        # Create empty temp file
        with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as f:
            temp_path = f.name
        
        try:
            valid, error = validator.validate_apk_file(temp_path)
            assert not valid
            assert "empty" in error.lower()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_validate_apk_file_wrong_extension(self):
        """Test validation of file with wrong extension."""
        from src.core.validators import APKValidator
        
        validator = APKValidator()
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = f.name
            f.write(b"test content")
        
        try:
            valid, error = validator.validate_apk_file(temp_path)
            assert not valid
            assert "extension" in error.lower()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_validate_apk_file_too_large(self):
        """Test validation of file that exceeds size limit."""
        from src.core.validators import APKValidator
        
        validator = APKValidator()
        
        with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as f:
            temp_path = f.name
            # Write data exceeding MAX_FILE_SIZE
            f.write(b'x' * (APKValidator.MAX_FILE_SIZE + 1))
        
        try:
            valid, error = validator.validate_apk_file(temp_path)
            assert not valid
            assert "too large" in error.lower()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestPermissionChecker:
    """Test permission checking functionality."""
    
    def test_analyze_permissions_dangerous(self):
        """Test analysis of dangerous permissions."""
        from src.services.permission_checker import PermissionChecker
        
        checker = PermissionChecker()
        permissions = [
            {'name': 'android.permission.READ_SMS', 'protection_level': 'dangerous'},
            {'name': 'android.permission.RECORD_AUDIO', 'protection_level': 'dangerous'},
            {'name': 'android.permission.INTERNET', 'protection_level': 'normal'},
        ]
        
        result = checker.analyze_permissions(permissions)
        
        assert result['total_permissions'] == 3
        assert len(result['dangerous_permissions']) == 2
        assert 'android.permission.READ_SMS' in result['dangerous_permissions']
        assert 'android.permission.RECORD_AUDIO' in result['dangerous_permissions']
        assert 'android.permission.INTERNET' in result['normal_permissions']
    
    def test_check_component_exposure(self):
        """Test component exposure detection."""
        from src.services.permission_checker import PermissionChecker
        
        checker = PermissionChecker()
        components = {
            'activities': [
                {'name': 'MainActivity', 'exported': False, 'permission': None},
                {'name': 'ExposedActivity', 'exported': True, 'permission': None},
            ],
            'services': [
                {'name': 'SomeService', 'exported': True, 'permission': 'custom.permission'}
            ]
        }
        
        result = checker.check_component_exposure(components)
        
        assert result['total_issues'] == 1
        assert len(result['component_issues']) == 1
        assert result['component_issues'][0]['component'] == 'ExposedActivity'
    
    def test_assess_security_flags_debuggable(self):
        """Test security flag assessment for debuggable flag."""
        from src.services.permission_checker import PermissionChecker
        
        checker = PermissionChecker()
        flags = {'debuggable': True, 'allow_backup': False, 'uses_cleartext_traffic': False}
        
        result = checker.assess_security_flags(flags)
        
        assert result['total_issues'] >= 1
        issues = [i for i in result['security_issues'] if i['type'] == 'debuggable_enabled']
        assert len(issues) == 1
        assert issues[0]['severity'] == 'critical'


class TestManifestParser:
    """Test manifest parsing."""
    
    def test_parse_simple_manifest(self):
        """Test parsing a simple manifest."""
        from src.services.manifest_parser import ManifestParser
        
        parser = ManifestParser()
        manifest_xml = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app"
    android:versionCode="1"
    android:versionName="1.0">
    
    <uses-permission android:name="android.permission.INTERNET"/>
    
    <application android:debuggable="false" android:allowBackup="true">
        <activity android:name=".MainActivity" android:exported="true"/>
    </application>
</manifest>'''
        
        result = parser.parse_manifest(manifest_xml)
        
        assert result['package'] == 'com.example.app'
        assert result['version_code'] == '1'
        assert result['version_name'] == '1.0'
        assert len(result['permissions']) == 1
        assert result['permissions'][0]['name'] == 'android.permission.INTERNET'
        assert 'debuggable' in result['security_flags']


class TestDecompiler:
    """Test decompiler functionality."""
    
    @patch('src.services.decompiler.subprocess.run')
    def test_decompile_with_apktool_success(self, mock_run):
        """Test successful APK decompilation."""
        from src.services.decompiler import Decompiler
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        decompiler = Decompiler()
        
        with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as f:
            apk_path = f.name
            f.write(b"test apk")
        
        try:
            result = decompiler.decompile_with_apktool(apk_path)
            assert result is not None
            assert '_decompiled' in result
        finally:
            if os.path.exists(apk_path):
                os.remove(apk_path)
    
    @patch('src.services.decompiler.APK')
    def test_analyze_with_androguard(self, mock_apk_class):
        """Test androguard analysis."""
        from src.services.decompiler import Decompiler
        
        # Mock APK instance
        mock_apk = MagicMock()
        mock_apk.get_package.return_value = 'com.example.app'
        mock_apk.get_androidversion_code.return_value = '1'
        mock_apk.get_androidversion_name.return_value = '1.0'
        mock_apk.get_min_sdk_version.return_value = '21'
        mock_apk.get_target_sdk_version.return_value = '30'
        mock_apk.get_permissions.return_value = ['android.permission.INTERNET']
        mock_apk.get_activities.return_value = ['MainActivity']
        mock_apk.get_services.return_value = []
        mock_apk.get_receivers.return_value = []
        mock_apk.get_providers.return_value = []
        
        # Mock manifest
        mock_manifest = MagicMock()
        mock_manifest.get_xml.return_value = '<manifest></manifest>'
        mock_apk.get_android_manifest_axml.return_value = mock_manifest
        
        mock_apk_class.return_value = mock_apk
        
        decompiler = Decompiler()
        result = decompiler.analyze_with_androguard('/fake/path.apk')
        
        assert result['package_name'] == 'com.example.app'
        assert result['version_code'] == '1'
        assert result['version_name'] == '1.0'
