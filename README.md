# APKScanner

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A comprehensive **APK security analysis and decompilation microservice** for Android applications with a complete 5-stage processing pipeline. Built with FastAPI, SQLAlchemy, and modern security analysis techniques.

## 🔄 Processing Pipeline

```
INPUT APK → VALIDATE → EXTRACT → DECOMPILE → ORGANIZE → OUTPUT
   |          |          |          |          |         |
   |    File validation  Metadata   Code      Security   Database
   |    Size check      Extraction Decompile Analysis   Storage
   |    Format check    Permissions APKtool   Risk Score Relationships
   └─ Files are        Manifest    Endpoints Risk Eval   Queries
      validated,       parsing     Extraction Assessment  Persistence
      extracted,
      processed
```

The project implements a robust pipeline for complete APK analysis:
- ✅ **Validate**: File format, size, and structure validation
- ✅ **Extract**: APK metadata extraction using Androguard
- ✅ **Decompile**: APK decompilation with apktool and advanced code analysis
- ✅ **Organize**: Structured data organization and comprehensive risk assessment
- ✅ **Output**: Database storage with relationships and correlation capabilities

See [PIPELINE.md](PIPELINE.md) for detailed pipeline documentation.

## ✨ Key Features

### 🔍 APK Decompilation & Structural Analysis
- **Apktool Integration**: Decode APK resources, manifest files, and reconstruct source structure
- **Androguard Analysis**: Deep bytecode analysis and DEX-to-Java decompilation
- **Complete File Extraction**: Resources, assets, compiled code, and metadata extraction
- **SMALI Code Analysis**: Low-level bytecode inspection for security patterns

### 🛡️ Android Manifest Security Analysis
- **Comprehensive Parsing**: Extract all security-critical information from AndroidManifest.xml
- **Permission Analysis**: Identify requested permissions with risk categorization
- **Component Security**: Check export status of Activities, Services, Broadcast Receivers, and Content Providers
- **Security Flags Assessment**: Analyze critical attributes:
  - `debuggable` - Debug mode detection
  - `allowBackup` - Data backup vulnerability
  - `usesCleartextTraffic` - Plaintext network communication
  - `networkSecurityConfig` - Custom security configuration

### ⚠️ Permission Risk Assessment
- **Risk Categorization**: Normal, Dangerous, and Signature permission classification
- **Overprivilege Detection**: Identify unnecessary permission requests
- **Attack Vector Mapping**: Correlate permissions with potential security threats
- **Permission Groups**: Analyze permission combinations for elevated risks

### 🔧 Component Analysis
- **Complete Component Inventory**: List all Activities, Services, Receivers, and Providers
- **Intent Filter Analysis**: Detect implicit intents and exposed components
- **Permission Protection**: Identify components without proper access controls
- **Deep Link Security**: Analyze custom URL schemes and intent vulnerabilities

### 🌐 Endpoint & URI Extraction
- **Hardcoded URL Detection**: Scan decompiled code for embedded URLs and API endpoints
- **External Service Analysis**: Identify connections to external services and APIs
- **Deep Link Extraction**: Discover custom URL schemes and app linking configurations
- **URI Pattern Analysis**: Detect potentially sensitive data in URLs

### 💾 Metadata Storage & Organization
- **SQLite Database**: Persistent storage with ACID compliance
- **Relationship Management**: Maintain connections between components, permissions, and findings
- **Query Capabilities**: Enable complex searches and correlation analysis
- **Microservice Integration**: RESTful API for integration with other security tools

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/houssamb4/APKScanner.git
cd APKScanner

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Visit http://localhost:8001/docs for interactive API documentation
```

## 📦 Installation

### Prerequisites
- **Python**: 3.8 or higher
- **Java Runtime Environment (JRE)**: 8 or higher (for apktool)
- **Optional**: Rust toolchain (for enhanced Androguard features)

### Setup Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/houssamb4/APKScanner.git
   cd APKScanner
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Install all requirements
   pip install -r requirements.txt

   # Or use the Makefile
   make install
   ```

4. **Verify Installation**
   ```bash
   # Check pipeline integrity
   python -c "from src.core.pipeline import Pipeline; print('✅ Pipeline ready')"
   ```

### Docker Installation

```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up --build

# Or build manually
docker build -t apkscanner .
docker run -p 8001:8001 apkscanner
```

## 📡 API Documentation

The APKScanner provides a RESTful API with comprehensive OpenAPI documentation available at `http://localhost:8001/docs` when running.

### Core Endpoints

