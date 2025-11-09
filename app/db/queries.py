from sqlalchemy.orm import Session
from app.database import HealthApp
from datetime import datetime
from typing import Dict, Any


def get_or_create_user(db: Session, tgid: str) -> HealthApp:
    """Get or create user record by tgid"""
    user = db.query(HealthApp).filter(HealthApp.tgid == tgid).first()
    
    if not user:
        user = HealthApp(
            tgid=tgid,
            profile={},
            analyses={},
            recommendations={}
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user


def update_profile(db: Session, tgid: str, profile: Dict[str, Any]) -> HealthApp:
    """Update user profile (merge with existing)"""
    user = get_or_create_user(db, tgid)
    
    # Merge profile
    current_profile = user.profile or {}
    current_profile.update(profile)
    user.profile = current_profile
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user


def update_analyses(db: Session, tgid: str, analyses: Dict[str, Any]) -> HealthApp:
    """Update analyses"""
    user = get_or_create_user(db, tgid)
    user.analyses = analyses
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user


def update_recommendations(db: Session, tgid: str, recommendations: Dict[str, Any]) -> HealthApp:
    """Update recommendations"""
    user = get_or_create_user(db, tgid)
    user.recommendations = recommendations
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user


def notify_upload(db: Session, tgid: str, file_name: str, mime: str, size: int) -> HealthApp:
    """Update analyses with upload notification"""
    user = get_or_create_user(db, tgid)
    
    # Get current analyses
    current_analyses = user.analyses or {}
    
    # Update last_upload and history
    upload_info = {
        "fileName": file_name,
        "mime": mime,
        "size": size,
        "uploadedAt": datetime.utcnow().isoformat(),
    }
    
    current_analyses["last_upload"] = upload_info
    
    # Add to history
    upload_history = current_analyses.get("upload_history", [])
    upload_history.append(upload_info)
    current_analyses["upload_history"] = upload_history
    
    user.analyses = current_analyses
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user

