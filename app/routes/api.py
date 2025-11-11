from fastapi import APIRouter, Depends, Header, HTTPException, status, UploadFile, File, Form, Request

from sqlalchemy.orm import Session

from typing import Dict, Any, Optional

from pydantic import BaseModel

from datetime import datetime

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




class GetRecommendationRequest(BaseModel):
    analysis_id: str


class GetRecommendationByTextRequest(BaseModel):
    analysis_text: str
    analysis_id: Optional[str] = None


class RecommendationResultRequest(BaseModel):
    tgid: str
    analysis_id: str
    recommendation: str



# GET /api/analyses/history - Get all analyses history from allanalize column

@router.get("/analyses/history")

async def get_analyses_history(

    tgid: str = Depends(get_tgid_from_header),

    db: Session = Depends(get_db)

):

    """Get all analyses history from allanalize column"""

    user = queries.get_or_create_user(db, tgid)

    all_analyses = user.allanalize or {}

    
    
    # Return as list if it's a list, or wrap in object if it's a dict

    if isinstance(all_analyses, list):

        return {"analyses": all_analyses}

    elif isinstance(all_analyses, dict):

        # If it's a dict, try to extract list from common keys

        if "analyses" in all_analyses:

            return {"analyses": all_analyses["analyses"]}

        elif "history" in all_analyses:

            return {"analyses": all_analyses["history"]}

        else:

            # Convert dict to list of items

            return {"analyses": [all_analyses] if all_analyses else []}

    else:

        return {"analyses": []}





# GET /api/me - Get or create user

@router.get("/me")

async def get_me(

    tgid: str = Depends(get_tgid_from_header),

    db: Session = Depends(get_db)

):

    user = queries.get_or_create_user(db, tgid)

    
    
    # Явно обновляем данные из базы перед возвратом

    db.refresh(user)

    
    
    # Логирование для отладки

    print(f"[get_me] User {tgid} - analyses type: {type(user.analyses)}")

    print(f"[get_me] User {tgid} - analyses value: {user.analyses}")

    if user.analyses:

        print(f"[get_me] User {tgid} - analyses keys: {list(user.analyses.keys()) if isinstance(user.analyses, dict) else 'not a dict'}")

        if isinstance(user.analyses, dict) and "last_report" in user.analyses:

            print(f"[get_me] User {tgid} - last_report: {user.analyses['last_report']}")

            if isinstance(user.analyses["last_report"], dict):

                print(f"[get_me] User {tgid} - last_report keys: {list(user.analyses['last_report'].keys())}")

                print(f"[get_me] User {tgid} - last_report.text exists: {'text' in user.analyses['last_report']}")

                if "text" in user.analyses["last_report"]:

                    text_value = user.analyses["last_report"]["text"]

                    print(f"[get_me] User {tgid} - last_report.text type: {type(text_value)}")

                    print(f"[get_me] User {tgid} - last_report.text length: {len(text_value) if isinstance(text_value, str) else 'not a string'}")
    
    

    # Убеждаемся, что возвращаем правильный формат

    analyses_data = user.analyses if user.analyses is not None else {}

    # Если analyses это не dict, пытаемся преобразовать

    if not isinstance(analyses_data, dict):

        print(f"[get_me] WARNING: analyses is not a dict, type: {type(analyses_data)}, value: {analyses_data}")

        analyses_data = {}
    
    

    return {

        "tgid": user.tgid,

        "profile": user.profile or {},

        "analyses": analyses_data

    }





# POST /api/me - Update profile

@router.post("/me")

