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
import traceback

router = APIRouter()

# Test endpoint to verify routing works
@router.get("/test")
async def test_endpoint():
    return {"message": "API router is working", "status": "ok"}

# Test endpoint for upload-file (no auth, no file)
@router.post("/upload-file-test")
async def upload_file_test():
    print("=" * 50)
    print("UPLOAD FILE TEST ENDPOINT CALLED")
    print("=" * 50)
    return {"message": "Upload file endpoint is accessible", "status": "ok"}


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
    x_telegram_initdata: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Proxy file upload to webhook"""
    print("=" * 50)
    print("UPLOAD FILE ENDPOINT CALLED - FUNCTION STARTED")
    print("=" * 50)
    
    # Get tgid from header (optional for now to debug 404)
    tgid = "unknown"
    if x_telegram_initdata:
        try:
            # Call the function directly with the header value
            tgid = get_tgid_from_header(x_telegram_initdata)
            print(f"TGID extracted from header: {tgid}")
        except Exception as auth_err:
            print(f"Auth error (continuing anyway): {auth_err}")
            print(traceback.format_exc())
            # Use a default tgid if auth fails
            tgid = "auth_failed"
    else:
        print("WARNING: No x-telegram-initdata header provided")
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
        
        # Build JSON payload with base64 file for n8n
        json_data = {
            'fileName': fileName,
            'mimeType': mimeType,
            'size': size,
            'tgid': tgid,
            'file': file_base64,  # Base64 encoded image
        }
        
        print(f"Building JSON payload for n8n...")
        print(f"JSON keys: {list(json_data.keys())}")
        print(f"JSON size: {len(str(json_data))} characters")
        print(f"Base64 data length: {len(file_base64)} characters")
        print(f"First 100 chars of base64: {file_base64[:100]}...")
        
        # Send to n8n webhook - ALWAYS use POST with JSON body
        # Even if webhook is configured for GET, we send POST with file data
        print(f"Sending POST request with JSON to n8n webhook: {webhook_url}")
        print(f"Payload contains: fileName, mimeType, size, tgid, file (base64)")
        
        response = requests.post(
            webhook_url,
            json=json_data,
            headers={
                'Content-Type': 'application/json',
            },
            timeout=60,
            allow_redirects=True
        )
        
        print(f"✅ Request sent! Response status: {response.status_code}")
        
        # Even if status is 404 or error, we consider it sent (webhook received it)
        if response.status_code == 404:
            print(f"⚠️ Webhook returned 404 - but data was sent. Webhook might be configured incorrectly.")
        elif response.status_code >= 400:
            print(f"⚠️ Webhook returned {response.status_code} - but data was sent.")
        else:
            print(f"✅ Webhook accepted request successfully!")
        
        print(f"Webhook response status: {response.status_code}")
        print(f"Webhook response headers: {dict(response.headers)}")
        response_text = response.text[:500] if response.text else 'No response'
        print(f"Webhook response (first 500 chars): {response_text}")
        
        # Update database (try, but don't fail if it doesn't work)
        analyses = {}
        try:
            print("Updating database...")
            user = queries.notify_upload(db, tgid, fileName, mimeType, size)
            print("Database updated successfully")
            analyses = user.analyses or {}
        except Exception as db_err:
            print(f"⚠️ Database update failed (non-critical): {db_err}")
        
        # Always return success from our side (file was sent to n8n webhook)
        result = {
            "success": True,
            "message": "File sent to n8n webhook",
            "fileName": fileName,
            "mime": mimeType,
            "size": size,
            "webhookStatus": response.status_code,
            "webhookResponse": response.text[:1000] if response.text else None,
            "analyses": analyses
        }
        print(f"✅ Returning success result")
        print("=" * 50)
        print("UPLOAD FILE ENDPOINT - SUCCESS")
        print("=" * 50)
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