#### 🔍 Analyze APK
Upload and analyze an Android APK file through the complete 5-stage pipeline.

```http
POST /api/v1/analyze
Content-Type: multipart/form-data

file: <apk-file>
Authorization: Bearer <token> (optional)
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8001/api/v1/analyze" \
     -F "file=@/path/to/app.apk"
```

**Response Example:**
```json
{
  "apk_id": 1,
  "package_name": "com.example.secureapp",
  "version_code": "100",
  "version_name": "1.0.0",
  "permissions": {
    "total_permissions": 15,
    "dangerous_permissions": [
      "android.permission.READ_EXTERNAL_STORAGE",
      "android.permission.ACCESS_FINE_LOCATION"
    ],
    "overprivilege_score": 3
  },
  "components": {
    "total_components": 8,
    "exported_components": 2,
    "exposed_components": [
      {
        "type": "activity",
        "name": "com.example.MainActivity",
        "exported": true,
        "permission": null
      }
    ]
  },
  "security_flags": {
    "debuggable": false,
    "allow_backup": true,
    "uses_cleartext_traffic": false,
    "network_security_config": null,
    "total_issues": 1
  },
  "endpoints": [
    {
      "url": "https://api.example.com/v1/data",
      "type": "hardcoded"
    }
  ],
  "security_analysis": {
    "api_keys_found": 0,
    "risk_level": "MEDIUM",
    "findings": []
  },
  "crypto_usage": {
    "algorithms_detected": ["AES", "RSA"],
    "weak_crypto_found": false
  },
  "overall_risk_score": 6
}
```

#### 📋 List Analyzed APKs
Retrieve a paginated list of all analyzed APKs.

```http
GET /api/v1/apks?skip=0&limit=10
```

**Response:**
```json
{
  "total": 25,
  "apks": [
    {
      "id": 1,
      "filename": "app.apk",
      "package_name": "com.example.app",
      "version_name": "1.0.0",
      "overall_risk_score": 6,
      "analyzed_at": "2025-12-21T15:00:00Z"
    }
  ]
}
```

#### 📄 Get APK Details
Retrieve detailed analysis results for a specific APK.

```http
GET /api/v1/apks/{apk_id}
```

**Response:** Complete analysis object (same as analyze endpoint)

#### 🏥 Health Check
Check service availability and basic statistics.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "total_analyzed": 42,
  "uptime": "2h 30m"
}
```

### Error Responses

```json
{
  "detail": "File validation failed: Invalid APK format",
  "error_code": "VALIDATION_ERROR"
}
```

Common error codes:
- `VALIDATION_ERROR`: File format/size issues
- `DECOMPILATION_ERROR`: APK processing failed
- `DATABASE_ERROR`: Storage issues
- `ANALYSIS_ERROR`: Analysis pipeline failure

## ⚙️ Configuration

Create a `.env` file in the project root (copy from `.env.example`) to customize the service behavior.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./apkscanner.db` | Database connection string (SQLite/PostgreSQL) |
| `TEMP_DIR` | `./temp` | Directory for temporary APK processing files |
| `LOGS_DIR` | `./logs` | Directory for application log files |
| `APKTOOL_PATH` | `apktool` | Path to apktool executable or JAR file |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_FILE_SIZE` | `104857600` | Maximum APK file size in bytes (100MB default) |
| `SECRET_KEY` | `auto-generated` | Secret key for security features |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of allowed hosts |

### Example `.env` Configuration

```env
# Database Configuration
DATABASE_URL=sqlite:///./apkscanner.db

# File System Paths
TEMP_DIR=./temp
LOGS_DIR=./logs

# Tool Paths
APKTOOL_PATH=tools/apktool.jar

# Logging
LOG_LEVEL=DEBUG

# Security Limits
MAX_FILE_SIZE=52428800  # 50MB limit

# Network Security
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### Advanced Configuration

For production deployments, consider:
- Using PostgreSQL instead of SQLite for better concurrency
- Setting up log rotation for the `LOGS_DIR`
- Configuring proper file permissions for `TEMP_DIR`
- Using environment-specific configuration files

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
make test

# Or manually
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual component testing (`test_analyzer.py`)
- **API Tests**: Endpoint validation (`test_api.py`)
- **Integration Tests**: Full pipeline validation

### Manual Testing
```bash
# Start service in test mode
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Test health endpoint
curl http://localhost:8001/api/v1/health

# Test APK analysis (replace with actual APK)
curl -X POST "http://localhost:8001/api/v1/analyze" \
     -F "file=@test.apk"
```

