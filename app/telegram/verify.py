import hmac
import hashlib
from urllib.parse import parse_qs, urlencode
from typing import Dict


def verify_init_data(init_data: str, bot_token: str) -> bool:
    """
    Verify Telegram WebApp initData signature using HMAC-SHA256
    
    Algorithm:
    1. secret = HMAC_SHA256(key="WebAppData", data=BOT_TOKEN)
    2. data_check_string = sorted k=v pairs through \n (excluding hash)
    3. Compare hex with hash
    """
    try:
        # Parse init_data string
        params = parse_qs(init_data, keep_blank_values=True)
        
        # Get hash
        hash_value = params.get("hash", [None])[0]
        if not hash_value:
            return False
        
        # Remove hash from params
        params.pop("hash", None)
        
        # Create secret: HMAC_SHA256(key="WebAppData", data=BOT_TOKEN)
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Build data_check_string: sort k=v pairs and join with \n
        data_check_items = []
        for key in sorted(params.keys()):
            value = params[key][0] if params[key] else ""
            data_check_items.append(f"{key}={value}")
        
        data_check_string = "\n".join(data_check_items)
        
        # Calculate HMAC of data_check_string with secret
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes (case-insensitive)
        return calculated_hash.lower() == hash_value.lower()
        
    except Exception as e:
        print(f"Error verifying initData: {e}")
        return False