async def update_profile(

    request: UpdateProfileRequest,

    tgid: str = Depends(get_tgid_from_header),

    db: Session = Depends(get_db)

):

    # Log incoming profile data

    print(f"=== UPDATE PROFILE REQUEST ===")

    print(f"TGID: {tgid}")

    print(f"Received profile data: {request.profile}")

    print(f"Profile data type: {type(request.profile)}")

    print(f"Profile keys: {list(request.profile.keys())}")

    for key, value in request.profile.items():

        print(f"  {key}: {value} (type: {type(value)})")
    
    

    # Update profile (this function already handles getting/creating user)

    user = queries.update_profile(db, tgid, request.profile)

    
    
    # Log updated profile

    print(f"Profile after update: {user.profile}")

    print(f"Profile type after update: {type(user.profile)}")

    print(f"Profile keys after update: {list(user.profile.keys()) if user.profile else 'None'}")

    if user.profile:

        for key, value in user.profile.items():

            print(f"  {key}: {value} (type: {type(value)})")

    print(f"===============================")

    
    
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




# POST /api/recommendations/get - Get recommendation by sending analysis text to webhook
@router.post("/recommendations/get")
async def get_recommendation(
    request: GetRecommendationByTextRequest,
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    """Get recommendation by sending analysis text to AI webhook"""
    webhook_url = settings.RECOMMENDATIONS_WEBHOOK_URL
    
    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Recommendations webhook URL not configured"
        )
    
    # Check if recommendation exists in rekom
    analysis_id = request.analysis_id or f"analysis_{tgid}_{int(datetime.utcnow().timestamp())}"
    user = queries.get_or_create_user(db, tgid)
    rekom_data = user.rekom or {}
    
    # Check if recommendation already exists in rekom
    if isinstance(rekom_data, dict) and analysis_id in rekom_data:
        return {
            "analysis_id": analysis_id,
            "recommendation": rekom_data[analysis_id],
            "cached": True
        }
    
    # Get user profile data
    profile = user.profile or {}
    
    # Send analysis text to webhook with profile data (webhook will send result back via HTTP Request)
    try:
        webhook_payload = {
            "tgid": tgid,
            "analysis_text": request.analysis_text,
            "analysis_id": analysis_id,
            "profile": {
                "height": profile.get("height"),
                "weight": profile.get("weight"),
                "gender": profile.get("gender"),
                "age": profile.get("age")
            }
        }
        
        print(f"Sending analysis text to recommendations webhook: {webhook_url}")
        print(f"Analysis text length: {len(request.analysis_text)} characters")
        print(f"Webhook will send result back via HTTP Request to /api/recommendations/result")
        
        # Send to webhook (don't wait for response - webhook will send result via HTTP Request)
        try:
            requests.post(
                webhook_url,
                json=webhook_payload,
                headers={"Content-Type": "application/json"},
                timeout=10  # Short timeout just to send the request
            )
        except Exception as e:
            print(f"Warning: Could not send to webhook: {e}")
            # Continue anyway - webhook might still process
        
        # Return status - recommendation will be saved in rekom by webhook
        return {
            "analysis_id": analysis_id,
            "status": "processing",
            "message": "Analysis sent to AI for processing. Please wait..."
        }
            
    except Exception as e:
        print(f"Error sending to webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending to webhook: {str(e)}"
        )


# POST /api/recommendations/result - Receive recommendation result from webhook (no auth required)
@router.post("/recommendations/result")
async def receive_recommendation_result(
    request: RecommendationResultRequest,
    db: Session = Depends(get_db)
):
    """Receive recommendation result from webhook and save to rekom column
    
    This endpoint is called by n8n webhook via HTTP Request to send back
    the AI-generated recommendation.
    
    Expected JSON body:
    {
        "tgid": "747737181",
        "analysis_id": "analysis_123",
        "recommendation": "текст рекомендации..."
    }
    """
    print(f"=== Receiving recommendation result from webhook ===")
    print(f"TGID: {request.tgid}")
    print(f"Analysis ID: {request.analysis_id}")
    print(f"Recommendation length: {len(request.recommendation)} characters")
    
    try:
        # Get or create user
        user = queries.get_or_create_user(db, request.tgid)
        rekom_data = user.rekom or {}
        
        # Save recommendation to rekom column
        if not isinstance(rekom_data, dict):
            rekom_data = {}
        rekom_data[request.analysis_id] = request.recommendation
        user.rekom = rekom_data
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "rekom")
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        print(f"✅ Recommendation saved to rekom for user {request.tgid}")
        print(f"Analysis ID: {request.analysis_id}")
        
        return {
            "success": True,
            "message": "Recommendation saved to rekom",
            "tgid": request.tgid,
            "analysis_id": request.analysis_id,
            "recommendation_length": len(request.recommendation)
        }
    except Exception as e:
        print(f"❌ Error saving recommendation: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving recommendation: {str(e)}"
        )


