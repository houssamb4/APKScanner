# APKScanner - Complete APK Analysis Pipeline

A comprehensive APK security analysis and decompilation microservice for Android applications with a complete processing pipeline.

## 🔄 Processing Pipeline

The project implements a robust 5-stage pipeline for APK analysis:

```
Input APK → Validate → Extract → Decompile → Organize → Output
```

### Pipeline Stages

#### 1. **VALIDATE** ✓
Validates the APK file before processing:
- ✅ File existence check
- ✅ File size validation (max 100MB)
- ✅ File extension validation (.apk)
- ✅ ZIP format validation (APKs are ZIP files)
- ✅ APK structure validation (must contain AndroidManifest.xml and classes.dex)

**Code**: `src/core/validators.py`

#### 2. **EXTRACT** ✓
Extracts APK metadata using Androguard:
- ✅ Package name and version information
- ✅ Permissions list
- ✅ SDK version information (min/target)
- ✅ Application components (Activities, Services, Receivers, Providers)
- ✅ Android Manifest XML parsing
- ✅ Intent filter extraction

**Code**: `src/services/decompiler.py` → `analyze_with_androguard()`

#### 3. **DECOMPILE** ✓
Decompiles APK using apktool and analyzes code:
- ✅ Resource decompilation
- ✅ Manifest XML extraction
- ✅ Dex code decompilation
- ✅ Hardcoded URL/endpoint extraction from SMALI code

**Code**: `src/services/decompiler.py` → `decompile_with_apktool()`

#### 4. **ORGANIZE** ✓
Organizes analysis into structured format:
- ✅ Manifest parsing with security analysis
- ✅ Permission risk assessment
- ✅ Component exposure detection
- ✅ Security flags assessment
- ✅ Endpoint organization

**Code**: `src/core/pipeline.py` → `_stage_organize()`

#### 5. **OUTPUT** ✓
Stores results in database:
- ✅ APK metadata storage
- ✅ Permission relationships
- ✅ Component storage
- ✅ Endpoint storage
- ✅ Risk score calculation

**Code**: `src/core/pipeline.py` → `_stage_output()`

## 📁 Project Structure

```
APKScanner/
├── main.py                          # FastAPI application entry point
├── validate_pipeline.py             # Pipeline validation and testing script
├── requirements.txt                 # Python dependencies
├── Makefile                        # Build commands
├── .env                            # Environment configuration
│
├── src/
│   ├── api/
│   │   ├── routes.py              # API endpoints (POST /analyze, GET /apks, etc.)
│   │   └── schemas.py             # Pydantic response schemas
│   │
│   ├── core/
│   │   ├── config.py              # Application configuration
│   │   ├── pipeline.py            # Main pipeline orchestrator (5 stages)
│   │   ├── validators.py          # APK file validators
│   │   ├── dependencies.py        # Dependency injection
│   │   └── security.py            # Security utilities
│   │
│   ├── services/
│   │   ├── apk_analyzer.py        # APK analysis orchestrator
│   │   ├── decompiler.py          # Androguard and apktool wrapper
│   │   ├── manifest_parser.py     # XML manifest parsing
│   │   └── permission_checker.py  # Security analysis
│   │
│   ├── database/
│   │   ├── models.py              # SQLAlchemy ORM models
│   │   ├── session.py             # Database session management
│   │   └── crud.py                # Database operations
│   │
│   └── utils/
│       ├── logger.py              # Logging configuration
│       └── file_handler.py        # File operations
│
├── tests/
│   ├── test_analyzer.py           # Unit tests for analysis
│   └── test_api.py                # API endpoint tests
│
├── docker/
│   ├── Dockerfile                 # Container definition
│   └── docker-compose.yml         # Multi-container setup
│
└── logs/                          # Application logs

```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
cd APKScanner

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p temp logs
```

### 2. Configuration

Edit `.env` file:
```env
DATABASE_URL=sqlite:///./apkscanner.db
TEMP_DIR=./temp
LOGS_DIR=./logs
APKTOOL_PATH=tools/apktool.bat
LOG_LEVEL=INFO
MAX_FILE_SIZE=104857600
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8001
```

### 3. Run Application

```bash
# Using make
make install
make run

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 4. Test Pipeline

```bash
# Run validation script with test APK
python validate_pipeline.py --create-test-apk --verbose

# Or test with real APK
python validate_pipeline.py /path/to/app.apk
```

## 📊 API Endpoints

### 1. POST `/api/v1/analyze`
Analyze an APK file through the complete pipeline.

**Request:**
```bash
curl -F "file=@myapp.apk" http://localhost:8001/api/v1/analyze
```

