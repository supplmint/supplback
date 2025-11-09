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
        # PRIORITY: JSON first (webhook seems to accept JSON based on response)
        response = None
        last_error = None
        successful_method = None
        
        import base64
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        print(f"=== File Encoding Info ===")
        print(f"Original file size: {size} bytes")
        print(f"Base64 encoded size: {len(file_base64)} bytes")
        print(f"Size increase: {len(file_base64) / size:.2f}x")
        
        # Method 1: JSON with base64 file (PRIORITY - webhook accepts JSON)
        try:
            print("Trying method 1: JSON with base64 file...")
            # Build JSON payload with file data
            json_data = {
                'fileName': fileName,
                'mimeType': mimeType,
                'size': size,
                'tgid': tgid,
                'file': file_base64,  # Main field for file data
            }
            
            # Log what we're sending (truncate base64 for logging)
            print(f"JSON payload keys: {list(json_data.keys())}")
            print(f"JSON payload size: ~{len(str(json_data))} characters")
            print(f"File data length (base64): {len(file_base64)} characters")
            print(f"First 100 chars of base64: {file_base64[:100]}...")
            
            response = requests.post(
                webhook_url,
                json=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'suppl-backend/1.0',
                },
                timeout=45,
                allow_redirects=True
            )
            
            print(f"Method 1 (JSON) response: {response.status_code}")
            print(f"Method 1 response headers: {dict(response.headers)}")
            response_text = response.text[:500] if response.text else 'No response'
            print(f"Method 1 response preview: {response_text}")
            
            # Log request details for debugging
            print(f"Request URL: {webhook_url}")
            print(f"Request method: POST")
            print(f"Request content-type: application/json")
            
            if response.status_code < 500:  # Accept any response except server errors
                successful_method = "Method 1 (JSON with base64)"
                print(f"✅ Using {successful_method}")
                # Check if file data is in response (meaning it was received)
                if fileName.lower() in response.text.lower() or response.status_code in [200, 201, 202]:
                    print(f"✅ File appears to be received by webhook")
                else:
                    print(f"⚠️ Warning: Response doesn't confirm file receipt")
        except Exception as e1:
            last_error = e1
            print(f"Method 1 failed: {e1}")
            import traceback
            print(traceback.format_exc())
        
        # Only try other methods if JSON failed or returned 500 error
        # But if JSON returned 200-499, we consider it successful (even if it's not ideal)
        if response is None or (response.status_code >= 500 and last_error is not None):
            # Method 2: Multipart form-data with 'file' field
            try:
                print("Trying method 2: multipart/form-data with 'file' field...")
                files = {
                    'file': (fileName, file_content, mimeType),
                    'upload': (fileName, file_content, mimeType),  # Alternative field name
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
                print(f"Method 2 (multipart) response: {response.status_code}")
                if response.status_code < 500:
                    successful_method = "Method 2 (multipart with fields)"
                    print(f"✅ Using {successful_method}")
            except Exception as e2:
                last_error = e2
                print(f"Method 2 failed: {e2}")
                
                # Method 3: Only file in multipart
                try:
                    print("Trying method 3: multipart file only...")
                    files = {
                        'file': (fileName, file_content, mimeType)
                    }
                    response = requests.post(
                        webhook_url,
                        files=files,
                        timeout=45,
                        allow_redirects=True
                    )
                    print(f"Method 3 (multipart file only) response: {response.status_code}")
                    if response.status_code < 500:
                        successful_method = "Method 3 (multipart file only)"
                        print(f"✅ Using {successful_method}")
                except Exception as e3:
                    last_error = e3
                    print(f"Method 3 failed: {e3}")
        
        if response is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"All methods failed. Last error: {str(last_error)}. Webhook URL might be incorrect or endpoint doesn't exist."
            )
        
        print(f"=== Webhook Response ===")
        print(f"Successful method: {successful_method}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        response_preview = response.text[:500] if response.text else "No response body"
        print(f"Response text (first 500 chars): {response_preview}")
        
        # Check if file was actually received by webhook
        # If response body contains file metadata or confirms receipt, it's good
        response_lower = response_preview.lower()
        file_received = (
            fileName.lower() in response_lower or
            'file' in response_lower or
            'received' in response_lower or
            'success' in response_lower or
            response.status_code in [200, 201, 202]
        )
        
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
        
        # Warn if file doesn't seem to be received
        if not file_received and response.status_code >= 200 and response.status_code < 300:
            print(f"⚠️ WARNING: Response doesn't indicate file was received. Response: {response_preview}")
        
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
            "fileReceived": file_received,
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

