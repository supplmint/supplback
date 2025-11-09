from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel
import requests
import os

from app.database import get_db
from app.db import queries
from app.middleware.auth import get_tgid_from_header
from app.config import settings

router = APIRouter()


# Request models
class UpdateProfileRequest(BaseModel):
    profile: Dict[str, Any]


class UpdateAnalysesRequest(BaseModel):
    analyses: Dict[str, Any]


class UpdateRecommendationsRequest(BaseModel):
    recommendations: Dict[str, Any]


class NotifyUploadRequest(BaseModel):
    fileName: str
    mime: str
    size: int


# GET /api/me - Get or create user
@router.get("/me")
async def get_me(
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    user = queries.get_or_create_user(db, tgid)
    return {
        "tgid": user.tgid,
        "profile": user.profile or {}
    }


# POST /api/me - Update profile
@router.post("/me")
async def update_profile(
    request: UpdateProfileRequest,
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    user = queries.update_profile(db, tgid, request.profile)
    return {
        "tgid": user.tgid,
        "profile": user.profile or {}
    }


# POST /api/analyses/summary - Update analyses
@router.post("/analyses/summary")
async def update_analyses(
    request: UpdateAnalysesRequest,
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    user = queries.update_analyses(db, tgid, request.analyses)
    return {
        "analyses": user.analyses or {}
    }


# POST /api/reco/basic - Update recommendations
@router.post("/reco/basic")
async def update_recommendations(
    request: UpdateRecommendationsRequest,
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    user = queries.update_recommendations(db, tgid, request.recommendations)
    return {
        "recommendations": user.recommendations or {}
    }


# POST /api/notify-upload - Notify about file upload
@router.post("/notify-upload")
async def notify_upload(
    request: NotifyUploadRequest,
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    user = queries.notify_upload(db, tgid, request.fileName, request.mime, request.size)
    
    # Send file info to webhook
    webhook_url = settings.ANALYSIS_WEBHOOK_URL
    if webhook_url:
        try:
            webhook_payload = {
                "tgid": tgid,
                "fileName": request.fileName,
                "mime": request.mime,
                "size": request.size,
                "uploadedAt": user.updated_at.isoformat() if user.updated_at else None,
            }
            # Send to webhook asynchronously (don't block response)
            requests.post(
                webhook_url,
                json=webhook_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Webhook error: {e}")
    
    return {
        "fileName": request.fileName,
        "mime": request.mime,
        "size": request.size,
        "analyses": user.analyses or {}
    }

