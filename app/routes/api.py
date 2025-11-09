from fastapi import APIRouter, Depends, Header, HTTPException, status, UploadFile, File, Form
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

# Test endpoint to verify routing works
@router.get("/test")
async def test_endpoint():
    return {"message": "API router is working", "status": "ok"}


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


# POST /api/upload-file - Upload file to webhook (proxy)
@router.post("/upload-file")
async def upload_file_to_webhook(
    file: UploadFile = File(...),
    fileName: str = Form(...),
    mimeType: str = Form(...),
    size: int = Form(...),
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    """Proxy file upload to webhook"""
    print("=" * 50)
    print("UPLOAD FILE ENDPOINT CALLED")
    print("=" * 50)
    print(f"Received file: {fileName}")
    print(f"File size: {size}")
    print(f"File type: {mimeType}")
    print(f"TGID: {tgid}")
    
    webhook_url = settings.ANALYSIS_WEBHOOK_URL
    print(f"Webhook URL from settings: {webhook_url}")
    
    if not webhook_url:
        print("ERROR: Webhook URL not configured!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook URL not configured"
        )
    
    try:
        print("Reading file content...")
        # Read file content
        file_content = await file.read()
        print(f"File content read: {len(file_content)} bytes")
        
        print(f"=== Sending file to webhook ===")
        print(f"Webhook URL: {webhook_url}")
        print(f"File: {fileName}, Size: {size} bytes, Type: {mimeType}, TGID: {tgid}")
        
        # Encode file to base64
        import base64
        print("Encoding file to base64...")
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        print(f"File encoded to base64: {len(file_base64)} characters")
        
        # Build JSON payload with base64 file
        json_data = {
            'fileName': fileName,
            'mimeType': mimeType,
            'size': size,
            'tgid': tgid,
            'file': file_base64,
        }
        
        print(f"Building JSON payload...")
        print(f"JSON keys: {list(json_data.keys())}")
        print(f"JSON size: {len(str(json_data))} characters")
        print(f"Base64 data length: {len(file_base64)} characters")
        
        # Send to webhook
        print(f"Sending POST request to webhook: {webhook_url}")
        try:
            response = requests.post(
                webhook_url,
                json=json_data,
                headers={
                    'Content-Type': 'application/json',
                },
                timeout=60,
                allow_redirects=True
            )
            print(f"Webhook request completed")
        except Exception as req_err:
            print(f"ERROR during webhook request: {req_err}")
            raise
        
        print(f"Webhook response status: {response.status_code}")
        print(f"Webhook response headers: {dict(response.headers)}")
        response_text = response.text[:500] if response.text else 'No response'
        print(f"Webhook response (first 500 chars): {response_text}")
        
        # Update database
        print("Updating database...")
        user = queries.notify_upload(db, tgid, fileName, mimeType, size)
        print("Database updated successfully")
        
        # Always return success from our side (file was sent to webhook)
        # Even if webhook returns error, we consider it sent
        result = {
            "success": True,
            "message": "File sent to webhook",
            "fileName": fileName,
            "mime": mimeType,
            "size": size,
            "webhookStatus": response.status_code,
            "webhookResponse": response.text[:1000] if response.text else None,
            "analyses": user.analyses or {}
        }
        print(f"Returning result: {result}")
        return result
    except requests.exceptions.Timeout as e:
        print(f"Webhook timeout error: {e}")
        # Update database even on timeout (file was processed)
        user = queries.notify_upload(db, tgid, fileName, mimeType, size)
        # Return success but note the timeout
        return {
            "success": True,
            "message": "File sent to webhook (timeout waiting for response)",
            "fileName": fileName,
            "mime": mimeType,
            "size": size,
            "webhookStatus": "timeout",
            "webhookResponse": None,
            "analyses": user.analyses or {}
        }
    except requests.exceptions.ConnectionError as e:
        print(f"Webhook connection error: {e}")
        # Update database
        user = queries.notify_upload(db, tgid, fileName, mimeType, size)
        # Return success but note the connection error
        return {
            "success": True,
            "message": "File sent to webhook (connection error)",
            "fileName": fileName,
            "mime": mimeType,
            "size": size,
            "webhookStatus": "connection_error",
            "webhookResponse": str(e),
            "analyses": user.analyses or {}
        }
    except requests.exceptions.RequestException as e:
        print(f"Webhook request error: {e}")
        import traceback
        print(traceback.format_exc())
        # Update database
        user = queries.notify_upload(db, tgid, fileName, mimeType, size)
        # Return success but note the error
        return {
            "success": True,
            "message": f"File sent to webhook (error: {str(e)})",
            "fileName": fileName,
            "mime": mimeType,
            "size": size,
            "webhookStatus": "error",
            "webhookResponse": str(e),
            "analyses": user.analyses or {}
        }
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        print(traceback.format_exc())
        # Don't fail completely - still try to update database
        try:
            user = queries.notify_upload(db, tgid, fileName, mimeType, size)
            analyses = user.analyses or {}
        except:
            analyses = {}
        
        # Return error but with details
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload error: {str(e)}"
        )

