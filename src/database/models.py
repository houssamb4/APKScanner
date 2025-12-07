from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class APKAnalysis(Base):
    __tablename__ = "apk_analyses"
    
    id = Column(String, primary_key=True)
    package_name = Column(String)
    version = Column(String)
    analysis_date = Column(DateTime, default=datetime.datetime.utcnow)
    permissions = Column(JSON)
    security_findings = Column(JSON)
    raw_data = Column(JSON)