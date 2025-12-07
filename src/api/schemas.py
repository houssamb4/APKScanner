from pydantic import BaseModel
from typing import List, Dict, Optional

class PermissionBase(BaseModel):
    name: str
    protection_level: str
    is_dangerous: bool

class ComponentBase(BaseModel):
    type: str
    name: str
    exported: bool
    permission: Optional[str] = None

class EndpointBase(BaseModel):
    url: str
    type: str

class SecurityIssue(BaseModel):
    type: str
    severity: str
    description: str

class AnalysisResult(BaseModel):
    apk_id: int
    package_name: str
    version_code: Optional[str]
    version_name: Optional[str]
    permissions: Dict
    components: Dict
    security_flags: Dict
    endpoints: List[Dict]
    overall_risk_score: int

class APKUpload(BaseModel):
    filename: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None