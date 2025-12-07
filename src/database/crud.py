from sqlalchemy.orm import Session
from . import models

def create_apk(db: Session, apk_data: dict):
    apk = models.APK(**apk_data)
    db.add(apk)
    db.commit()
    db.refresh(apk)
    return apk

def get_apk(db: Session, apk_id: int):
    return db.query(models.APK).filter(models.APK.id == apk_id).first()

def get_apks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.APK).offset(skip).limit(limit).all()

def create_permission(db: Session, permission_data: dict):
    permission = models.Permission(**permission_data)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission

def get_permission_by_name(db: Session, name: str):
    return db.query(models.Permission).filter(models.Permission.name == name).first()

def create_component(db: Session, component_data: dict):
    component = models.Component(**component_data)
    db.add(component)
    db.commit()
    db.refresh(component)
    return component

def create_endpoint(db: Session, endpoint_data: dict):
    endpoint = models.Endpoint(**endpoint_data)
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint

def get_endpoints_by_apk(db: Session, apk_id: int):
    return db.query(models.Endpoint).filter(models.Endpoint.apk_id == apk_id).all()