# GET /api/recommendations/{analysis_id} - Get recommendation from rekom by analysis_id
@router.get("/recommendations/{analysis_id}")
async def get_recommendation_by_id(
    analysis_id: str,
    tgid: str = Depends(get_tgid_from_header),
    db: Session = Depends(get_db)
):
    """Get recommendation from rekom by analysis_id"""
    user = queries.get_or_create_user(db, tgid)
    rekom_data = user.rekom or {}
    
    if isinstance(rekom_data, dict) and analysis_id in rekom_data:
        return {
            "analysis_id": analysis_id,
            "recommendation": rekom_data[analysis_id],
            "status": "ready"
        }
    
    return {
        "analysis_id": analysis_id,
        "status": "processing",
        "message": "Recommendation is being processed"
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





# Request model for analysis result (JSON)

class AnalysisResultRequest(BaseModel):

    tgid: str

    report: str

    fileName: Optional[str] = None

    clientTime: Optional[str] = None  # Client's local time (ISO format with timezone)





# POST /api/analyses/result - Receive analysis result from n8n (no auth required)

# Accepts both JSON and Form-Data for flexibility

@router.post("/analyses/result")

async def receive_analysis_result(

    raw_request: Request,

    request_data: Optional[AnalysisResultRequest] = None,

    tgid: Optional[str] = Form(None),

    report: Optional[str] = Form(None),

    fileName: Optional[str] = Form(None),

    clientTime: Optional[str] = Form(None),

    db: Session = Depends(get_db)

):

    """Receive analysis report from n8n and save to database

    
    
    Accepts both formats:

    1. JSON body: {"tgid": "...", "report": "...", "fileName": "..."}

    2. Form-Data: tgid, report, fileName as form fields

    3. Nested JSON: {"body": {"tgid": "...", "report": "..."}}

    
    
    n8n can send any of these formats.

    """

    print(f"=== Receiving analysis result from n8n ===")

    
    
    tgid_value = None

    report_value = None

    fileName_value = None

    client_time_value = None

    
    
    # Try to get data from JSON first (Pydantic model)

    if request_data:

        tgid_value = request_data.tgid

        report_value = request_data.report

        fileName_value = request_data.fileName

        client_time_value = request_data.clientTime

        print("Received as JSON (Pydantic model)")

    # Try Form-Data

    elif tgid and report:

        tgid_value = tgid

        report_value = report

        fileName_value = fileName

        client_time_value = clientTime  # Get from Form if available

        print("Received as Form-Data")

    # Try to parse raw request body (for nested JSON from n8n)

    else:

        try:

            content_type = raw_request.headers.get("content-type", "")

            if "application/json" in content_type:

                json_data = await raw_request.json()

                print(f"Raw JSON received: {list(json_data.keys()) if isinstance(json_data, dict) else 'not a dict'}")

                
                
                # Handle nested body structure from n8n: {"body": {"tgid": "...", "report": "..."}}

                if isinstance(json_data, dict):

                    if "body" in json_data and isinstance(json_data["body"], dict):

                        # n8n sometimes wraps data in "body"

                        json_data = json_data["body"]

                        print("Unwrapped nested 'body' structure")

                    tgid_value = json_data.get("tgid")

                    report_value = json_data.get("report")

                    fileName_value = json_data.get("fileName")

                    client_time_value = json_data.get("clientTime")

                    print("Received as nested JSON from raw request")

        except Exception as e:

            print(f"Error parsing raw request: {e}")

            print(traceback.format_exc())
    
    

    if not tgid_value or not report_value:

        raise HTTPException(

            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

            detail="Missing required fields: tgid and report. Send as JSON {\"tgid\": \"...\", \"report\": \"...\"} or Form-Data."

        )
    
    

    print(f"TGID: {tgid_value}")

    print(f"Report length: {len(report_value)} characters")

    print(f"FileName: {fileName_value}")

    print(f"First 200 chars of report: {report_value[:200]}...")

    
    
    try:

        # Get or create user

        user = queries.get_or_create_user(db, tgid_value)

        
        
        # Get existing reports only (ignore last_upload, upload_history - they are not part of analyses)

        current_analyses = user.analyses or {}

        reports = current_analyses.get("reports", [])

        
        
        # Use client's local time if provided, otherwise use UTC server time
        # client_time_value comes from the webhook (n8n should return it back)
        created_at = client_time_value if client_time_value else datetime.utcnow().isoformat()
        
        if client_time_value:
            print(f"Using client's local time: {client_time_value}")
        else:
            print(f"Using UTC server time (clientTime not provided): {created_at}")
        
        # Create new report

        new_report = {

            "text": report_value,

            "fileName": fileName_value or "unknown",

            "createdAt": created_at,

        }

        
        
        # Add to reports list

        reports.append(new_report)

        
        
        # Save ONLY report data in analyses (no last_upload, upload_history)

        # analyses should contain only what comes from HTTP Request (reports)

        user.analyses = {

            "reports": reports,

            "last_report": new_report  # Save last report for quick access

        }

        
        
        # Add to allanalize - история всех анализов

        # ВАЖНО: в allanalize сохраняем только отдельные отчеты, а не весь объект analyses

        current_allanalize = user.allanalize or {}

        all_analyses_list = []

        
        
        # Если allanalize - это список, используем его

        if isinstance(current_allanalize, list):

            all_analyses_list = current_allanalize.copy()

        # Если allanalize - это объект с ключом "analyses" или "history"

        elif isinstance(current_allanalize, dict):

            if "analyses" in current_allanalize and isinstance(current_allanalize["analyses"], list):

                all_analyses_list = current_allanalize["analyses"].copy()

            elif "history" in current_allanalize and isinstance(current_allanalize["history"], list):

                all_analyses_list = current_allanalize["history"].copy()

            else:

                # Если это просто объект, создаем новый список

                all_analyses_list = []
        
        

        # ВАЖНО: Добавляем только new_report (отдельный отчет), а не весь объект analyses

        # Проверяем, что не добавляем дубликаты

        # Если последний элемент уже такой же (по fileName и createdAt), не добавляем

        if all_analyses_list:

            last_item = all_analyses_list[-1]

            if isinstance(last_item, dict):

                # Если последний элемент - это весь объект analyses (старый формат), удаляем его

                if "reports" in last_item and "last_report" in last_item:

                    # Это старый формат - удаляем его

                    all_analyses_list.pop()

                # Если это уже такой же отчет, не добавляем дубликат

                elif last_item.get("fileName") == new_report["fileName"] and last_item.get("createdAt") == new_report["createdAt"]:

                    # Дубликат - не добавляем

                    pass

                else:

                    all_analyses_list.append(new_report)

            else:

                all_analyses_list.append(new_report)

        else:

            all_analyses_list.append(new_report)
        
        

        # Сохраняем обновленную историю в allanalize

        user.allanalize = all_analyses_list

        
        
        # Помечаем JSONB колонки как измененные

        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(user, "analyses")

        flag_modified(user, "allanalize")

        
        
        user.updated_at = datetime.utcnow()

        
        
        db.flush()

        db.commit()

        db.refresh(user)

        
        
        # Детальное логирование после сохранения

        print(f"✅ Report saved successfully for user {tgid_value}")

        print(f"Analyses now contains only reports (no upload data)")

        print(f"Reports count: {len(reports)}")

        print(f"Last report exists: True")

        print(f"✅ All analyses history saved to allanalize")

        print(f"All analyses count: {len(all_analyses_list)}")

        print(f"Allanalize type: {type(user.allanalize)}")

        
        
        # Проверяем, что данные правильно сохранились

        print(f"[DEBUG] After commit and refresh:")

        print(f"[DEBUG] user.analyses type: {type(user.analyses)}")

        print(f"[DEBUG] user.analyses value: {user.analyses}")

        if isinstance(user.analyses, dict):

            print(f"[DEBUG] user.analyses keys: {list(user.analyses.keys())}")

            if "last_report" in user.analyses:

                print(f"[DEBUG] user.analyses['last_report']: {user.analyses['last_report']}")

                if isinstance(user.analyses["last_report"], dict):

                    print(f"[DEBUG] user.analyses['last_report'] keys: {list(user.analyses['last_report'].keys())}")

                    if "text" in user.analyses["last_report"]:

                        text_val = user.analyses["last_report"]["text"]

                        print(f"[DEBUG] user.analyses['last_report']['text'] type: {type(text_val)}")

                        print(f"[DEBUG] user.analyses['last_report']['text'] length: {len(text_val) if isinstance(text_val, str) else 'not a string'}")

                        print(f"[DEBUG] user.analyses['last_report']['text'] first 200 chars: {text_val[:200] if isinstance(text_val, str) else 'not a string'}")

                    else:

                        print(f"[DEBUG] WARNING: 'text' key not found in last_report!")

                else:

                    print(f"[DEBUG] WARNING: last_report is not a dict, type: {type(user.analyses['last_report'])}")

            else:

                print(f"[DEBUG] WARNING: 'last_report' key not found in analyses!")

        else:

            print(f"[DEBUG] WARNING: user.analyses is not a dict, type: {type(user.analyses)}")
        
        

        return {

            "success": True,

            "message": "Report saved",

            "tgid": tgid_value,

            "reportLength": len(report_value),

            "analysesKeys": list(user.analyses.keys())

        }

    except Exception as e:

        print(f"❌ Error saving report: {e}")

        print(traceback.format_exc())

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error saving report: {str(e)}"

        )