## 🏗️ Architecture

### Core Components

```
APKScanner/
├── 📡 API Layer (FastAPI)
│   ├── Routes: REST endpoints
│   ├── Schemas: Request/Response models
│   └── Dependencies: Authentication & validation
├── 🔄 Pipeline Core
│   ├── Validators: File validation
│   ├── Config: Settings management
│   └── Dependencies: DI container
├── 🔧 Services Layer
│   ├── APK Analyzer: Main orchestration
│   ├── Decompiler: APK processing
│   ├── Manifest Parser: XML analysis
│   └── Permission Checker: Security assessment
├── 💾 Data Layer
│   ├── Models: SQLAlchemy ORM
│   ├── Session: DB connections
│   └── CRUD: Data operations
└── 🛠️ Utils
    ├── File Handler: Upload/download
    └── Logger: Structured logging
```

### Data Flow
1. **Input**: APK file uploaded via API
2. **Validation**: File format and security checks
3. **Processing**: Decompilation and analysis pipeline
4. **Storage**: Results stored in database
5. **Output**: JSON response with analysis results

## 🔧 Development

### Project Structure Details

```
apkscanner/
├── src/                    # Source code
│   ├── api/               # REST API layer
│   ├── core/              # Pipeline & configuration
│   ├── services/          # Business logic
│   ├── database/          # Data persistence
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── temp/                  # Temporary files (auto-cleaned)
├── logs/                  # Application logs
├── tools/                 # External tools (apktool)
├── docker/                # Containerization
└── docs/                  # Documentation
```

### Code Quality
- **Type Hints**: Full type annotation support
- **Linting**: Follow PEP 8 standards
- **Testing**: 90%+ test coverage target
- **Documentation**: Comprehensive docstrings

## 🚨 Security Considerations

### Safe APK Handling
- **Sandboxing**: All APK processing occurs in isolated temporary directories
- **Cleanup**: Automatic removal of temporary files after analysis
- **No Storage**: Original APK files are never retained on disk
- **Metadata Only**: Database stores analysis results, not APK content

### Best Practices
- **Containerization**: Run in Docker for additional isolation
- **Network Security**: Configure firewall rules appropriately
- **Access Control**: Implement authentication for production use
- **Monitoring**: Enable logging and monitoring for security events

### Known Limitations
- **Memory Usage**: Large APKs may require significant RAM
- **Processing Time**: Complex APKs can take several minutes to analyze
- **False Positives**: Some benign patterns may trigger security warnings

## 🐛 Troubleshooting

### Common Issues

**❌ "apktool not found" Error**
```bash
# Ensure apktool is installed
java -jar tools/apktool.jar --version

# Or install via package manager
# Ubuntu/Debian:
sudo apt install apktool
# macOS:
brew install apktool
```

**❌ "Androguard not available" Warning**
```bash
# Install Rust (required for androguard)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install androguard
pip install androguard[all]
```

**❌ Database Connection Issues**
```bash
# Check database file permissions
ls -la apkscanner.db

# Reset database if corrupted
rm apkscanner.db
python -c "from src.database.session import create_tables; create_tables()"
```

**❌ Memory/Performance Issues**
```bash
# Increase system limits
export PYTHONPATH=$PYTHONPATH:.
ulimit -n 4096

# Monitor resource usage
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug

# Check logs
tail -f logs/apkscanner.log
```

### Health Checks
```bash
# API health
curl http://localhost:8001/api/v1/health

# Pipeline validation
python -c "from src.core.pipeline import Pipeline; p = Pipeline(); print('Pipeline OK')"
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup
```bash
# Fork and clone
git clone https://github.com/houssamb4/APKScanner.git
cd APKScanner

# Create feature branch
git checkout -b feature/amazing-enhancement

# Set up development environment
make install-dev
```

### Code Standards
- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Add type annotations to new functions
- **Docstrings**: Document all public functions and classes
- **Tests**: Add tests for new features (aim for 90%+ coverage)

### Pull Request Process
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Testing Your Changes
```bash
# Run full test suite
make test

# Run linting
make lint

# Check coverage
make coverage
```

### Reporting Issues
- Use the GitHub issue tracker
- Include APK samples if possible (or describe the issue)
- Provide steps to reproduce
- Include environment details (Python version, OS, etc.)

## 🙏 Acknowledgments

- **Androguard**: For powerful Android analysis capabilities
- **Apktool**: For reliable APK decompilation
- **FastAPI**: For the excellent web framework
- **SQLAlchemy**: For robust database operations