"""Tests for the API endpoints."""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def test_db():
    """Create a test database."""
    from src.database.models import Base
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    return override_get_db


@pytest.fixture
def client(test_db):
    """Create a test client."""
    from main import app
    from src.database.session import get_db
    
    app.dependency_overrides[get_db] = test_db
    
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'service' in data


class TestAnalyzeEndpoint:
    """Test APK analysis endpoint."""
    
    def test_analyze_invalid_file_extension(self, client):
        """Test upload with invalid file extension."""
        with open('test.txt', 'wb') as f:
            f.write(b'test content')
        
        try:
            with open('test.txt', 'rb') as f:
                response = client.post(
                    "/api/v1/analyze",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "APK" in data.get('detail', '')
        finally:
            import os
            if os.path.exists('test.txt'):
                os.remove('test.txt')
    
    @patch('src.core.pipeline.APKPipeline.process_apk')
    def test_analyze_apk_success(self, mock_process, client):
        """Test successful APK analysis."""
        # Mock pipeline response
        mock_process.return_value = (True, {
            'success': True,
            'stages': {
                'validate': {'success': True, 'message': 'Valid'},
                'extract': {'success': True, 'message': 'Extracted'},
                'decompile': {'success': True, 'message': 'Decompiled'},
                'organize': {'success': True, 'message': 'Organized'},
                'output': {'success': True, 'message': 'Output'}
            },
            'data': {
                'apk_id': 1,
                'package_name': 'com.example.app',
                'version_code': '1',
                'version_name': '1.0',
                'permissions': {},
                'components': {},
                'security_flags': {},
                'endpoints': [],
                'overall_risk_score': 5
            }
        })
        
        import tempfile
        import os
        
        # Create a temporary APK file
        with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as f:
            temp_path = f.name
            f.write(b'PK\x03\x04')  # ZIP file signature
        
        try:
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/api/v1/analyze",
                    files={"file": ("test.apk", f, "application/vnd.android.package-archive")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestAPKsListEndpoint:
    """Test APKs list endpoint."""
    
    def test_get_apks_empty(self, client):
        """Test getting empty APKs list."""
        response = client.get("/api/v1/apks")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_apks_with_pagination(self, client):
        """Test APKs list with pagination."""
        response = client.get("/api/v1/apks?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAPKDetailsEndpoint:
    """Test APK details endpoint."""
    
    def test_get_apk_details_not_found(self, client):
        """Test getting details for non-existent APK."""
        response = client.get("/api/v1/apks/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get('detail', '').lower()
    
    def test_get_apk_details_success(self, client, test_db):
        """Test getting APK details."""
        from src.database.models import APK
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create test APK in DB
        engine = create_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        from src.database.models import Base
        Base.metadata.create_all(bind=engine)
        
        db = TestingSessionLocal()
        apk = APK(
            filename='test.apk',
            package_name='com.example.test',
            version_code='1',
            version_name='1.0',
            min_sdk='21',
            target_sdk='30',
            debuggable=False,
            allow_backup=True,
            uses_cleartext_traffic=False,
            network_security_config=''
        )
        db.add(apk)
        db.commit()
        db.refresh(apk)
        
        response = client.get(f"/api/v1/apks/{apk.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data['package_name'] == 'com.example.test'
        assert data['version_code'] == '1'
        
        db.close()


class TestPipelineFlow:
    """Test complete pipeline flow."""
    
    @patch('src.services.decompiler.Decompiler.analyze_with_androguard')
    @patch('src.services.manifest_parser.ManifestParser.parse_manifest')
    def test_pipeline_stages(self, mock_manifest, mock_androguard):
        """Test pipeline executes all stages."""
        from src.core.pipeline import APKPipeline
        
        # Mock androguard response
        mock_androguard.return_value = {
            'package_name': 'com.example.app',
            'version_code': '1',
            'version_name': '1.0',
            'min_sdk': '21',
            'target_sdk': '30',
            'permissions': [],
            'activities': [],
            'services': [],
            'receivers': [],
            'providers': [],
            'intent_filters': {},
            'manifest_xml': '<manifest></manifest>'
        }
        
        # Mock manifest parser response
        mock_manifest.return_value = {
            'package': 'com.example.app',
            'version_code': '1',
            'version_name': '1.0',
            'permissions': [],
            'components': {'activities': [], 'services': [], 'receivers': [], 'providers': []},
            'security_flags': {'debuggable': False, 'allow_backup': True, 'uses_cleartext_traffic': False}
        }
        
        pipeline = APKPipeline()
        
        # Test validation stage
        valid, error = pipeline._stage_validate(__file__)
        assert not valid  # Current test file is not an APK
        assert error  # Should have error message
