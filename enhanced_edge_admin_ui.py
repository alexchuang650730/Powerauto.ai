#!/usr/bin/env python3
"""
PowerAutomation 端Admin完整管理界面
包含用戶管理、系統監控、Qwen模型管理、登錄體驗優化、編碼器協同等功能
"""

import asyncio
import json
import logging
import time
import uuid
import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
import threading
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import io
import base64
from edge_cloud_sync_core import EdgeAdminCore, SyncStatus, MessageType
from intelligent_qwen_mcp import IntelligentQwenMCP, SystemDetector

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EdgeAdminUI")

class UserRole(Enum):
    """用戶角色"""
    ADMIN = "admin"
    USER = "user"
    DEVELOPER = "developer"
    GUEST = "guest"

class LoginMethod(Enum):
    """登錄方式"""
    PASSWORD = "password"
    QR_CODE = "qr_code"
    TOKEN = "token"
    SSO = "sso"

@dataclass
class EnhancedUserSession:
    """增強用戶會話"""
    session_id: str
    user_id: str
    username: str
    email: str
    role: UserRole
    credit_balance: float
    login_time: datetime
    last_activity: datetime
    login_method: LoginMethod
    device_info: Dict[str, Any]
    preferences: Dict[str, Any]
    is_active: bool = True

