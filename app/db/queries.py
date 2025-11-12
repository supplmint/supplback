from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import text
from app.database import HealthApp
from datetime import datetime
from typing import Dict, Any
import copy
import json
import os


def get_or_create_user(db: Session, tgid: str) -> HealthApp:
    """Get or create user record by tgid"""
    user = db.query(HealthApp).filter(HealthApp.tgid == tgid).first()
    
    if not user:
        user = HealthApp(
            tgid=tgid,
            profile={},
            analyses={},
            recommendations={},
            allanalize={},
            rekom={}
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
    """Update analyses and also update corresponding report in allanalize"""
    print(f"[update_analyses] Starting update for tgid: {tgid}")
    print(f"[update_analyses] Received analyses data keys: {list(analyses.keys()) if isinstance(analyses, dict) else 'not a dict'}")
    
    user = get_or_create_user(db, tgid)
    
    # Get current analyses
    current_analyses = user.analyses or {}
    if not isinstance(current_analyses, dict):
        current_analyses = {}
    
    print(f"[update_analyses] Current analyses keys: {list(current_analyses.keys())}")
    
    # Get the updated last_report if it exists
    updated_last_report = None
    if "last_report" in analyses and isinstance(analyses["last_report"], dict):
        updated_last_report = analyses["last_report"]
        print(f"[update_analyses] Found updated last_report with text length: {len(updated_last_report.get('text', '')) if isinstance(updated_last_report.get('text'), str) else 0}")
    
    # Merge new data with current data to preserve structure
    # Create a completely new dict object to ensure SQLAlchemy detects the change
    updated_analyses = copy.deepcopy(current_analyses)
    updated_analyses.update(analyses)
    
    # Ensure nested objects are also new dicts
    if "last_report" in updated_analyses and isinstance(updated_analyses["last_report"], dict):
        updated_analyses["last_report"] = dict(updated_analyses["last_report"])
    if "reports" in updated_analyses and isinstance(updated_analyses["reports"], list):
        updated_analyses["reports"] = [dict(r) if isinstance(r, dict) else r for r in updated_analyses["reports"]]
    
    # Update allanalize if we have an updated last_report
    if updated_last_report:
        current_allanalize = user.allanalize or {}
        all_analyses_list = []
        
        # Handle different allanalize formats
        if isinstance(current_allanalize, list):
            all_analyses_list = current_allanalize.copy()
        elif isinstance(current_allanalize, dict):
            if "analyses" in current_allanalize and isinstance(current_allanalize["analyses"], list):
                all_analyses_list = current_allanalize["analyses"].copy()
            elif "history" in current_allanalize and isinstance(current_allanalize["history"], list):
                all_analyses_list = current_allanalize["history"].copy()
        
        # Update the corresponding report in allanalize
        if all_analyses_list and isinstance(updated_last_report, dict):
            report_file_name = updated_last_report.get("fileName")
            report_created_at = updated_last_report.get("createdAt")
            report_text = updated_last_report.get("text")
            
            print(f"[update_analyses] Looking for report in allanalize: fileName={report_file_name}, createdAt={report_created_at}")
            
            # Find and update the matching report
            updated_count = 0
            for i, item in enumerate(all_analyses_list):
                if isinstance(item, dict):
                    # Match by fileName and createdAt
                    if (report_file_name and report_created_at and
                        item.get("fileName") == report_file_name and
                        item.get("createdAt") == report_created_at):
                        # Update this report
                        all_analyses_list[i] = dict(updated_last_report)
                        updated_count += 1
                        print(f"[update_analyses] Updated report at index {i} in allanalize")
                    # Or match by text if fileName/createdAt not available
                    elif report_text and item.get("text") == current_analyses.get("last_report", {}).get("text"):
                        all_analyses_list[i] = dict(updated_last_report)
                        updated_count += 1
                        print(f"[update_analyses] Updated report at index {i} in allanalize (matched by text)")
            
            if updated_count > 0:
                print(f"[update_analyses] Updated {updated_count} report(s) in allanalize")
                user.allanalize = all_analyses_list
                flag_modified(user, "allanalize")
            else:
                print(f"[update_analyses] No matching report found in allanalize to update")
    
    # Create a completely new dict to ensure SQLAlchemy detects the change
    new_analyses = dict(updated_analyses)
    user.analyses = new_analyses
    user.updated_at = datetime.utcnow()
    
    # Explicitly mark the JSONB column as modified
    flag_modified(user, "analyses")
    
    db.flush()
    print(f"[update_analyses] After flush, user.analyses keys: {list(user.analyses.keys()) if isinstance(user.analyses, dict) else 'not a dict'}")
    
    db.commit()
    db.refresh(user)
    
    # Verify what was saved
    print(f"[update_analyses] After commit, user.analyses keys: {list(user.analyses.keys()) if isinstance(user.analyses, dict) else 'not a dict'}")
    if isinstance(user.analyses, dict) and "last_report" in user.analyses:
        saved_last_report = user.analyses["last_report"]
        if isinstance(saved_last_report, dict) and "text" in saved_last_report:
            saved_text_length = len(saved_last_report["text"]) if isinstance(saved_last_report["text"], str) else 0
            print(f"[update_analyses] Saved last_report.text length: {saved_text_length}")
            print(f"[update_analyses] Saved last_report.text first 200 chars: {saved_last_report['text'][:200] if isinstance(saved_last_report['text'], str) else 'not a string'}")
    
    return user


def update_recommendations(db: Session, tgid: str, recommendations: Dict[str, Any]) -> HealthApp:
    """Update recommendations"""
    user = get_or_create_user(db, tgid)
    user.recommendations = recommendations
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user


def update_opros_anemia(db: Session, tgid: str, opros_data: Dict[str, Any]) -> HealthApp:
    """Update opros_anemia (iron deficiency questionnaire)"""
    print(f"[update_opros_anemia] Starting update for tgid: {tgid}")
    print(f"[update_opros_anemia] Received opros data: {opros_data}")
    
    user = get_or_create_user(db, tgid)
    
    # Get current opros_anemia and create a copy
    current_opros = user.opros_anemia or {}
    if not isinstance(current_opros, dict):
        current_opros = {}
        print(f"[update_opros_anemia] Warning: opros_anemia was not a dict, resetting to empty dict")
    
    # Create a new dict by copying current and updating with new data
    updated_opros = copy.deepcopy(current_opros)
    updated_opros.update(opros_data)
    
    # Add timestamp
    updated_opros['updated_at'] = datetime.utcnow().isoformat()
    
    # Create a completely new dict object to ensure SQLAlchemy detects the change
    new_opros = dict(updated_opros)
    user.opros_anemia = new_opros
    user.updated_at = datetime.utcnow()
    
    # Explicitly mark the JSONB column as modified
    flag_modified(user, "opros_anemia")
    
    db.flush()
    print(f"[update_opros_anemia] After flush, user.opros_anemia keys: {list(user.opros_anemia.keys()) if isinstance(user.opros_anemia, dict) else 'not a dict'}")
    
    db.commit()
    db.refresh(user)
    
    print(f"[update_opros_anemia] After commit, user.opros_anemia keys: {list(user.opros_anemia.keys()) if isinstance(user.opros_anemia, dict) else 'not a dict'}")
    
    return user


def get_rekom_for_analysis(db: Session, tgid: str, analysis_id: str) -> Dict[str, Any]:
    """Get recommendation for specific analysis from rekom column or base.txt"""
    user = get_or_create_user(db, tgid)
    
    # Check if recommendation exists in rekom column
    rekom_data = user.rekom or {}
    if isinstance(rekom_data, dict) and analysis_id in rekom_data:
        return {
            "analysis_id": analysis_id,
            "recommendation": rekom_data[analysis_id]
        }
    
    # If not found, load from base.txt
    try:
        # Try multiple possible paths for base.txt
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "base.txt"),  # Root of project
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "base.txt"),  # Alternative relative path
            "base.txt",  # Current directory
        ]
        
        base_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                base_path = abs_path
                break
        
        if base_path and os.path.exists(base_path):
            with open(base_path, 'r', encoding='utf-8') as f:
                base_content = f.read()
            
            # Save to rekom column for future use
            if not isinstance(rekom_data, dict):
                rekom_data = {}
            rekom_data[analysis_id] = base_content
            user.rekom = rekom_data
            flag_modified(user, "rekom")
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            return {
                "analysis_id": analysis_id,
                "recommendation": base_content
            }
    except Exception as e:
        print(f"Error loading base.txt: {e}")
    
    # Return empty if nothing found
    return {
        "analysis_id": analysis_id,
        "recommendation": ""
    }


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

