#!/usr/bin/env python3
"""
PowerAutomation 端Admin完整功能實現
包含用戶界面、服務管理、統計監控等核心功能
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
import threading
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets
import hashlib
from edge_cloud_sync_core import EdgeAdminCore, SyncStatus, MessageType

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EdgeAdmin")

class ServiceStatus(Enum):
    """服務狀態"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"

@dataclass
class UserSession:
    """用戶會話"""
    session_id: str
    user_id: str
    username: str
    credit_balance: float
    login_time: datetime
    last_activity: datetime
    is_active: bool = True

class EdgeAdminUI:
    """端Admin用戶界面"""
    
    def __init__(self, edge_core: EdgeAdminCore, config: Dict[str, Any]):
        self.edge_core = edge_core
        self.config = config
        
        # Flask應用
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.app.secret_key = config.get('secret_key', secrets.token_hex(32))
        
        # SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 用戶會話管理
        self.user_sessions: Dict[str, UserSession] = {}
        self.session_lock = threading.Lock()
        
        # 服務狀態
        self.service_status = ServiceStatus.STOPPED
        
        # 註冊路由和事件
        self._register_routes()
        self._register_socketio_events()
        self._register_edge_callbacks()
    
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
            
            # 獲取統計數據
            stats = self.edge_core.get_statistics()
            
            return render_template('dashboard.html', 
                                 user=user_session,
                                 stats=stats,
                                 sync_status=self.edge_core.sync_status.value)
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """用戶登錄"""
            if request.method == 'POST':
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                
                # 驗證用戶（這裡簡化處理）
                if self._authenticate_user(username, password):
                    user_id = self._get_user_id(username)
                    session_id = str(uuid.uuid4())
                    
                    # 創建用戶會話
                    user_session = UserSession(
                        session_id=session_id,
                        user_id=user_id,
                        username=username,
                        credit_balance=0.0,  # 將從雲端同步
                        login_time=datetime.now(),
                        last_activity=datetime.now()
                    )
                    
                    with self.session_lock:
                        self.user_sessions[session_id] = user_session
                    
                    session['user_id'] = user_id
                    session['session_id'] = session_id
                    
                    # 同步用戶積分
                    asyncio.create_task(self.edge_core.sync_user_credits(user_id))
                    
                    return jsonify({
                        'success': True,
                        'redirect': url_for('index')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': '用戶名或密碼錯誤'
                    })
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """用戶登出"""
            session_id = session.get('session_id')
            if session_id and session_id in self.user_sessions:
                with self.session_lock:
                    self.user_sessions[session_id].is_active = False
                    del self.user_sessions[session_id]
            
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/api/statistics')
        def api_statistics():
            """獲取統計數據API"""
            if 'user_id' not in session:
                return jsonify({'error': '未登錄'}), 401
            
            stats = self.edge_core.get_statistics()
            return jsonify(stats)
        
        @self.app.route('/api/user/credits')
        def api_user_credits():
            """獲取用戶積分API"""
            if 'user_id' not in session:
                return jsonify({'error': '未登錄'}), 401
            
            session_id = session['session_id']
            user_session = self.user_sessions.get(session_id)
            
            if user_session:
                return jsonify({
                    'user_id': user_session.user_id,
                    'credit_balance': user_session.credit_balance,
                    'last_sync': user_session.last_activity.isoformat()
                })
            else:
                return jsonify({'error': '會話無效'}), 401
        
        @self.app.route('/api/service/request', methods=['POST'])
        def api_service_request():
            """服務請求API"""
            if 'user_id' not in session:
                return jsonify({'error': '未登錄'}), 401
            
            data = request.get_json()
            service_type = data.get('service_type')
            request_data = data.get('request_data', {})
            user_id = session['user_id']
            
            # 異步處理服務請求
            result = asyncio.create_task(
                self.edge_core.request_service(service_type, request_data, user_id)
            )
            
            return jsonify({'success': True, 'message': '請求已提交'})
        
        @self.app.route('/api/sync/credits', methods=['POST'])
        def api_sync_credits():
            """同步積分API"""
            if 'user_id' not in session:
                return jsonify({'error': '未登錄'}), 401
            
            user_id = session['user_id']
            
            # 異步同步積分
            asyncio.create_task(self.edge_core.sync_user_credits(user_id))
            
            return jsonify({'success': True, 'message': '積分同步請求已發送'})
        
        @self.app.route('/admin')
        def admin_dashboard():
            """管理員儀表板"""
            # 檢查管理員權限
            if not self._is_admin():
                return redirect(url_for('login'))
            
            # 獲取系統統計
            stats = self.edge_core.get_statistics()
            
            # 獲取用戶會話
            active_sessions = [
                session for session in self.user_sessions.values()
                if session.is_active
            ]
            
            return render_template('admin_dashboard.html',
                                 stats=stats,
                                 active_sessions=active_sessions,
                                 service_status=self.service_status.value)
        
        @self.app.route('/api/admin/users')
        def api_admin_users():
            """管理員用戶列表API"""
            if not self._is_admin():
                return jsonify({'error': '權限不足'}), 403
            
            users_data = []
            for session_data in self.user_sessions.values():
                if session_data.is_active:
                    users_data.append({
                        'user_id': session_data.user_id,
                        'username': session_data.username,
                        'credit_balance': session_data.credit_balance,
                        'login_time': session_data.login_time.isoformat(),
                        'last_activity': session_data.last_activity.isoformat()
                    })
            
            return jsonify(users_data)
        
        @self.app.route('/api/admin/service/control', methods=['POST'])
        def api_admin_service_control():
            """管理員服務控制API"""
            if not self._is_admin():
                return jsonify({'error': '權限不足'}), 403
            
            data = request.get_json()
            action = data.get('action')
            
            if action == 'start':
                self.service_status = ServiceStatus.STARTING
                # 啟動服務邏輯
                self.service_status = ServiceStatus.RUNNING
            elif action == 'stop':
                self.service_status = ServiceStatus.STOPPING
                # 停止服務邏輯
                self.service_status = ServiceStatus.STOPPED
            elif action == 'restart':
                self.service_status = ServiceStatus.STOPPING
                # 重啟服務邏輯
                self.service_status = ServiceStatus.RUNNING
            
            return jsonify({
                'success': True,
                'status': self.service_status.value
            })
    
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
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客戶端斷開"""
            if 'user_id' in session:
                leave_room(session['user_id'])
        
        @self.socketio.on('request_stats')
        def handle_request_stats():
            """請求統計數據"""
            if 'user_id' in session:
                stats = self.edge_core.get_statistics()
                emit('stats_update', stats)
        
        @self.socketio.on('ping')
        def handle_ping():
            """心跳檢測"""
            emit('pong', {'timestamp': datetime.now().isoformat()})
    
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
        
        def on_service_response(data):
            """服務響應"""
            request_id = data.get('request_id')
            self.socketio.emit('service_response', data, broadcast=True)
        
        def on_error(data):
            """錯誤事件"""
            self.socketio.emit('error', data, broadcast=True)
        
        # 註冊回調
        self.edge_core.register_event_callback('connected', on_connected)
        self.edge_core.register_event_callback('credit_synced', on_credit_synced)
        self.edge_core.register_event_callback('service_response', on_service_response)
        self.edge_core.register_event_callback('error', on_error)
    
    def _authenticate_user(self, username: str, password: str) -> bool:
        """驗證用戶（簡化實現）"""
        # 這裡應該連接到實際的用戶數據庫
        # 暫時使用硬編碼的測試用戶
        test_users = {
            'admin': 'admin123',
            'user1': 'password1',
            'user2': 'password2'
        }
        
        return test_users.get(username) == password
    
    def _get_user_id(self, username: str) -> str:
        """獲取用戶ID"""
        # 這裡應該從數據庫獲取真實的用戶ID
        return hashlib.md5(username.encode()).hexdigest()[:8]
    
    def _is_admin(self) -> bool:
        """檢查是否為管理員"""
        if 'user_id' not in session:
            return False
        
        session_id = session.get('session_id')
        user_session = self.user_sessions.get(session_id)
        
        # 簡化的管理員檢查
        return user_session and user_session.username == 'admin'
    
    def run(self, host='0.0.0.0', port=5001, debug=False):
        """運行端Admin UI"""
        logger.info(f"啟動端Admin UI - {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

class EdgeAdminManager:
    """端Admin管理器"""
    
    def __init__(self, config_path: str = "edge_admin_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # 初始化核心組件
        self.edge_core = EdgeAdminCore(self.config)
        self.ui = EdgeAdminUI(self.edge_core, self.config)
        
        # 運行狀態
        self.is_running = False
    
    def _load_config(self) -> Dict[str, Any]:
        """加載配置"""
        default_config = {
            "edge_id": str(uuid.uuid4()),
            "secret_key": secrets.token_hex(32),
            "cloud_endpoint": "wss://api.powerauto.ai/ws",
            "db_path": "edge_admin.db",
            "ui_host": "0.0.0.0",
            "ui_port": 5001,
            "debug": False
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
        except Exception as e:
            logger.warning(f"加載配置失敗，使用默認配置: {e}")
        
        # 保存配置
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存配置失敗: {e}")
    
    async def start(self):
        """啟動端Admin"""
        if self.is_running:
            logger.warning("端Admin已在運行")
            return
        
        logger.info("啟動PowerAutomation端Admin")
        self.is_running = True
        
        try:
            # 啟動端雲協同核心
            edge_task = asyncio.create_task(self.edge_core.start())
            
            # 啟動UI服務器（在新線程中）
            ui_thread = threading.Thread(
                target=self.ui.run,
                kwargs={
                    'host': self.config['ui_host'],
                    'port': self.config['ui_port'],
                    'debug': self.config['debug']
                }
            )
            ui_thread.daemon = True
            ui_thread.start()
            
            # 等待核心任務
            await edge_task
            
        except Exception as e:
            logger.error(f"端Admin運行錯誤: {e}")
            self.is_running = False
            raise
    
    def stop(self):
        """停止端Admin"""
        logger.info("停止PowerAutomation端Admin")
        self.is_running = False

# HTML模板
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 端Admin</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; margin-top: 5px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-connected { background: #27ae60; }
        .status-disconnected { background: #e74c3c; }
        .status-syncing { background: #f39c12; }
        .controls { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        .btn:hover { background: #2980b9; }
        .btn-success { background: #27ae60; }
        .btn-warning { background: #f39c12; }
        .btn-danger { background: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PowerAutomation 端Admin</h1>
            <p>用戶: {{ user.username }} | 積分: <span id="credit-balance">{{ user.credit_balance }}</span></p>
            <p>同步狀態: <span class="status-indicator status-{{ sync_status }}"></span>{{ sync_status }}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-requests">{{ stats.total_requests }}</div>
                <div class="stat-label">總請求數</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="tokens-saved">{{ stats.tokens_saved }}</div>
                <div class="stat-label">節省Token</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="edge-ratio">{{ "%.1f"|format(stats.edge_processing_ratio * 100) }}%</div>
                <div class="stat-label">端側處理比例</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="uptime">{{ stats.uptime_formatted }}</div>
                <div class="stat-label">運行時間</div>
            </div>
        </div>
        
        <div class="controls">
            <h3>操作控制</h3>
            <button class="btn btn-success" onclick="syncCredits()">同步積分</button>
            <button class="btn btn-warning" onclick="requestStats()">刷新統計</button>
            <button class="btn" onclick="testService()">測試服務</button>
            <button class="btn btn-danger" onclick="logout()">登出</button>
        </div>
    </div>

    <script>
        const socket = io();
        
        socket.on('connect', function() {
            console.log('已連接到端Admin');
        });
        
        socket.on('stats_update', function(stats) {
            document.getElementById('total-requests').textContent = stats.total_requests;
            document.getElementById('tokens-saved').textContent = stats.tokens_saved;
            document.getElementById('edge-ratio').textContent = (stats.edge_processing_ratio * 100).toFixed(1) + '%';
            document.getElementById('uptime').textContent = stats.uptime_formatted;
        });
        
        socket.on('credit_updated', function(data) {
            document.getElementById('credit-balance').textContent = data.balance;
        });
        
        function syncCredits() {
            fetch('/api/sync/credits', { method: 'POST' })
                .then(response => response.json())
                .then(data => alert(data.message));
        }
        
        function requestStats() {
            socket.emit('request_stats');
        }
        
        function testService() {
            fetch('/api/service/request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    service_type: 'ai_chat',
                    request_data: { query: '測試請求' }
                })
            })
            .then(response => response.json())
            .then(data => alert(data.message));
        }
        
        function logout() {
            window.location.href = '/logout';
        }
        
        // 自動刷新統計
        setInterval(requestStats, 30000);
    </script>
</body>
</html>
"""

# 使用示例
async def main():
    """主函數"""
    manager = EdgeAdminManager()
    
    print("=== PowerAutomation 端Admin 啟動 ===")
    print(f"Web界面: http://localhost:{manager.config['ui_port']}")
    print(f"Edge ID: {manager.config['edge_id']}")
    
    try:
        await manager.start()
    except KeyboardInterrupt:
        print("\n正在停止端Admin...")
        manager.stop()

if __name__ == "__main__":
    asyncio.run(main())