class CodeEditorIntegration:
    """編碼器集成"""
    
    def __init__(self, qwen_mcp: IntelligentQwenMCP):
        self.qwen_mcp = qwen_mcp
        self.active_sessions = {}
        self.code_suggestions_cache = {}
        
    async def handle_code_completion(self, code_context: str, cursor_position: int, 
                                   language: str = "python") -> Dict[str, Any]:
        """處理代碼補全"""
        try:
            prompt = f"""
作為一個專業的代碼助手，請為以下代碼提供智能補全建議：

語言: {language}
代碼上下文:
```{language}
{code_context}
```

光標位置: {cursor_position}

請提供3-5個最相關的代碼補全建議，每個建議包含：
1. 補全代碼
2. 簡短說明
3. 置信度評分(0-1)

返回JSON格式。
"""
            
            response = await self.qwen_mcp.process_request({
                'prompt': prompt,
                'user_id': 'code_editor',
                'max_tokens': 1024,
                'temperature': 0.3
            })
            
            if response['success']:
                # 解析AI響應並格式化為代碼補全建議
                suggestions = self._parse_code_suggestions(response['content'])
                return {
                    'success': True,
                    'suggestions': suggestions,
                    'model_used': response.get('model_used'),
                    'response_time': response.get('generation_time', 0)
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', '代碼補全失敗')
                }
                
        except Exception as e:
            logger.error(f"代碼補全處理失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def handle_code_explanation(self, code_snippet: str, language: str = "python") -> Dict[str, Any]:
        """處理代碼解釋"""
        try:
            prompt = f"""
請詳細解釋以下{language}代碼的功能、邏輯和最佳實踐：

```{language}
{code_snippet}
```

請包含：
1. 代碼功能概述
2. 逐行解釋
3. 潛在問題或改進建議
4. 相關最佳實踐
"""
            
            response = await self.qwen_mcp.process_request({
                'prompt': prompt,
                'user_id': 'code_editor',
                'max_tokens': 2048,
                'temperature': 0.5
            })
            
            return response
            
        except Exception as e:
            logger.error(f"代碼解釋處理失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def handle_code_optimization(self, code_snippet: str, language: str = "python") -> Dict[str, Any]:
        """處理代碼優化"""
        try:
            prompt = f"""
請優化以下{language}代碼，提供性能更好、更簡潔、更符合最佳實踐的版本：

原始代碼:
```{language}
{code_snippet}
```

請提供：
1. 優化後的代碼
2. 優化說明
3. 性能提升預期
4. 注意事項
"""
            
            response = await self.qwen_mcp.process_request({
                'prompt': prompt,
                'user_id': 'code_editor',
                'max_tokens': 2048,
                'temperature': 0.4
            })
            
            return response
            
        except Exception as e:
            logger.error(f"代碼優化處理失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_code_suggestions(self, ai_response: str) -> List[Dict[str, Any]]:
        """解析AI響應為代碼建議"""
        try:
            # 嘗試解析JSON響應
            if ai_response.strip().startswith('{') or ai_response.strip().startswith('['):
                return json.loads(ai_response)
            
            # 如果不是JSON，則解析文本格式
            suggestions = []
            lines = ai_response.split('\n')
            current_suggestion = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('```'):
                    if 'code' not in current_suggestion:
                        current_suggestion['code'] = ''
                    else:
                        if current_suggestion:
                            suggestions.append(current_suggestion)
                            current_suggestion = {}
                elif 'code' in current_suggestion and not line.startswith('```'):
                    current_suggestion['code'] += line + '\n'
                elif line and 'description' not in current_suggestion:
                    current_suggestion['description'] = line
                    current_suggestion['confidence'] = 0.8  # 默認置信度
            
            if current_suggestion:
                suggestions.append(current_suggestion)
            
            return suggestions[:5]  # 最多返回5個建議
            
        except Exception as e:
            logger.error(f"解析代碼建議失敗: {e}")
            return [{
                'code': '// AI建議解析失敗',
                'description': '無法解析AI響應',
                'confidence': 0.1
            }]

class EnhancedEdgeAdminUI:
    """增強的端Admin用戶界面"""
    
    def __init__(self, edge_core: EdgeAdminCore, qwen_mcp: IntelligentQwenMCP, config: Dict[str, Any]):
        self.edge_core = edge_core
        self.qwen_mcp = qwen_mcp
        self.config = config
        
        # Flask應用
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.app.secret_key = config.get('secret_key', secrets.token_hex(32))
        
        # SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 用戶會話管理
        self.user_sessions: Dict[str, EnhancedUserSession] = {}
        self.session_lock = threading.Lock()
        
        # 編碼器集成
        self.code_editor = CodeEditorIntegration(qwen_mcp)
        
        # QR碼登錄
        self.qr_login_tokens = {}
        
        # JWT配置
        self.jwt_secret = config.get('jwt_secret', secrets.token_hex(32))
        
        # 初始化數據庫
        self._init_user_database()
        
        # 註冊路由和事件
        self._register_routes()
        self._register_socketio_events()
        self._register_edge_callbacks()
    
    def _init_user_database(self):
        """初始化用戶數據庫"""
        with sqlite3.connect('edge_admin_users.db') as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    preferences TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS login_history (
                    login_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    login_method TEXT NOT NULL,
                    device_info TEXT NOT NULL,
                    ip_address TEXT,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL
                )
            """)
            
            # 創建默認管理員用戶
            admin_password = generate_password_hash('admin123')
            conn.execute("""
                INSERT OR IGNORE INTO users 
                (user_id, username, email, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                'admin',
                'admin@powerauto.ai',
                admin_password,
                UserRole.ADMIN.value
            ))
            
            conn.commit()
    
    def _register_routes(self):
        """註冊Flask路由"""
        
        @self.app.route('/')
        def index():
            """主頁"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_session = self.user_sessions.get(session['session_id'])
            if not user_session or not user_session.is_active:
                return redirect(url_for('login'))
            
            # 根據用戶角色重定向
            if user_session.role == UserRole.ADMIN:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """增強登錄頁面"""
            if request.method == 'POST':
                data = request.get_json()
                login_method = data.get('method', 'password')
                
                if login_method == 'password':
                    return self._handle_password_login(data)
                elif login_method == 'qr_code':
                    return self._handle_qr_login(data)
                elif login_method == 'token':
                    return self._handle_token_login(data)
                else:
                    return jsonify({
                        'success': False,
                        'error': '不支持的登錄方式'
                    })
            
            # 生成QR碼登錄token
            qr_token = str(uuid.uuid4())
            self.qr_login_tokens[qr_token] = {
                'created_at': datetime.now(),
                'used': False
            }
            
            # 生成QR碼
            qr_code_data = self._generate_qr_code(qr_token)
            
            return render_template('enhanced_login.html', 
                                 qr_token=qr_token,
                                 qr_code_data=qr_code_data)
        
        @self.app.route('/admin')
        def admin_dashboard():
            """管理員儀表板"""
            if not self._check_admin_permission():
                return redirect(url_for('login'))
            
            # 獲取系統統計
            stats = self.edge_core.get_statistics()
            qwen_stats = self.qwen_mcp.get_statistics()
            
            # 獲取用戶會話
            active_sessions = [
                session for session in self.user_sessions.values()
                if session.is_active
            ]
            
            return render_template('admin_dashboard.html',
                                 stats=stats,
                                 qwen_stats=qwen_stats,
                                 active_sessions=active_sessions)
        
        @self.app.route('/user')
        def user_dashboard():
            """用戶儀表板"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_session = self.user_sessions.get(session['session_id'])
            if not user_session:
                return redirect(url_for('login'))
            
            return render_template('user_dashboard.html', user=user_session)
        
        @self.app.route('/code-editor')
        def code_editor():
            """代碼編輯器頁面"""
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            return render_template('code_editor.html')
        
        # API路由
        @self.app.route('/api/code/complete', methods=['POST'])
        def api_code_complete():
            """代碼補全API"""
            if not self._check_user_permission():
                return jsonify({'error': '未授權'}), 401
            
            data = request.get_json()
            code_context = data.get('code', '')
            cursor_position = data.get('cursor', 0)
            language = data.get('language', 'python')
            
            # 異步處理代碼補全
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.code_editor.handle_code_completion(code_context, cursor_position, language)
            )
            loop.close()
            
            return jsonify(result)
        
        @self.app.route('/api/code/explain', methods=['POST'])
        def api_code_explain():
            """代碼解釋API"""
            if not self._check_user_permission():
                return jsonify({'error': '未授權'}), 401
            
            data = request.get_json()
            code_snippet = data.get('code', '')
            language = data.get('language', 'python')
            
            # 異步處理代碼解釋
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.code_editor.handle_code_explanation(code_snippet, language)
            )
            loop.close()
            
            return jsonify(result)
        
        @self.app.route('/api/code/optimize', methods=['POST'])
        def api_code_optimize():
            """代碼優化API"""
            if not self._check_user_permission():
                return jsonify({'error': '未授權'}), 401
            
            data = request.get_json()
            code_snippet = data.get('code', '')
            language = data.get('language', 'python')
            
            # 異步處理代碼優化
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.code_editor.handle_code_optimization(code_snippet, language)
            )
            loop.close()
            
            return jsonify(result)
        
        @self.app.route('/api/qwen/switch-model', methods=['POST'])
        def api_switch_qwen_model():
            """切換Qwen模型API"""
            if not self._check_admin_permission():
                return jsonify({'error': '權限不足'}), 403
            
            data = request.get_json()
            target_model = data.get('model')
            
            # 異步切換模型
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.qwen_mcp.model_manager.switch_model(target_model)
            )
            loop.close()
            
            return jsonify(result)
        
        @self.app.route('/api/admin/users')
        def api_admin_users():
            """管理員用戶列表API"""
            if not self._check_admin_permission():
                return jsonify({'error': '權限不足'}), 403
            
            users_data = []
            for session_data in self.user_sessions.values():
                if session_data.is_active:
                    users_data.append({
                        'user_id': session_data.user_id,
                        'username': session_data.username,
                        'email': session_data.email,
                        'role': session_data.role.value,
                        'credit_balance': session_data.credit_balance,
                        'login_time': session_data.login_time.isoformat(),
                        'last_activity': session_data.last_activity.isoformat(),
                        'login_method': session_data.login_method.value,
                        'device_info': session_data.device_info
                    })
            
            return jsonify(users_data)
        
        @self.app.route('/api/qr-login/<token>')
        def api_qr_login_status(token):
            """QR碼登錄狀態檢查"""
            if token in self.qr_login_tokens:
                token_data = self.qr_login_tokens[token]
                if token_data['used']:
                    return jsonify({
                        'status': 'success',
                        'redirect': url_for('index')
                    })
                elif datetime.now() - token_data['created_at'] > timedelta(minutes=5):
                    del self.qr_login_tokens[token]
                    return jsonify({'status': 'expired'})
                else:
                    return jsonify({'status': 'waiting'})
            else:
                return jsonify({'status': 'invalid'})
    
    def _handle_password_login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理密碼登錄"""
        username = data.get('username')
        password = data.get('password')
        device_info = data.get('device_info', {})
        
        # 驗證用戶
        user_data = self._authenticate_user(username, password)
        if user_data:
            session_id = self._create_user_session(user_data, LoginMethod.PASSWORD, device_info)
            
            return jsonify({
                'success': True,
                'redirect': url_for('index'),
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '用戶名或密碼錯誤'
            })
    
    def _handle_qr_login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理QR碼登錄"""
        token = data.get('token')
        username = data.get('username')
        password = data.get('password')
        
        if token not in self.qr_login_tokens:
            return jsonify({
                'success': False,
                'error': 'QR碼已過期'
            })
        
        # 驗證用戶
        user_data = self._authenticate_user(username, password)
        if user_data:
            # 標記QR碼已使用
            self.qr_login_tokens[token]['used'] = True
            
            session_id = self._create_user_session(user_data, LoginMethod.QR_CODE, {})
            
            return jsonify({
                'success': True,
                'message': 'QR碼登錄成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '用戶名或密碼錯誤'
            })
    
    def _handle_token_login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理Token登錄"""
        token = data.get('token')
        
        try:
            # 驗證JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # 獲取用戶數據
            with sqlite3.connect('edge_admin_users.db') as conn:
                cursor = conn.execute(
                    "SELECT user_id, username, email, role FROM users WHERE user_id = ? AND is_active = 1",
                    (user_id,)
                )
                user_row = cursor.fetchone()
                
                if user_row:
                    user_data = {
                        'user_id': user_row[0],
                        'username': user_row[1],
                        'email': user_row[2],
                        'role': user_row[3]
                    }
                    
                    session_id = self._create_user_session(user_data, LoginMethod.TOKEN, {})
                    
                    return jsonify({
                        'success': True,
                        'redirect': url_for('index')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '用戶不存在或已禁用'
                    })
                    
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token已過期'
            })
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': '無效Token'
            })
    
    def _authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """驗證用戶"""
        try:
            with sqlite3.connect('edge_admin_users.db') as conn:
                cursor = conn.execute(
                    "SELECT user_id, username, email, password_hash, role FROM users WHERE username = ? AND is_active = 1",
                    (username,)
                )
                user_row = cursor.fetchone()
                
                if user_row and check_password_hash(user_row[3], password):
                    return {
                        'user_id': user_row[0],
                        'username': user_row[1],
                        'email': user_row[2],
                        'role': user_row[4]
                    }
                    
        except Exception as e:
            logger.error(f"用戶驗證失敗: {e}")
        
        return None
    
    def _create_user_session(self, user_data: Dict[str, Any], login_method: LoginMethod, 
                           device_info: Dict[str, Any]) -> str:
        """創建用戶會話"""
        session_id = str(uuid.uuid4())
        
        # 創建增強用戶會話
        user_session = EnhancedUserSession(
            session_id=session_id,
            user_id=user_data['user_id'],
            username=user_data['username'],
            email=user_data['email'],
            role=UserRole(user_data['role']),
            credit_balance=0.0,  # 將從雲端同步
            login_time=datetime.now(),
            last_activity=datetime.now(),
            login_method=login_method,
            device_info=device_info,
            preferences={}
        )
        
        with self.session_lock:
            self.user_sessions[session_id] = user_session
        
        # 設置Flask session
        session['user_id'] = user_data['user_id']
        session['session_id'] = session_id
        
        # 記錄登錄歷史
        self._log_login_attempt(user_data['user_id'], login_method, device_info, True)
        
        # 同步用戶積分
        asyncio.create_task(self.edge_core.sync_user_credits(user_data['user_id']))
        
        return session_id
    
    def _log_login_attempt(self, user_id: str, login_method: LoginMethod, 
                          device_info: Dict[str, Any], success: bool):
        """記錄登錄嘗試"""
        try:
            with sqlite3.connect('edge_admin_users.db') as conn:
                conn.execute("""
                    INSERT INTO login_history 
                    (login_id, user_id, login_method, device_info, ip_address, success)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    user_id,
                    login_method.value,
                    json.dumps(device_info),
                    request.remote_addr if request else 'unknown',
                    success
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"記錄登錄歷史失敗: {e}")
    
    def _generate_qr_code(self, token: str) -> str:
        """生成QR碼"""
        try:
            qr_data = {
                'type': 'powerauto_login',
                'token': token,
                'endpoint': f"http://localhost:{self.config.get('ui_port', 5001)}/api/qr-login/{token}"
            }
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 轉換為base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"生成QR碼失敗: {e}")
            return ""
    
    def _check_user_permission(self) -> bool:
        """檢查用戶權限"""
        if 'user_id' not in session:
            return False
        
        session_id = session.get('session_id')
        user_session = self.user_sessions.get(session_id)
        
        return user_session and user_session.is_active
    
    def _check_admin_permission(self) -> bool:
        """檢查管理員權限"""
        if not self._check_user_permission():
            return False
        
        session_id = session.get('session_id')
        user_session = self.user_sessions.get(session_id)
        
        return user_session and user_session.role == UserRole.ADMIN
    
    def _register_socketio_events(self):
        """註冊SocketIO事件"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """客戶端連接"""
            if 'user_id' in session:
                join_room(session['user_id'])
                emit('connected', {'message': '連接成功'})
            else:
                emit('error', {'message': '未登錄'})
        
        @self.socketio.on('code_completion_request')
        def handle_code_completion(data):
            """實時代碼補全請求"""
            if not self._check_user_permission():
                emit('error', {'message': '未授權'})
                return
            
            # 異步處理代碼補全
            async def process_completion():
                result = await self.code_editor.handle_code_completion(
                    data.get('code', ''),
                    data.get('cursor', 0),
                    data.get('language', 'python')
                )
                self.socketio.emit('code_completion_response', result, room=session['user_id'])
            
            asyncio.create_task(process_completion())
    
    def _register_edge_callbacks(self):
        """註冊端雲協同事件回調"""
        
        def on_connected(data):
            """雲端連接成功"""
            self.socketio.emit('cloud_connected', data, broadcast=True)
        
        def on_credit_synced(data):
            """積分同步完成"""
            user_id = data.get('user_id')
            balance = data.get('balance')
            
            # 更新用戶會話中的積分
            for session_data in self.user_sessions.values():
                if session_data.user_id == user_id:
                    session_data.credit_balance = balance
                    session_data.last_activity = datetime.now()
                    break
            
            # 通知前端
            self.socketio.emit('credit_updated', data, room=user_id)
        
        # 註冊回調
        self.edge_core.register_event_callback('connected', on_connected)
        self.edge_core.register_event_callback('credit_synced', on_credit_synced)
    
    def run(self, host='0.0.0.0', port=5001, debug=False):
        """運行端Admin UI"""
        logger.info(f"啟動增強端Admin UI - {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# 使用示例
async def main():
    """主函數"""
    config = {
        'edge_id': 'edge_001',
        'secret_key': 'your_secret_key_here',
        'cloud_endpoint': 'wss://api.powerauto.ai/ws',
        'db_path': 'edge_admin.db',
        'ui_host': '0.0.0.0',
        'ui_port': 5001,
        'debug': True
    }
    
    # 初始化組件
    edge_core = EdgeAdminCore(config)
    qwen_mcp = IntelligentQwenMCP(config)
    await qwen_mcp.initialize()
    
    # 創建增強UI
    ui = EnhancedEdgeAdminUI(edge_core, qwen_mcp, config)
    
    print("=== PowerAutomation 增強端Admin UI ===")
    print(f"Web界面: http://localhost:{config['ui_port']}")
    print(f"管理員界面: http://localhost:{config['ui_port']}/admin")
    print(f"代碼編輯器: http://localhost:{config['ui_port']}/code-editor")
    print("默認管理員賬號: admin / admin123")
    
    # 啟動UI服務器
    ui.run(host=config['ui_host'], port=config['ui_port'], debug=config['debug'])

if __name__ == "__main__":
    asyncio.run(main())

