import json
from urllib.parse import parse_qs
from typing import Dict, Optional


class TelegramUser:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.username = data.get("username")
        self.language_code = data.get("language_code")
        self.is_premium = data.get("is_premium")
        self.photo_url = data.get("photo_url")
    
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "language_code": self.language_code,
            "is_premium": self.is_premium,
            "photo_url": self.photo_url,
        }


def parse_init_data(init_data: str) -> Dict:
    """
    Parse Telegram WebApp initData string into object
    Extracts user field and parses it as JSON
    """
    params = parse_qs(init_data, keep_blank_values=True)
    result = {}
    
    # Parse all parameters
    for key, value_list in params.items():
        result[key] = value_list[0] if value_list else None
    
    # Parse user field as JSON if present
    if "user" in result and result["user"]:
        try:
            user_data = json.loads(result["user"])
            result["parsed_user"] = TelegramUser(user_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing user field: {e}")
            result["parsed_user"] = None
    
    return result