# POST /api/upload-file - Upload file to webhook (proxy)

@router.post("/upload-file")

async def upload_file_to_webhook(

    file: UploadFile = File(...),

    fileName: str = Form(...),

    mimeType: str = Form(...),

    size: int = Form(...),

    clientTime: Optional[str] = Form(None),

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

    
    
    # Get user profile data from database

    profile_data = {}

    if tgid != "unknown" and tgid != "auth_failed":

        try:

            user = queries.get_or_create_user(db, tgid)

            profile_data = user.profile or {}

            print(f"Profile data loaded: {list(profile_data.keys()) if profile_data else 'empty'}")

        except Exception as profile_err:

            print(f"Warning: Could not load profile data: {profile_err}")

            profile_data = {}

    else:

        print("Skipping profile load - invalid tgid")
    
    

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

        
        
        # Build JSON payload with base64 file and profile data for n8n

        json_data = {

            'fileName': fileName,

            'mimeType': mimeType,

            'size': size,

            'tgid': tgid,

            'file': file_base64,  # Base64 encoded image

            'profile': profile_data,  # User profile data from database

            'clientTime': clientTime,  # Client's local time (ISO format with timezone)

        }

        
        
        print(f"Building JSON payload for n8n...")

        print(f"JSON keys: {list(json_data.keys())}")

        print(f"JSON size: {len(str(json_data))} characters")

        print(f"Base64 data length: {len(file_base64)} characters")

        print(f"Profile data keys: {list(profile_data.keys()) if profile_data else 'none'}")

        print(f"First 100 chars of base64: {file_base64[:100]}...")

        
        
        # Send to n8n webhook

        # IMPORTANT: n8n webhooks should be configured to accept POST, not GET

        # GET requests cannot send file data (URL length limit)

        print(f"Sending POST request with JSON to n8n webhook: {webhook_url}")

        print(f"Payload contains: fileName, mimeType, size, tgid, file (base64), profile")

        print(f"Total payload size: {len(str(json_data))} characters")

        
        
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

            
            
            print(f"✅ Request sent successfully! Response status: {response.status_code}")

            print(f"Webhook response headers: {dict(response.headers)}")

            response_text = response.text[:500] if response.text else 'No response'

            print(f"Webhook response (first 500 chars): {response_text}")

            
            
            # Log response status

            if response.status_code == 404:

                print(f"⚠️ WARNING: Webhook returned 404. Check n8n webhook settings - it should accept POST requests.")

            elif response.status_code >= 400:

                print(f"⚠️ WARNING: Webhook returned {response.status_code}. Check n8n webhook configuration.")

            else:

                print(f"✅ SUCCESS: Webhook accepted request (status {response.status_code})")
                
                

        except Exception as send_err:

            print(f"❌ ERROR sending to webhook: {send_err}")

            print(traceback.format_exc())

            # Don't fail - we tried to send

            response = type('obj', (object,), {'status_code': 0, 'text': str(send_err)})()
        
        

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




        current_allanalize = user.allanalize or {}

        all_analyses_list = []

        

        # Если allanalize - это список, используем его

        if isinstance(current_allanalize, list):

            all_analyses_list = current_allanalize.copy()

        # Если allanalize - это объект с ключом "analyses" или "history"

        elif isinstance(current_allanalize, dict):

            if "analyses" in current_allanalize and isinstance(current_allanalize["analyses"], list):

                all_analyses_list = current_allanalize["analyses"].copy()

            elif "history" in current_allanalize and isinstance(current_allanalize["history"], list):

                all_analyses_list = current_allanalize["history"].copy()

            else:

                # Если это просто объект, создаем новый список

                all_analyses_list = []

        

        # ВАЖНО: Добавляем только new_report (отдельный отчет), а не весь объект analyses

        # Проверяем, что не добавляем дубликаты

        # Если последний элемент уже такой же (по fileName и createdAt), не добавляем

        if all_analyses_list:

            last_item = all_analyses_list[-1]

            if isinstance(last_item, dict):

                # Если последний элемент - это весь объект analyses (старый формат), удаляем его

                if "reports" in last_item and "last_report" in last_item:

                    # Это старый формат - удаляем его

                    all_analyses_list.pop()

                # Если это уже такой же отчет, не добавляем дубликат

                elif last_item.get("fileName") == new_report["fileName"] and last_item.get("createdAt") == new_report["createdAt"]:

                    # Дубликат - не добавляем

                    pass

                else:

                    all_analyses_list.append(new_report)

            else:

                all_analyses_list.append(new_report)

        else:

            all_analyses_list.append(new_report)

        

        # Сохраняем обновленную историю в allanalize

        user.allanalize = all_analyses_list

        

        # Помечаем JSONB колонки как измененные

        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(user, "analyses")

        flag_modified(user, "allanalize")

        

        user.updated_at = datetime.utcnow()

        

        db.flush()

        db.commit()

        db.refresh(user)

        

        # Детальное логирование после сохранения

        print(f"✅ Report saved successfully for user {tgid_value}")

        print(f"Analyses now contains only reports (no upload data)")

        print(f"Reports count: {len(reports)}")

        print(f"Last report exists: True")

        print(f"✅ All analyses history saved to allanalize")

        print(f"All analyses count: {len(all_analyses_list)}")

        print(f"Allanalize type: {type(user.allanalize)}")

        

        # Проверяем, что данные правильно сохранились

        print(f"[DEBUG] After commit and refresh:")

        print(f"[DEBUG] user.analyses type: {type(user.analyses)}")

        print(f"[DEBUG] user.analyses value: {user.analyses}")

        if isinstance(user.analyses, dict):

            print(f"[DEBUG] user.analyses keys: {list(user.analyses.keys())}")

            if "last_report" in user.analyses:

                print(f"[DEBUG] user.analyses['last_report']: {user.analyses['last_report']}")

                if isinstance(user.analyses["last_report"], dict):

                    print(f"[DEBUG] user.analyses['last_report'] keys: {list(user.analyses['last_report'].keys())}")

                    if "text" in user.analyses["last_report"]:

                        text_val = user.analyses["last_report"]["text"]

                        print(f"[DEBUG] user.analyses['last_report']['text'] type: {type(text_val)}")

                        print(f"[DEBUG] user.analyses['last_report']['text'] length: {len(text_val) if isinstance(text_val, str) else 'not a string'}")

                        print(f"[DEBUG] user.analyses['last_report']['text'] first 200 chars: {text_val[:200] if isinstance(text_val, str) else 'not a string'}")

                    else:

                        print(f"[DEBUG] WARNING: 'text' key not found in last_report!")

                else:

                    print(f"[DEBUG] WARNING: last_report is not a dict, type: {type(user.analyses['last_report'])}")

            else:

                print(f"[DEBUG] WARNING: 'last_report' key not found in analyses!")

        else:

            print(f"[DEBUG] WARNING: user.analyses is not a dict, type: {type(user.analyses)}")

        

        return {

            "success": True,

            "message": "Report saved",

            "tgid": tgid_value,

            "reportLength": len(report_value),

            "analysesKeys": list(user.analyses.keys())

        }

    except Exception as e:

        print(f"❌ Error saving report: {e}")

        print(traceback.format_exc())

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=f"Error saving report: {str(e)}"

        )





