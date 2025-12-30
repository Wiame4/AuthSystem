from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from auth import AuthSystem
from utils import JSONResponse
import re

class AuthRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.auth_system = AuthSystem()
        super().__init__(*args, **kwargs)
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/users':
            self._handle_get_users()
        elif parsed_path.path == '/api/verify':
            self._handle_verify_token()
        else:
            self._set_headers(404)
            self.wfile.write(JSONResponse.error("Endpoint not found", 404).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode())
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(JSONResponse.error("Invalid JSON", 400).encode())
            return
        
        if self.path == '/api/register':
            self._handle_register(data)
        elif self.path == '/api/login':
            self._handle_login(data)
        elif self.path == '/api/logout':
            self._handle_logout(data)
        elif self.path == '/api/users/update-role':
            self._handle_update_role(data)
        else:
            self._set_headers(404)
            self.wfile.write(JSONResponse.error("Endpoint not found", 404).encode())
    
    def _handle_register(self, data):
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        role = data.get('role', 'user')
        
        if not all([username, email, password]):
            self._set_headers(400)
            self.wfile.write(JSONResponse.error("Missing required fields", 400).encode())
            return
        
        response = self.auth_system.register(username, email, password, role)
        self._set_headers(200 if json.loads(response)['success'] else 400)
        self.wfile.write(response.encode())
    
    def _handle_login(self, data):
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not all([username, password]):
            self._set_headers(400)
            self.wfile.write(JSONResponse.error("Missing credentials", 400).encode())
            return
        
        response = self.auth_system.login(username, password)
        self._set_headers(200 if json.loads(response)['success'] else 401)
        self.wfile.write(response.encode())
    
    def _handle_logout(self, data):
        token = data.get('token', '')
        
        if not token:
            self._set_headers(400)
            self.wfile.write(JSONResponse.error("Token required", 400).encode())
            return
        
        response = self.auth_system.logout(token)
        self._set_headers(200)
        self.wfile.write(response.encode())
    
    def _handle_verify_token(self):
        auth_header = self.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            self._set_headers(401)
            self.wfile.write(JSONResponse.error("Missing or invalid token", 401).encode())
            return
        
        token = auth_header.split(' ')[1]
        user_data = self.auth_system.verify_token(token)
        
        if user_data:
            self._set_headers(200)
            self.wfile.write(JSONResponse.success(user_data).encode())
        else:
            self._set_headers(401)
            self.wfile.write(JSONResponse.error("Invalid or expired token", 401).encode())
    
    def _handle_get_users(self):
        auth_header = self.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            self._set_headers(401)
            self.wfile.write(JSONResponse.error("Missing or invalid token", 401).encode())
            return
        
        token = auth_header.split(' ')[1]
        user_data = self.auth_system.verify_token(token)
        
        if not user_data:
            self._set_headers(401)
            self.wfile.write(JSONResponse.error("Invalid or expired token", 401).encode())
            return
        
        response = self.auth_system.get_all_users(user_data['role'])
        status_code = 200 if json.loads(response)['success'] else 403
        self._set_headers(status_code)
        self.wfile.write(response.encode())
    
    def _handle_update_role(self, data):
        auth_header = self.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            self._set_headers(401)
            self.wfile.write(JSONResponse.error("Missing or invalid token", 401).encode())
            return
        
        token = auth_header.split(' ')[1]
        user_data = self.auth_system.verify_token(token)
        
        if not user_data:
            self._set_headers(401)
            self.wfile.write(JSONResponse.error("Invalid or expired token", 401).encode())
            return
        
        user_id = data.get('user_id')
        new_role = data.get('new_role')
        
        if not all([user_id, new_role]):
            self._set_headers(400)
            self.wfile.write(JSONResponse.error("Missing required fields", 400).encode())
            return
        
        response = self.auth_system.update_user_role(user_id, new_role, user_data['role'])
        status_code = 200 if json.loads(response)['success'] else 403
        self._set_headers(status_code)
        self.wfile.write(response.encode())

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AuthRequestHandler)
    print(f'Server running on port {port}')
    print(f'API endpoints:')
    print(f'  POST http://localhost:{port}/api/register')
    print(f'  POST http://localhost:{port}/api/login')
    print(f'  POST http://localhost:{port}/api/logout')
    print(f'  GET  http://localhost:{port}/api/verify')
    print(f'  GET  http://localhost:{port}/api/users (admin only)')
    print(f'  POST http://localhost:{port}/api/users/update-role (admin only)')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()