from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import text
from app.database import HealthApp
from datetime import datetime
from typing import Dict, Any
import copy
import json


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
    """Update user profile (merge with existing)
    
    Args:
        db: Database session
        tgid: Telegram user ID
        profile: Dictionary with profile data to update (will be merged with existing)
    
    Returns:
        Updated HealthApp user record
    """
    print(f"[update_profile] Starting update for tgid: {tgid}")
    print(f"[update_profile] Received profile data: {profile}")
    
    user = get_or_create_user(db, tgid)
    
    # Get current profile and create a copy to avoid mutation issues
    current_profile = user.profile or {}
    if not isinstance(current_profile, dict):
        current_profile = {}
        print(f"[update_profile] Warning: profile was not a dict, resetting to empty dict")
    
    print(f"[update_profile] Current profile before merge: {current_profile}")
    
    # Create a new dict by copying current and updating with new data
    # This ensures we create a new object reference for SQLAlchemy
    updated_profile = copy.deepcopy(current_profile)
    updated_profile.update(profile)
    
    print(f"[update_profile] Updated profile after merge: {updated_profile}")
    print(f"[update_profile] Profile keys: {list(updated_profile.keys())}")
    
    # Method 1: Try direct assignment with flag_modified
    # Create a completely new dict object to ensure SQLAlchemy detects the change
    new_profile = dict(updated_profile)
    user.profile = new_profile
    user.updated_at = datetime.utcnow()
    
    # Explicitly mark the JSONB column as modified so SQLAlchemy saves it
    # This is critical for JSON/JSONB columns in PostgreSQL
    flag_modified(user, "profile")
    
    # Flush to ensure changes are sent to database
    db.flush()
    
    print(f"[update_profile] Profile after flush: {user.profile}")
    print(f"[update_profile] Committing to database...")
    
    db.commit()
    db.refresh(user)
    
    print(f"[update_profile] Profile after commit and refresh: {user.profile}")
    print(f"[update_profile] Profile type: {type(user.profile)}")
    print(f"[update_profile] Final profile keys: {list(user.profile.keys()) if user.profile else 'None'}")
    
    # Double-check: Query directly from database to verify
    verify_user = db.query(HealthApp).filter(HealthApp.tgid == tgid).first()
    if verify_user:
        print(f"[update_profile] Verification query - profile: {verify_user.profile}")
        print(f"[update_profile] Verification query - profile keys: {list(verify_user.profile.keys()) if verify_user.profile else 'None'}")
    
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