# POST /api/upload-file - Upload file to webhook (proxy)

@router.post("/upload-file")

async def upload_file_to_webhook(

    file: UploadFile = File(...),

    fileName: str = Form(...),

    mimeType: str = Form(...),

    size: int = Form(...),

    clientTime: Optional[str] = Form(None),

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

    

    # Get user profile data from database

    profile_data = {}

    if tgid != "unknown" and tgid != "auth_failed":

        try:

            user = queries.get_or_create_user(db, tgid)

            profile_data = user.profile or {}

            print(f"Profile data loaded: {list(profile_data.keys()) if profile_data else 'empty'}")

        except Exception as profile_err:

            print(f"Warning: Could not load profile data: {profile_err}")

            profile_data = {}

    else:

        print("Skipping profile load - invalid tgid")

    

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

        

        # Build JSON payload with base64 file and profile data for n8n

        json_data = {

            'fileName': fileName,

            'mimeType': mimeType,

            'size': size,

            'tgid': tgid,

            'file': file_base64,  # Base64 encoded image

            'profile': profile_data,  # User profile data from database

            'clientTime': clientTime,  # Client's local time (ISO format with timezone)

        }

        

        print(f"Building JSON payload for n8n...")

        print(f"JSON keys: {list(json_data.keys())}")

        print(f"JSON size: {len(str(json_data))} characters")

        print(f"Base64 data length: {len(file_base64)} characters")

        print(f"Profile data keys: {list(profile_data.keys()) if profile_data else 'none'}")

        print(f"First 100 chars of base64: {file_base64[:100]}...")

        

        # Send to n8n webhook

        # IMPORTANT: n8n webhooks should be configured to accept POST, not GET

        # GET requests cannot send file data (URL length limit)

        print(f"Sending POST request with JSON to n8n webhook: {webhook_url}")

        print(f"Payload contains: fileName, mimeType, size, tgid, file (base64), profile")

        print(f"Total payload size: {len(str(json_data))} characters")

        

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

            

            print(f"✅ Request sent successfully! Response status: {response.status_code}")

            print(f"Webhook response headers: {dict(response.headers)}")

            response_text = response.text[:500] if response.text else 'No response'

            print(f"Webhook response (first 500 chars): {response_text}")

            

            # Log response status

            if response.status_code == 404:

                print(f"⚠️ WARNING: Webhook returned 404. Check n8n webhook settings - it should accept POST requests.")

            elif response.status_code >= 400:

                print(f"⚠️ WARNING: Webhook returned {response.status_code}. Check n8n webhook configuration.")

            else:

                print(f"✅ SUCCESS: Webhook accepted request (status {response.status_code})")

                

        except Exception as send_err:

            print(f"❌ ERROR sending to webhook: {send_err}")

            print(traceback.format_exc())

            # Don't fail - we tried to send

            response = type('obj', (object,), {'status_code': 0, 'text': str(send_err)})()

        

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




