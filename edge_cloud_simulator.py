#!/usr/bin/env python3
"""
PowerAutomation v0.5.2 本地端雲模擬環境
端側Admin + 雲側Admin 完整實現
"""

import asyncio
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import socket
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import uuid

# 導入動態網絡管理器
from dynamic_network_manager import DynamicNetworkManager, NetworkConfig


@dataclass
class ServiceConfig:
    """服務配置"""
    name: str
    host: str
    port: int
    status: str = "stopped"
    start_time: Optional[float] = None
    endpoint: Optional[str] = None


class PowerAutomationLogger:
    """統一日誌管理器"""
    
    @staticmethod
    def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


class EdgeAdminHandler(BaseHTTPRequestHandler):
    """端側Admin HTTP處理器"""
    
    def __init__(self, *args, edge_admin_server=None, **kwargs):
        self.edge_admin_server = edge_admin_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """處理GET請求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            
            if path == "/":
                self._handle_root()
            elif path == "/health":
                self._handle_health()
            elif path == "/api/discovery":
                self._handle_discovery()
            elif path == "/api/adapters":
                self._handle_adapters()
            elif path == "/api/sync":
                self._handle_sync()
            elif path == "/api/config":
                self._handle_config()
            else:
                self._handle_404()
                
        except Exception as e:
            self._handle_error(str(e))
    
    def do_POST(self):
        """處理POST請求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            if path == "/api/mcp/call":
                self._handle_mcp_call(post_data)
            elif path == "/api/sync/trigger":
                self._handle_sync_trigger(post_data)
            elif path == "/api/auth":
                self._handle_auth(post_data)
            else:
                self._handle_404()
                
        except Exception as e:
            self._handle_error(str(e))
    
    def _handle_root(self):
        """處理根路徑"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PowerAutomation 端側Admin v0.5.2</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .status {{ color: #4CAF50; font-weight: bold; }}
                .endpoint {{ background: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 PowerAutomation 端側Admin</h1>
                <p>版本: v0.5.2 | 狀態: <span class="status">運行中</span></p>
            </div>
            
            <div class="section">
                <h3>📊 服務信息</h3>
                <p><strong>服務地址:</strong> <span class="endpoint">{self.edge_admin_server.get_endpoint()}</span></p>
                <p><strong>啟動時間:</strong> {datetime.fromtimestamp(self.edge_admin_server.start_time).strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>已註冊適配器:</strong> {len(self.edge_admin_server.adapters)}個</p>
            </div>
            
            <div class="section">
                <h3>🔗 API端點</h3>
                <ul>
                    <li><a href="/health">健康檢查</a> - /health</li>
                    <li><a href="/api/discovery">服務發現</a> - /api/discovery</li>
                    <li><a href="/api/adapters">適配器列表</a> - /api/adapters</li>
                    <li><a href="/api/config">配置信息</a> - /api/config</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>🌐 雲側連接</h3>
                <p><strong>雲側Admin:</strong> <span class="endpoint">{self.edge_admin_server.cloud_admin_endpoint}</span></p>
                <p><strong>同步狀態:</strong> <span class="status">已連接</span></p>
            </div>
        </body>
        </html>
        """
        self._send_response(200, html, "text/html")
    
    def _handle_health(self):
        """健康檢查"""
        health_data = {
            "status": "healthy",
            "service": "EdgeAdmin",
            "version": "v0.5.2",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.edge_admin_server.start_time,
            "adapters_count": len(self.edge_admin_server.adapters)
        }
        self._send_json_response(200, health_data)
    
    def _handle_discovery(self):
        """服務發現"""
        discovery_data = {
            "service_name": "PowerAutomation EdgeAdmin",
            "version": "v0.5.2",
            "capabilities": [
                "mcp_adapter_management",
                "edge_cloud_sync",
                "dynamic_routing",
                "unified_auth"
            ],
            "endpoints": {
                "health": "/health",
                "adapters": "/api/adapters",
                "mcp_call": "/api/mcp/call",
                "sync": "/api/sync",
                "auth": "/api/auth"
            },
            "network_config": self.edge_admin_server.network_manager.get_config_info()
        }
        self._send_json_response(200, discovery_data)
    
    def _handle_adapters(self):
        """適配器列表"""
        adapters_data = {
            "total_count": len(self.edge_admin_server.adapters),
            "adapters": list(self.edge_admin_server.adapters.values()),
            "categories": self.edge_admin_server.get_adapter_categories()
        }
        self._send_json_response(200, adapters_data)
    
    def _handle_sync(self):
        """同步狀態"""
        sync_data = {
            "last_sync": self.edge_admin_server.last_sync_time,
            "sync_status": "active",
            "cloud_endpoint": self.edge_admin_server.cloud_admin_endpoint,
            "pending_operations": 0
        }
        self._send_json_response(200, sync_data)
    
    def _handle_config(self):
        """配置信息"""
        config_data = {
            "network": self.edge_admin_server.network_manager.get_config_info(),
            "adapters": {
                "total": len(self.edge_admin_server.adapters),
                "categories": self.edge_admin_server.get_adapter_categories()
            },
            "cloud_connection": {
                "endpoint": self.edge_admin_server.cloud_admin_endpoint,
                "status": "connected"
            }
        }
        self._send_json_response(200, config_data)
    
    def _handle_mcp_call(self, post_data: str):
        """處理MCP調用"""
        try:
            request_data = json.loads(post_data)
            adapter_name = request_data.get("adapter")
            method = request_data.get("method")
            params = request_data.get("params", {})
            
            # 模擬MCP調用
            result = self.edge_admin_server.call_mcp_adapter(adapter_name, method, params)
            self._send_json_response(200, result)
            
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_sync_trigger(self, post_data: str):
        """觸發同步"""
        try:
            sync_result = self.edge_admin_server.trigger_cloud_sync()
            self._send_json_response(200, sync_result)
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_auth(self, post_data: str):
        """處理認證"""
        try:
            auth_data = json.loads(post_data)
            auth_result = self.edge_admin_server.authenticate_user(auth_data)
            self._send_json_response(200, auth_result)
        except Exception as e:
            self._send_json_response(401, {"error": "Authentication failed"})
    
    def _handle_404(self):
        """404錯誤"""
        self._send_json_response(404, {"error": "Not Found"})
    
    def _handle_error(self, error_msg: str):
        """錯誤處理"""
        self._send_json_response(500, {"error": error_msg})
    
    def _send_response(self, status_code: int, content: str, content_type: str = "application/json"):
        """發送響應"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, status_code: int, data: Dict):
        """發送JSON響應"""
        content = json.dumps(data, ensure_ascii=False, indent=2)
        self._send_response(status_code, content, "application/json")
    
    def log_message(self, format, *args):
        """重寫日誌方法，避免過多輸出"""
        pass


class CloudAdminHandler(BaseHTTPRequestHandler):
    """雲側Admin HTTP處理器"""
    
    def __init__(self, *args, cloud_admin_server=None, **kwargs):
        self.cloud_admin_server = cloud_admin_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """處理GET請求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            
            if path == "/":
                self._handle_root()
            elif path == "/health":
                self._handle_health()
            elif path == "/api/config":
                self._handle_config()
            elif path == "/api/monitor":
                self._handle_monitor()
            elif path == "/api/edges":
                self._handle_edges()
            else:
                self._handle_404()
                
        except Exception as e:
            self._handle_error(str(e))
    
    def do_POST(self):
        """處理POST請求"""
        try:
            path = urllib.parse.urlparse(self.path).path
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            if path == "/api/sync/receive":
                self._handle_sync_receive(post_data)
            elif path == "/api/config/update":
                self._handle_config_update(post_data)
            else:
                self._handle_404()
                
        except Exception as e:
            self._handle_error(str(e))
    
    def _handle_root(self):
        """處理根路徑"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PowerAutomation 雲側Admin v0.5.2</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #FF9800; color: white; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .status {{ color: #4CAF50; font-weight: bold; }}
                .endpoint {{ background: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }}
                .edge-list {{ list-style: none; padding: 0; }}
                .edge-item {{ background: #f9f9f9; margin: 5px 0; padding: 10px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>☁️ PowerAutomation 雲側Admin</h1>
                <p>版本: v0.5.2 | 狀態: <span class="status">運行中</span></p>
            </div>
            
            <div class="section">
                <h3>📊 服務信息</h3>
                <p><strong>服務地址:</strong> <span class="endpoint">{self.cloud_admin_server.get_endpoint()}</span></p>
                <p><strong>啟動時間:</strong> {datetime.fromtimestamp(self.cloud_admin_server.start_time).strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>已連接端側:</strong> {len(self.cloud_admin_server.connected_edges)}個</p>
            </div>
            
            <div class="section">
                <h3>🔗 API端點</h3>
                <ul>
                    <li><a href="/health">健康檢查</a> - /health</li>
                    <li><a href="/api/config">配置管理</a> - /api/config</li>
                    <li><a href="/api/monitor">監控數據</a> - /api/monitor</li>
                    <li><a href="/api/edges">端側列表</a> - /api/edges</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>🌐 已連接端側</h3>
                <ul class="edge-list">
                    {self._generate_edge_list()}
                </ul>
            </div>
        </body>
        </html>
        """
        self._send_response(200, html, "text/html")
    
    def _generate_edge_list(self) -> str:
        """生成端側列表HTML"""
        if not self.cloud_admin_server.connected_edges:
            return '<li class="edge-item">暫無連接的端側Admin</li>'
        
        edge_html = ""
        for edge_id, edge_info in self.cloud_admin_server.connected_edges.items():
            edge_html += f'''
            <li class="edge-item">
                <strong>{edge_id}</strong><br>
                端點: {edge_info.get("endpoint", "N/A")}<br>
                狀態: <span class="status">{edge_info.get("status", "unknown")}</span><br>
                最後同步: {edge_info.get("last_sync", "N/A")}
            </li>
            '''
        return edge_html
    
    def _handle_health(self):
        """健康檢查"""
        health_data = {
            "status": "healthy",
            "service": "CloudAdmin",
            "version": "v0.5.2",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.cloud_admin_server.start_time,
            "connected_edges": len(self.cloud_admin_server.connected_edges)
        }
        self._send_json_response(200, health_data)
    
    def _handle_config(self):
        """配置管理"""
        config_data = {
            "global_config": self.cloud_admin_server.global_config,
            "edge_configs": self.cloud_admin_server.edge_configs,
            "last_updated": self.cloud_admin_server.config_last_updated
        }
        self._send_json_response(200, config_data)
    
    def _handle_monitor(self):
        """監控數據"""
        monitor_data = {
            "system_status": "healthy",
            "connected_edges": len(self.cloud_admin_server.connected_edges),
            "total_sync_operations": self.cloud_admin_server.sync_operations_count,
            "last_sync": self.cloud_admin_server.last_sync_time,
            "performance_metrics": {
                "avg_response_time": "150ms",
                "success_rate": "99.2%",
                "error_rate": "0.8%"
            }
        }
        self._send_json_response(200, monitor_data)
    
    def _handle_edges(self):
        """端側列表"""
        edges_data = {
            "total_count": len(self.cloud_admin_server.connected_edges),
            "edges": self.cloud_admin_server.connected_edges
        }
        self._send_json_response(200, edges_data)
    
    def _handle_sync_receive(self, post_data: str):
        """接收同步數據"""
        try:
            sync_data = json.loads(post_data)
            result = self.cloud_admin_server.receive_sync_data(sync_data)
            self._send_json_response(200, result)
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_config_update(self, post_data: str):
        """更新配置"""
        try:
            config_data = json.loads(post_data)
            result = self.cloud_admin_server.update_config(config_data)
            self._send_json_response(200, result)
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_404(self):
        """404錯誤"""
        self._send_json_response(404, {"error": "Not Found"})
    
    def _handle_error(self, error_msg: str):
        """錯誤處理"""
        self._send_json_response(500, {"error": error_msg})
    
    def _send_response(self, status_code: int, content: str, content_type: str = "application/json"):
        """發送響應"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, status_code: int, data: Dict):
        """發送JSON響應"""
        content = json.dumps(data, ensure_ascii=False, indent=2)
        self._send_response(status_code, content, "application/json")
    
    def log_message(self, format, *args):
        """重寫日誌方法，避免過多輸出"""
        pass


class EdgeAdminServer:
    """端側Admin服務器"""
    
    def __init__(self):
        self.logger = PowerAutomationLogger.setup_logger("EdgeAdminServer")
        self.network_manager = DynamicNetworkManager()
        self.config: Optional[NetworkConfig] = None
        self.server: Optional[HTTPServer] = None
        self.start_time: float = 0
        self.adapters: Dict[str, Dict] = {}
        self.cloud_admin_endpoint: str = ""
        self.last_sync_time: Optional[str] = None
        self.is_running = False
        
        # 初始化模擬適配器
        self._initialize_mock_adapters()
    
    def _initialize_mock_adapters(self):
        """初始化模擬適配器"""
        mock_adapters = [
            {"name": "simple_gemini", "type": "text_generation", "status": "active"},
            {"name": "claude_adapter", "type": "reasoning", "status": "active"},
            {"name": "file_manager", "type": "file_operations", "status": "active"},
            {"name": "web_scraper", "type": "web_services", "status": "active"},
            {"name": "data_processor", "type": "data_processing", "status": "active"}
        ]
        
        for adapter in mock_adapters:
            self.adapters[adapter["name"]] = adapter
    
    def start_server(self) -> bool:
        """啟動服務器"""
        try:
            # 獲取網絡配置
            self.config = self.network_manager.get_or_create_config()
            if not self.config:
                self.logger.error("無法獲取有效的網絡配置")
                return False
            
            # 創建HTTP服務器
            def handler(*args, **kwargs):
                return EdgeAdminHandler(*args, edge_admin_server=self, **kwargs)
            
            self.server = HTTPServer((self.config.ipv6_address, self.config.port), handler)
            self.start_time = time.time()
            self.is_running = True
            
            endpoint = f"http://[{self.config.ipv6_address}]:{self.config.port}"
            self.logger.info(f"🚀 端側Admin服務器已啟動: {endpoint}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"啟動端側Admin服務器失敗: {e}")
            return False
    
    def run_server(self):
        """運行服務器"""
        if self.server and self.is_running:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop_server()
    
    def stop_server(self):
        """停止服務器"""
        self.is_running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        self.logger.info("端側Admin服務器已停止")
    
    def get_endpoint(self) -> str:
        """獲取服務端點"""
        if self.config:
            return f"http://[{self.config.ipv6_address}]:{self.config.port}"
        return "未配置"
    
    def set_cloud_admin_endpoint(self, endpoint: str):
        """設置雲側Admin端點"""
        self.cloud_admin_endpoint = endpoint
        self.logger.info(f"雲側Admin端點已設置: {endpoint}")
    
    def get_adapter_categories(self) -> Dict[str, int]:
        """獲取適配器分類統計"""
        categories = {}
        for adapter in self.adapters.values():
            adapter_type = adapter.get("type", "unknown")
            categories[adapter_type] = categories.get(adapter_type, 0) + 1
        return categories
    
    def call_mcp_adapter(self, adapter_name: str, method: str, params: Dict) -> Dict:
        """調用MCP適配器"""
        if adapter_name not in self.adapters:
            return {"error": f"適配器 {adapter_name} 不存在"}
        
        # 模擬MCP調用
        result = {
            "adapter": adapter_name,
            "method": method,
            "params": params,
            "result": f"模擬調用 {adapter_name}.{method} 成功",
            "timestamp": datetime.now().isoformat(),
            "execution_time": "0.5s"
        }
        
        self.logger.info(f"MCP調用: {adapter_name}.{method}")
        return result
    
    def trigger_cloud_sync(self) -> Dict:
        """觸發雲側同步"""
        sync_data = {
            "edge_id": f"edge_{self.config.port}",
            "timestamp": datetime.now().isoformat(),
            "adapters": self.adapters,
            "status": "active"
        }
        
        self.last_sync_time = datetime.now().isoformat()
        self.logger.info("觸發雲側同步")
        
        return {
            "status": "success",
            "sync_time": self.last_sync_time,
            "data_size": len(json.dumps(sync_data))
        }
    
    def authenticate_user(self, auth_data: Dict) -> Dict:
        """用戶認證"""
        username = auth_data.get("username")
        password = auth_data.get("password")
        
        # 模擬認證邏輯
        if username and password:
            token = str(uuid.uuid4())
            return {
                "status": "success",
                "token": token,
                "user": username,
                "expires": (time.time() + 3600)  # 1小時後過期
            }
        else:
            return {"status": "failed", "error": "Invalid credentials"}


class CloudAdminServer:
    """雲側Admin服務器"""
    
    def __init__(self):
        self.logger = PowerAutomationLogger.setup_logger("CloudAdminServer")
        self.network_manager = DynamicNetworkManager()
        self.config: Optional[NetworkConfig] = None
        self.server: Optional[HTTPServer] = None
        self.start_time: float = 0
        self.connected_edges: Dict[str, Dict] = {}
        self.global_config: Dict = {}
        self.edge_configs: Dict = {}
        self.config_last_updated: Optional[str] = None
        self.sync_operations_count: int = 0
        self.last_sync_time: Optional[str] = None
        self.is_running = False
        
        # 初始化配置
        self._initialize_config()
    
    def _initialize_config(self):
        """初始化配置"""
        self.global_config = {
            "version": "v0.5.2",
            "max_edges": 100,
            "sync_interval": 300,  # 5分鐘
            "auth_required": True
        }
        self.config_last_updated = datetime.now().isoformat()
    
    def start_server(self, preferred_port: int = 6001) -> bool:
        """啟動服務器"""
        try:
            # 為雲側Admin找到可用端口
            ipv6_configs = self.network_manager.discover_ipv6_addresses()
            
            for config in ipv6_configs:
                available_port = self.network_manager.find_available_port(
                    config.ipv6_address, 
                    [preferred_port, preferred_port + 1, preferred_port + 2]
                )
                if available_port:
                    config.port = available_port
                    self.config = config
                    break
            
            if not self.config:
                self.logger.error("無法為雲側Admin找到可用端口")
                return False
            
            # 創建HTTP服務器
            def handler(*args, **kwargs):
                return CloudAdminHandler(*args, cloud_admin_server=self, **kwargs)
            
            self.server = HTTPServer((self.config.ipv6_address, self.config.port), handler)
            self.start_time = time.time()
            self.is_running = True
            
            endpoint = f"http://[{self.config.ipv6_address}]:{self.config.port}"
            self.logger.info(f"☁️ 雲側Admin服務器已啟動: {endpoint}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"啟動雲側Admin服務器失敗: {e}")
            return False
    
    def run_server(self):
        """運行服務器"""
        if self.server and self.is_running:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop_server()
    
    def stop_server(self):
        """停止服務器"""
        self.is_running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        self.logger.info("雲側Admin服務器已停止")
    
    def get_endpoint(self) -> str:
        """獲取服務端點"""
        if self.config:
            return f"http://[{self.config.ipv6_address}]:{self.config.port}"
        return "未配置"
    
    def register_edge(self, edge_id: str, edge_info: Dict):
        """註冊端側Admin"""
        self.connected_edges[edge_id] = {
            **edge_info,
            "registered_time": datetime.now().isoformat(),
            "status": "connected"
        }
        self.logger.info(f"端側Admin已註冊: {edge_id}")
    
    def receive_sync_data(self, sync_data: Dict) -> Dict:
        """接收同步數據"""
        edge_id = sync_data.get("edge_id", "unknown")
        
        # 更新端側信息
        if edge_id not in self.connected_edges:
            self.connected_edges[edge_id] = {}
        
        self.connected_edges[edge_id].update({
            "last_sync": datetime.now().isoformat(),
            "adapters_count": len(sync_data.get("adapters", {})),
            "status": sync_data.get("status", "unknown")
        })
        
        self.sync_operations_count += 1
        self.last_sync_time = datetime.now().isoformat()
        
        self.logger.info(f"接收到端側同步數據: {edge_id}")
        
        return {
            "status": "received",
            "edge_id": edge_id,
            "timestamp": self.last_sync_time
        }
    
    def update_config(self, config_data: Dict) -> Dict:
        """更新配置"""
        try:
            if "global" in config_data:
                self.global_config.update(config_data["global"])
            
            if "edges" in config_data:
                self.edge_configs.update(config_data["edges"])
            
            self.config_last_updated = datetime.now().isoformat()
            
            self.logger.info("配置已更新")
            
            return {
                "status": "updated",
                "timestamp": self.config_last_updated
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}


class PowerAutomationOrchestrator:
    """PowerAutomation協調器 - 管理端雲服務"""
    
    def __init__(self):
        self.logger = PowerAutomationLogger.setup_logger("PowerAutomationOrchestrator")
        self.edge_admin = EdgeAdminServer()
        self.cloud_admin = CloudAdminServer()
        self.services: Dict[str, ServiceConfig] = {}
    
    def start_all_services(self) -> bool:
        """啟動所有服務"""
        self.logger.info("🚀 啟動PowerAutomation v0.5.2 本地端雲模擬環境")
        
        # 啟動雲側Admin
        if self.cloud_admin.start_server():
            cloud_config = ServiceConfig(
                name="CloudAdmin",
                host=self.cloud_admin.config.ipv6_address,
                port=self.cloud_admin.config.port,
                status="running",
                start_time=time.time(),
                endpoint=self.cloud_admin.get_endpoint()
            )
            self.services["cloud_admin"] = cloud_config
        else:
            self.logger.error("雲側Admin啟動失敗")
            return False
        
        # 啟動端側Admin
        if self.edge_admin.start_server():
            # 設置雲側Admin端點
            self.edge_admin.set_cloud_admin_endpoint(self.cloud_admin.get_endpoint())
            
            edge_config = ServiceConfig(
                name="EdgeAdmin",
                host=self.edge_admin.config.ipv6_address,
                port=self.edge_admin.config.port,
                status="running",
                start_time=time.time(),
                endpoint=self.edge_admin.get_endpoint()
            )
            self.services["edge_admin"] = edge_config
            
            # 在雲側註冊端側
            edge_id = f"edge_{self.edge_admin.config.port}"
            self.cloud_admin.register_edge(edge_id, {
                "endpoint": self.edge_admin.get_endpoint(),
                "adapters_count": len(self.edge_admin.adapters)
            })
            
        else:
            self.logger.error("端側Admin啟動失敗")
            return False
        
        self._print_startup_summary()
        return True
    
    def _print_startup_summary(self):
        """打印啟動摘要"""
        print("\n" + "="*80)
        print("🎉 PowerAutomation v0.5.2 本地端雲模擬環境啟動成功!")
        print("="*80)
        
        for service_name, service_config in self.services.items():
            print(f"\n📋 {service_config.name}:")
            print(f"   端點: {service_config.endpoint}")
            print(f"   狀態: {service_config.status}")
            print(f"   啟動時間: {datetime.fromtimestamp(service_config.start_time).strftime('%H:%M:%S')}")
        
        print(f"\n🔗 服務連接:")
        print(f"   端側Admin → 雲側Admin: {self.edge_admin.cloud_admin_endpoint}")
        print(f"   已註冊適配器: {len(self.edge_admin.adapters)}個")
        print(f"   已連接端側: {len(self.cloud_admin.connected_edges)}個")
        
        print(f"\n🌐 訪問地址:")
        print(f"   端側Admin Web界面: {self.edge_admin.get_endpoint()}")
        print(f"   雲側Admin Web界面: {self.cloud_admin.get_endpoint()}")
        
        print(f"\n⚡ API測試:")
        print(f"   curl {self.edge_admin.get_endpoint()}/health")
        print(f"   curl {self.cloud_admin.get_endpoint()}/health")
        
        print("\n按 Ctrl+C 停止所有服務")
        print("="*80)
    
    def run_services(self):
        """運行服務"""
        try:
            # 在不同線程中運行服務
            edge_thread = threading.Thread(target=self.edge_admin.run_server)
            cloud_thread = threading.Thread(target=self.cloud_admin.run_server)
            
            edge_thread.daemon = True
            cloud_thread.daemon = True
            
            edge_thread.start()
            cloud_thread.start()
            
            # 主線程等待
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop_all_services()
    
    def stop_all_services(self):
        """停止所有服務"""
        self.logger.info("停止所有服務...")
        self.edge_admin.stop_server()
        self.cloud_admin.stop_server()
        
        for service_name in self.services:
            self.services[service_name].status = "stopped"
        
        print("\n✅ 所有服務已停止")
    
    def get_services_status(self) -> Dict:
        """獲取服務狀態"""
        return {
            "services": {name: asdict(config) for name, config in self.services.items()},
            "edge_admin": {
                "adapters_count": len(self.edge_admin.adapters),
                "cloud_endpoint": self.edge_admin.cloud_admin_endpoint
            },
            "cloud_admin": {
                "connected_edges": len(self.cloud_admin.connected_edges),
                "sync_operations": self.cloud_admin.sync_operations_count
            }
        }


def main():
    """主函數"""
    orchestrator = PowerAutomationOrchestrator()
    
    if orchestrator.start_all_services():
        orchestrator.run_services()
    else:
        print("❌ 服務啟動失敗")


if __name__ == "__main__":
    main()

