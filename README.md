# APKScanner

A comprehensive APK security analysis and decompilation microservice for Android applications.

## Features

### APK Decompilation and Structural Analysis
- Uses Apktool to decode APK resources and manifest files
- Employs Androguard for deep bytecode analysis and decompilation
- Extracts the complete file structure including resources, assets, and compiled code

### Android Manifest Security Analysis
- Parses AndroidManifest.xml to extract security-critical information
- Permissions: Identifies all requested permissions, flagging dangerous ones
- Component Export Status: Checks if Activities, Services, Broadcast Receivers, or Content Providers are incorrectly exported
- Security Flags: Analyzes critical attributes like debuggable, allowBackup, usesCleartextTraffic, networkSecurityConfig

### Permission Risk Assessment
- Categorizes permissions by risk level (normal, dangerous, signature)
- Identifies permission overprivilege
- Maps permissions to potential attack vectors

### Component Analysis
- Lists all Activities, Services, Broadcast Receivers, and Content Providers
- Identifies components with implicit intents or no permission protection
- Detects intent filters that might expose components

### Endpoint and URI Extraction
- Scans decompiled code for hardcoded URLs, API endpoints, and URIs
- Identifies potential external service connections
- Extracts deep links and custom URL schemes

### Metadata Storage and Organization
- Stores extracted information in a SQLite database
- Maintains relationships between components, permissions, and security flags
- Enables querying and correlation with findings from other microservices

## Installation

### Prerequisites
- Python 3.8+
- Java Runtime Environment (JRE) - apktool is bundled with the project

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd apkscanner

# Install dependencies
make install

# Or manually
pip install -r requirements.txt
```

## Usage

### Running the Service
```bash
# Development mode
make run

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up --build
```

### API Endpoints

#### Analyze APK
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

file: <apk-file>
```

Response:
```json
{
  "apk_id": 1,
  "package_name": "com.example.app",
  "version_code": "1",
  "version_name": "1.0.0",
  "permissions": {...},
  "components": {...},
  "security_flags": {...},
  "endpoints": [...],
  "overall_risk_score": 7
}
```

#### Get Analyzed APKs
```http
GET /api/v1/apks?skip=0&limit=100
```

#### Get APK Details
```http
GET /api/v1/apks/{apk_id}
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=sqlite:///./apkscanner.db
TEMP_DIR=./temp
LOGS_DIR=./logs
APKTOOL_PATH=apktool
LOG_LEVEL=INFO
MAX_FILE_SIZE=104857600
```

## Testing

```bash
make test
```

## Project Structure

```
apkscanner/
├── src/
│   ├── api/
│   │   ├── routes.py          # FastAPI endpoints
│   │   └── schemas.py         # Pydantic models
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── security.py        # Auth (future)
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── services/
│   │   ├── apk_analyzer.py    # Main analysis logic
│   │   ├── manifest_parser.py # XML parsing
│   │   ├── permission_checker.py
│   │   └── decompiler.py      # Apktool/Androguard wrapper
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── crud.py            # Database operations
│   │   └── session.py         # DB connection
│   └── utils/
│       ├── file_handler.py    # File upload/download
│       └── logger.py          # Logging setup
├── tests/
├── temp/                      # Temporary APK storage
├── logs/                      # Application logs
├── tools/                     # Apktool binaries
├── docker/
├── requirements.txt
├── .env.example
├── Makefile
└── main.py
```

## Security Considerations

- The service analyzes potentially malicious APKs in a sandboxed environment
- All temporary files are cleaned up after analysis
- Database stores metadata only; original APKs are not retained
- Consider running in Docker for additional isolation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

DATABASE_URL=sqlite:///./apkscanner.db
TEMP_DIR=./temp
LOGS_DIR=./logs
APKTOOL_PATH=C:\tools\apktool.bat
LOG_LEVEL=INFO
MAX_FILE_SIZE=104857600  # 100MB
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000  