from utils import PasswordHasher, TokenManager, InputValidator, JSONResponse
from database import Database
from datetime import datetime

class AuthSystem:
    def __init__(self):
        self.db = Database()
        self.validator = InputValidator()
    
    def register(self, username, email, password, role='user'):
        # Validation des entrées
        valid, message = self.validator.validate_username(username)
        if not valid:
            return JSONResponse.error(message)
        
        valid, message = self.validator.validate_email(email)
        if not valid:
            return JSONResponse.error(message)
        
        valid, message = self.validator.validate_password(password)
        if not valid:
            return JSONResponse.error(message)
        
        # Hash du mot de passe
        password_hash = PasswordHasher.hash_password(password)
        
        try:
            user_id = self.db.create_user(username, email, password_hash, role)
            return JSONResponse.success({
                "user_id": user_id,
                "username": username,
                "role": role
            }, "User registered successfully")
        except ValueError as e:
            return JSONResponse.error(str(e))
    
    def login(self, username, password):
        user = self.db.get_user_by_username(username)
        
        if not user:
            return JSONResponse.error("Invalid username or password", 401)
        
        if not user['is_active']:
            return JSONResponse.error("Account is disabled", 403)
        
        if not PasswordHasher.verify_password(password, user['password_hash']):
            return JSONResponse.error("Invalid username or password", 401)
        
        # Générer un token
        token = TokenManager.generate_token()
        expires_at = TokenManager.get_expiration_time()
        
        # Sauvegarder la session
        self.db.save_session(user['id'], token, expires_at)
        
        return JSONResponse.success({
            "token": token,
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role']
            },
            "expires_at": expires_at.isoformat()
        }, "Login successful")
    
    def logout(self, token):
        self.db.delete_session(token)
        return JSONResponse.success(message="Logged out successfully")
    
    def verify_token(self, token):
        session = self.db.get_session(token)
        
        if not session:
            return None
        
        return {
            "user_id": session['user_id'],
            "username": session['username'],
            "role": session['role'],
            "expires_at": session['expires_at']
        }
    
    def get_all_users(self, current_user_role):
        if current_user_role != 'admin':
            return JSONResponse.error("Unauthorized", 403)
        
        users = self.db.get_all_users()
        return JSONResponse.success(users)
    
    def update_user_role(self, user_id, new_role, current_user_role):
        if current_user_role != 'admin':
            return JSONResponse.error("Unauthorized", 403)
        
        if new_role not in ['user', 'admin']:
            return JSONResponse.error("Invalid role")
        
        success = self.db.update_user_role(user_id, new_role)
        if success:
            return JSONResponse.success(message="User role updated successfully")
        return JSONResponse.error("User not found")