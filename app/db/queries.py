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
    """Update analyses with upload notification
    
    NOTE: This function is kept for backward compatibility but should not be used
    if analyses should only contain reports from HTTP Request.
    Upload data should be stored separately or not stored in analyses field.
    """
    user = get_or_create_user(db, tgid)
    
    # Get current analyses (preserve existing reports)
    current_analyses = user.analyses or {}
    
    # Preserve existing reports if they exist
    reports = current_analyses.get("reports", [])
    last_report = current_analyses.get("last_report")
    
    # Update last_upload and history (but preserve reports)
    upload_info = {
        "fileName": file_name,
        "mime": mime,
        "size": size,
        "uploadedAt": datetime.utcnow().isoformat(),
    }
    
    # Only add upload data if we're not using analyses for reports only
    # For now, we'll preserve both, but the user wants analyses to contain only reports
    # So we'll skip adding upload data here
    # current_analyses["last_upload"] = upload_info
    # upload_history = current_analyses.get("upload_history", [])
    # upload_history.append(upload_info)
    # current_analyses["upload_history"] = upload_history
    
    # Keep only reports in analyses
    if reports or last_report:
        current_analyses = {
            "reports": reports,
            "last_report": last_report
        }
    else:
        # If no reports, keep empty
        current_analyses = {}
    
    user.analyses = current_analyses
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user

