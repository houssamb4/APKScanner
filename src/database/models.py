from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association table for many-to-many relationship between APK and Permissions
apk_permissions = Table(
    'apk_permissions',
    Base.metadata,
    Column('apk_id', Integer, ForeignKey('apks.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# Association table for APK and Components
apk_components = Table(
    'apk_components',
    Base.metadata,
    Column('apk_id', Integer, ForeignKey('apks.id'), primary_key=True),
    Column('component_id', Integer, ForeignKey('components.id'), primary_key=True)
)

class APK(Base):
    __tablename__ = 'apks'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    package_name = Column(String)
    version_code = Column(String)
    version_name = Column(String)
    min_sdk = Column(String)
    target_sdk = Column(String)
    debuggable = Column(Boolean, default=False)
    allow_backup = Column(Boolean, default=False)
    uses_cleartext_traffic = Column(Boolean, default=False)
    network_security_config = Column(Text)

    # Relationships
    permissions = relationship("Permission", secondary=apk_permissions, back_populates="apks")
    components = relationship("Component", secondary=apk_components, back_populates="apks")
    endpoints = relationship("Endpoint", back_populates="apk")

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    protection_level = Column(String)  # normal, dangerous, signature, etc.
    description = Column(Text)

    # Relationships
    apks = relationship("APK", secondary=apk_permissions, back_populates="permissions")

class Component(Base):
    __tablename__ = 'components'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # Activity, Service, BroadcastReceiver, ContentProvider
    name = Column(String)
    exported = Column(Boolean, default=False)
    permission = Column(String)
    intent_filters = Column(Text)  # JSON string of intent filters

    # Relationships
    apks = relationship("APK", secondary=apk_components, back_populates="components")

class Endpoint(Base):
    __tablename__ = 'endpoints'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    type = Column(String)  # hardcoded, api, deeplink, etc.
    apk_id = Column(Integer, ForeignKey('apks.id'))

    # Relationships
    apk = relationship("APK", back_populates="endpoints")