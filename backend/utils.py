import json
import bcrypt
from datetime import datetime, timedelta
import secrets
import re

class JSONResponse:
    @staticmethod
    def success(data=None, message="Success"):
        return json.dumps({
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    def error(message="Error", status_code=400):
        return json.dumps({
            "success": False,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        })

class PasswordHasher:
    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    @staticmethod
    def verify_password(password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode())

class TokenManager:
    @staticmethod
    def generate_token(length=64):
        return secrets.token_hex(length)
    
    @staticmethod
    def get_expiration_time(hours=24):
        return datetime.now() + timedelta(hours=hours)

class InputValidator:
    @staticmethod
    def validate_username(username):
        if len(username) < 3 or len(username) > 20:
            return False, "Username must be between 3 and 20 characters"
        if not re.match("^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers and underscores"
        return True, ""
    
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, ""
    
    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one number"
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(char.islower() for char in password):
            return False, "Password must contain at least one lowercase letter"
        return True, ""