**Response:**
```json
{
  "success": true,
  "stages": {
    "validate": {"success": true, "message": "APK file validation successful"},
    "extract": {"success": true, "message": "APK metadata extraction successful"},
    "decompile": {"success": true, "message": "APK decompilation successful"},
    "organize": {"success": true, "message": "Analysis organization successful"},
    "output": {"success": true, "message": "Results stored successfully"}
  },
  "data": {
    "apk_id": 1,
    "package_name": "com.example.app",
    "version_code": "1",
    "version_name": "1.0.0",
    "permissions": {...},
    "components": {...},
    "security_flags": {...},
    "endpoints": [...],
    "overall_risk_score": 5
  }
}
```

### 2. GET `/api/v1/apks`
List all analyzed APKs with pagination.

```bash
curl "http://localhost:8001/api/v1/apks?skip=0&limit=10"
```

### 3. GET `/api/v1/apks/{apk_id}`
Get detailed analysis for a specific APK.

```bash
curl http://localhost:8001/api/v1/apks/1
```

### 4. GET `/api/v1/health`
Health check endpoint.

```bash
curl http://localhost:8001/api/v1/health
```

## 🧪 Testing

### Run All Tests
```bash
# Run pytest
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test
```bash
pytest tests/test_analyzer.py::TestAPKValidator::test_validate_apk_file_not_found -v
```

### Validate Pipeline
```bash
# Create test APK and run through entire pipeline
python validate_pipeline.py --create-test-apk --verbose

# Test with real APK
python validate_pipeline.py /path/to/real_app.apk --verbose
```

## 🔍 Key Features

### APK Decompilation and Analysis
- ✅ Uses Apktool to decode APK resources and manifest
- ✅ Employs Androguard for bytecode analysis and decompilation
- ✅ Extracts complete file structure

### Android Manifest Security Analysis
- ✅ Extracts all permissions with risk levels
- ✅ Checks component export status
- ✅ Analyzes security flags (debuggable, allowBackup, etc.)

### Permission Risk Assessment
- ✅ Categorizes by protection level (normal, dangerous, signature)
- ✅ Identifies permission overprivilege
- ✅ Maps permissions to attack vectors

### Component Analysis
- ✅ Lists Activities, Services, Receivers, Providers
- ✅ Identifies components with implicit intents
- ✅ Detects intent filters

### Endpoint Extraction
- ✅ Scans decompiled code for hardcoded URLs
- ✅ Identifies API endpoints and URIs
- ✅ Extracts deep links and custom URL schemes

### Database Storage
- ✅ SQLite database for results persistence
- ✅ Relationship management (APK ↔ Permissions ↔ Components)
- ✅ Query and correlation support

## 📋 Database Models

### APK
```python
- id (Integer, Primary Key)
- filename (String)
- package_name (String)
- version_code (String)
- version_name (String)
- min_sdk (String)
- target_sdk (String)
- debuggable (Boolean)
- allow_backup (Boolean)
- uses_cleartext_traffic (Boolean)
- network_security_config (Text)
- relationships: permissions, components, endpoints
```

### Permission
```python
- id (Integer, Primary Key)
- name (String, Unique)
- protection_level (String)
- description (Text)
- relationships: apks
```

### Component
```python
- id (Integer, Primary Key)
- type (String) - Activity, Service, Receiver, Provider
- name (String)
- exported (Boolean)
- permission (String)
- intent_filters (Text)
- relationships: apks
```

### Endpoint
```python
- id (Integer, Primary Key)
- url (String)
- type (String)
- apk_id (Integer, Foreign Key)
- relationships: apk
```

## 🐳 Docker Deployment

### Build Image
```bash
make docker-build
```

### Run Container
```bash
make docker-run
```

### With Docker Compose
```bash
docker-compose -f docker/docker-compose.yml up
```

## 📝 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./apkscanner.db` | Database connection string |
| `TEMP_DIR` | `./temp` | Temporary files directory |
| `LOGS_DIR` | `./logs` | Application logs directory |
| `APKTOOL_PATH` | `tools/apktool.bat` | Path to apktool executable |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE` | `104857600` | Max APK size (100MB) |
| `UVICORN_HOST` | `0.0.0.0` | Server host |
| `UVICORN_PORT` | `8001` | Server port |

## 🔒 Security Considerations

1. **File Size Limits**: Maximum 100MB per APK
2. **Temporary File Cleanup**: Automatic cleanup after processing
3. **Database Isolation**: Each APK stored separately
4. **Permission Analysis**: Identifies high-risk permissions
5. **Component Exposure**: Detects improperly exported components
6. **Debuggable Flag**: Alerts on debuggable applications

## 📦 Dependencies

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Androguard**: Android bytecode analysis
- **Apktool**: APK resource/manifest decompilation
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

Full list in `requirements.txt`

## 🚨 Troubleshooting

### Apktool Not Found
```bash
# Windows
set APKTOOL_PATH=tools\apktool.bat

# Linux/Mac
export APKTOOL_PATH=$(which apktool)
```

### Database Issues
```bash
# Reset database
rm apkscanner.db
python -c "from src.database.session import create_tables; create_tables()"
```

### Missing Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## 📄 License

MIT License - See LICENSE file for details

## 👥 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Last Updated**: December 8, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
