from fastapi import Header, HTTPException, status
from typing import Optional
from app.telegram.verify import verify_init_data
from app.telegram.parse import parse_init_data
from app.config import settings


def get_tgid_from_header(x_telegram_initdata: Optional[str] = Header(None)) -> str:
    """Extract and verify Telegram user ID from initData header"""
    if not x_telegram_initdata:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-telegram-initdata header"
        )
    
    # Verify signature
    if not verify_init_data(x_telegram_initdata, settings.BOT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData signature"
        )
    
    # Parse initData and extract user ID
    parsed = parse_init_data(x_telegram_initdata)
    
    if not parsed.get("parsed_user") or not parsed["parsed_user"].id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user data in initData"
        )
    
    return str(parsed["parsed_user"].id)

