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
    webhook_url = settings.ANALYSIS_WEBHOOK_URL
    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook URL not configured"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        print(f"=== Webhook Upload Debug ===")
        print(f"Webhook URL: {webhook_url}")
        print(f"File: {fileName}, Size: {size}, Type: {mimeType}, TGID: {tgid}")
        print(f"File content length: {len(file_content)} bytes")
        
        # First, check if webhook endpoint exists (GET request)
        try:
            print("Checking webhook endpoint availability...")
            check_response = requests.get(webhook_url, timeout=5, allow_redirects=True)
            print(f"GET request status: {check_response.status_code}")
            print(f"GET response: {check_response.text[:200]}")
        except Exception as check_err:
            print(f"GET request failed (this is OK for POST-only endpoints): {check_err}")
        
        # Try different methods to send to webhook
        response = None
        last_error = None
        successful_method = None
        
        # Method 1: Multipart form-data with 'file' field
        try:
            print("Trying method 1: multipart/form-data with 'file' field...")
            files = {
                'file': (fileName, file_content, mimeType)
            }
            data = {
                'fileName': fileName,
                'mimeType': mimeType,
                'size': str(size),
                'tgid': tgid,
            }
            response = requests.post(
                webhook_url,
                files=files,
                data=data,
                timeout=45,
                allow_redirects=True
            )
            print(f"Method 1 response: {response.status_code}")
            if response.status_code != 404:
                successful_method = "Method 1 (multipart with fields)"
                print(f"✅ Success with {successful_method}")
            else:
                raise Exception(f"404 Not Found with method 1")
        except Exception as e1:
            last_error = e1
            print(f"Method 1 failed: {e1}")
            
            # Method 2: Only file, no extra fields
            try:
                print("Trying method 2: only file, no extra fields...")
                files = {
                    'file': (fileName, file_content, mimeType)
                }
                response = requests.post(
                    webhook_url,
                    files=files,
                    timeout=45,
                    allow_redirects=True
                )
                print(f"Method 2 response: {response.status_code}")
                if response.status_code != 404:
                    successful_method = "Method 2 (multipart file only)"
                    print(f"✅ Success with {successful_method}")
                else:
                    raise Exception(f"404 Not Found with method 2")
            except Exception as e2:
                last_error = e2
                print(f"Method 2 failed: {e2}")
                
                # Method 3: JSON with base64 encoded file
                try:
                    print("Trying method 3: JSON with base64 file...")
                    import base64
                    file_base64 = base64.b64encode(file_content).decode('utf-8')
                    json_data = {
                        'fileName': fileName,
                        'mimeType': mimeType,
                        'size': size,
                        'tgid': tgid,
                        'file': file_base64,
                    }
                    response = requests.post(
                        webhook_url,
                        json=json_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=45,
                        allow_redirects=True
                    )
                    print(f"Method 3 response: {response.status_code}")
                    if response.status_code != 404:
                        successful_method = "Method 3 (JSON with base64)"
                        print(f"✅ Success with {successful_method}")
                    else:
                        raise Exception(f"404 Not Found with method 3")
                except Exception as e3:
                    last_error = e3
                    print(f"Method 3 failed: {e3}")
                    
                    # Method 4: Raw file data
                    try:
                        print("Trying method 4: raw file data...")
                        response = requests.post(
                            webhook_url,
                            data=file_content,
                            headers={
                                'Content-Type': mimeType,
                                'Content-Disposition': f'attachment; filename="{fileName}"',
                                'X-File-Name': fileName,
                                'X-File-Size': str(size),
                                'X-TGID': tgid,
                            },
                            timeout=45,
                            allow_redirects=True
                        )
                        print(f"Method 4 response: {response.status_code}")
                        if response.status_code != 404:
                            successful_method = "Method 4 (raw file data)"
                            print(f"✅ Success with {successful_method}")
                    except Exception as e4:
                        last_error = e4
                        print(f"Method 4 failed: {e4}")
        
        if response is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"All methods failed. Last error: {str(last_error)}. Webhook URL might be incorrect or endpoint doesn't exist."
            )
        
        print(f"=== Webhook Response ===")
        print(f"Successful method: {successful_method}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response text (first 500 chars): {response.text[:500]}")
        
        # If 404, it means endpoint doesn't exist
        if response.status_code == 404:
            error_msg = (
                f"Webhook returned 404 Not Found. "
                f"This means the endpoint '{webhook_url}' doesn't exist on the server. "
                f"Please check:\n"
                f"1. Is the webhook URL correct?\n"
                f"2. Does the endpoint exist on the server?\n"
                f"3. Is the server running and accessible?"
            )
            print(f"❌ {error_msg}")
            # Still update database for tracking
            user = queries.notify_upload(db, tgid, fileName, mimeType, size)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        
        # Update database
        user = queries.notify_upload(db, tgid, fileName, mimeType, size)
        
        # Return response
        return {
            "success": response.status_code < 400,  # Consider 2xx and 3xx as success
            "fileName": fileName,
            "mime": mimeType,
            "size": size,
            "webhookStatus": response.status_code,
            "webhookResponse": response.text[:1000] if response.text else None,
            "webhookHeaders": dict(response.headers),
            "method": successful_method,
            "analyses": user.analyses or {}
        }
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Webhook timeout"
        )
    except requests.exceptions.RequestException as e:
        print(f"Webhook request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Webhook error: {str(e)}"
        )
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload error: {str(e)}"
        )

