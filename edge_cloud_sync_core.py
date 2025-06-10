#!/usr/bin/env python3
"""
PowerAutomation 端雲協同核心機制
實現端側Admin和雲側Admin的完美協同工作
"""

import asyncio
import json
import logging
import time
import uuid
import websockets
import aiohttp
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import hashlib
import hmac
import ssl
import certifi

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EdgeCloudSync")

class SyncStatus(Enum):
    """同步狀態"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"
    ERROR = "error"
    RECONNECTING = "reconnecting"

class MessageType(Enum):
    """消息類型"""
    HEARTBEAT = "heartbeat"
    CREDIT_SYNC = "credit_sync"
    USER_AUTH = "user_auth"
    SERVICE_REQUEST = "service_request"
    SERVICE_RESPONSE = "service_response"
    STATISTICS = "statistics"
    CONFIG_UPDATE = "config_update"
    ERROR = "error"

@dataclass
class SyncMessage:
    """同步消息"""
    message_id: str
    message_type: MessageType
    source: str  # edge_admin 或 cloud_admin
    target: str
    payload: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None

class EdgeCloudProtocol:
    """端雲協同協議"""
    
    def __init__(self, edge_id: str, secret_key: str):
        self.edge_id = edge_id
        self.secret_key = secret_key
        self.protocol_version = "1.0"
        
    def sign_message(self, message: SyncMessage) -> str:
        """簽名消息"""
        payload_str = json.dumps(message.payload, sort_keys=True)
        message_data = f"{message.message_id}:{message.message_type.value}:{payload_str}:{message.timestamp.isoformat()}"
        return hmac.new(
            self.secret_key.encode(),
            message_data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_message(self, message: SyncMessage) -> bool:
        """驗證消息簽名"""
        if not message.signature:
            return False
        expected_signature = self.sign_message(message)
        return hmac.compare_digest(expected_signature, message.signature)
    
    def create_message(self, message_type: MessageType, payload: Dict[str, Any], 
                      target: str = "cloud_admin") -> SyncMessage:
        """創建消息"""
        message = SyncMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            source="edge_admin",
            target=target,
            payload=payload,
            timestamp=datetime.now()
        )
        message.signature = self.sign_message(message)
        return message

class EdgeAdminCore:
    """端Admin核心功能"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.edge_id = config.get("edge_id", str(uuid.uuid4()))
        self.secret_key = config.get("secret_key", "default_secret")
        self.cloud_endpoint = config.get("cloud_endpoint", "wss://api.powerauto.ai/ws")
        
        # 初始化組件
        self.protocol = EdgeCloudProtocol(self.edge_id, self.secret_key)
        self.sync_status = SyncStatus.DISCONNECTED
        self.websocket = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        # 本地數據庫
        self.db_path = config.get("db_path", "edge_admin.db")
        self._init_database()
        
        # 統計數據
        self.statistics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "tokens_saved": 0,
            "cloud_tokens_used": 0,
            "edge_processing_ratio": 0.0,
            "last_sync_time": None,
            "uptime_start": datetime.now()
        }
        
        # 事件回調
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
    def _init_database(self):
        """初始化本地數據庫"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_logs (
                    log_id TEXT PRIMARY KEY,
                    message_type TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    credit_balance REAL NOT NULL,
                    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS service_cache (
                    cache_key TEXT PRIMARY KEY,
                    service_type TEXT NOT NULL,
                    request_hash TEXT NOT NULL,
                    response_data TEXT NOT NULL,
                    tokens_saved INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            
            conn.commit()
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """註冊事件回調"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def emit_event(self, event_type: str, data: Any):
        """觸發事件"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"事件回調執行失敗: {e}")
    
    async def start(self):
        """啟動端Admin"""
        logger.info(f"啟動端Admin - Edge ID: {self.edge_id}")
        
        # 啟動後台任務
        tasks = [
            asyncio.create_task(self._connect_to_cloud()),
            asyncio.create_task(self._heartbeat_loop()),
            asyncio.create_task(self._statistics_update_loop()),
            asyncio.create_task(self._cache_cleanup_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"端Admin運行錯誤: {e}")
            self.emit_event("error", {"error": str(e)})
    
    async def _connect_to_cloud(self):
        """連接到雲Admin"""
        while True:
            try:
                logger.info(f"嘗試連接雲Admin: {self.cloud_endpoint}")
                
                # 創建SSL上下文
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                
                # 建立WebSocket連接
                self.websocket = await websockets.connect(
                    self.cloud_endpoint,
                    ssl=ssl_context,
                    extra_headers={
                        "X-Edge-ID": self.edge_id,
                        "X-Protocol-Version": self.protocol.protocol_version
                    }
                )
                
                self.sync_status = SyncStatus.CONNECTED
                self.reconnect_attempts = 0
                logger.info("成功連接到雲Admin")
                self.emit_event("connected", {"endpoint": self.cloud_endpoint})
                
                # 發送認證消息
                auth_message = self.protocol.create_message(
                    MessageType.USER_AUTH,
                    {
                        "edge_id": self.edge_id,
                        "protocol_version": self.protocol.protocol_version,
                        "capabilities": ["credit_sync", "service_request", "statistics"]
                    }
                )
                await self._send_message(auth_message)
                
                # 監聽消息
                await self._listen_messages()
                
            except Exception as e:
                logger.error(f"連接雲Admin失敗: {e}")
                self.sync_status = SyncStatus.ERROR
                self.reconnect_attempts += 1
                
                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error("達到最大重連次數，停止重連")
                    break
                
                # 指數退避重連
                wait_time = min(300, 2 ** self.reconnect_attempts)
                logger.info(f"等待 {wait_time} 秒後重連...")
                await asyncio.sleep(wait_time)
    
    async def _listen_messages(self):
        """監聽雲Admin消息"""
        try:
            async for message_data in self.websocket:
                try:
                    message_dict = json.loads(message_data)
                    message = SyncMessage(**message_dict)
                    
                    # 驗證消息簽名
                    if not self.protocol.verify_message(message):
                        logger.warning(f"消息簽名驗證失敗: {message.message_id}")
                        continue
                    
                    # 處理消息
                    await self._handle_message(message)
                    
                except json.JSONDecodeError:
                    logger.error("收到無效JSON消息")
                except Exception as e:
                    logger.error(f"處理消息失敗: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket連接已關閉")
            self.sync_status = SyncStatus.DISCONNECTED
        except Exception as e:
            logger.error(f"監聽消息失敗: {e}")
            self.sync_status = SyncStatus.ERROR
    
    async def _handle_message(self, message: SyncMessage):
        """處理收到的消息"""
        logger.info(f"收到消息: {message.message_type.value}")
        
        if message.message_type == MessageType.CREDIT_SYNC:
            await self._handle_credit_sync(message)
        elif message.message_type == MessageType.SERVICE_RESPONSE:
            await self._handle_service_response(message)
        elif message.message_type == MessageType.CONFIG_UPDATE:
            await self._handle_config_update(message)
        elif message.message_type == MessageType.HEARTBEAT:
            await self._handle_heartbeat(message)
        else:
            logger.warning(f"未知消息類型: {message.message_type.value}")
    
    async def _handle_credit_sync(self, message: SyncMessage):
        """處理積分同步"""
        try:
            user_id = message.payload.get("user_id")
            credit_balance = message.payload.get("credit_balance")
            
            if user_id and credit_balance is not None:
                # 更新本地用戶會話
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """INSERT OR REPLACE INTO user_sessions 
                           (session_id, user_id, credit_balance, last_sync)
                           VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                        (str(uuid.uuid4()), user_id, credit_balance)
                    )
                    conn.commit()
                
                logger.info(f"用戶 {user_id} 積分同步完成: {credit_balance}")
                self.emit_event("credit_synced", {
                    "user_id": user_id,
                    "balance": credit_balance
                })
                
        except Exception as e:
            logger.error(f"處理積分同步失敗: {e}")
    
    async def _handle_service_response(self, message: SyncMessage):
        """處理服務響應"""
        try:
            request_id = message.payload.get("request_id")
            response_data = message.payload.get("response_data")
            tokens_used = message.payload.get("tokens_used", 0)
            
            # 更新統計
            self.statistics["cloud_tokens_used"] += tokens_used
            self.statistics["successful_requests"] += 1
            
            self.emit_event("service_response", {
                "request_id": request_id,
                "response": response_data,
                "tokens_used": tokens_used
            })
            
        except Exception as e:
            logger.error(f"處理服務響應失敗: {e}")
    
    async def _handle_config_update(self, message: SyncMessage):
        """處理配置更新"""
        try:
            new_config = message.payload.get("config", {})
            
            # 更新本地配置
            self.config.update(new_config)
            
            logger.info("配置更新完成")
            self.emit_event("config_updated", new_config)
            
        except Exception as e:
            logger.error(f"處理配置更新失敗: {e}")
    
    async def _handle_heartbeat(self, message: SyncMessage):
        """處理心跳"""
        # 回應心跳
        response = self.protocol.create_message(
            MessageType.HEARTBEAT,
            {
                "status": self.sync_status.value,
                "statistics": self.statistics,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self._send_message(response)
    
    async def _send_message(self, message: SyncMessage):
        """發送消息到雲Admin"""
        if not self.websocket or self.sync_status != SyncStatus.CONNECTED:
            logger.warning("WebSocket未連接，無法發送消息")
            return False
        
        try:
            message_data = json.dumps(asdict(message), default=str)
            await self.websocket.send(message_data)
            
            # 記錄同步日誌
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO sync_logs 
                       (log_id, message_type, direction, payload, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        message.message_id,
                        message.message_type.value,
                        "outbound",
                        json.dumps(message.payload),
                        "sent"
                    )
                )
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"發送消息失敗: {e}")
            return False
    
    async def _heartbeat_loop(self):
        """心跳循環"""
        while True:
            try:
                if self.sync_status == SyncStatus.CONNECTED:
                    heartbeat = self.protocol.create_message(
                        MessageType.HEARTBEAT,
                        {
                            "edge_id": self.edge_id,
                            "status": "alive",
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    await self._send_message(heartbeat)
                
                await asyncio.sleep(30)  # 每30秒發送心跳
                
            except Exception as e:
                logger.error(f"心跳循環錯誤: {e}")
                await asyncio.sleep(30)
    
    async def _statistics_update_loop(self):
        """統計更新循環"""
        while True:
            try:
                # 計算端側處理比例
                total_requests = self.statistics["total_requests"]
                if total_requests > 0:
                    edge_requests = total_requests - self.statistics["cloud_tokens_used"] / 1000
                    self.statistics["edge_processing_ratio"] = edge_requests / total_requests
                
                # 更新最後同步時間
                self.statistics["last_sync_time"] = datetime.now().isoformat()
                
                await asyncio.sleep(60)  # 每分鐘更新統計
                
            except Exception as e:
                logger.error(f"統計更新錯誤: {e}")
                await asyncio.sleep(60)
    
    async def _cache_cleanup_loop(self):
        """緩存清理循環"""
        while True:
            try:
                # 清理過期緩存
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "DELETE FROM service_cache WHERE expires_at < ?",
                        (datetime.now(),)
                    )
                    conn.commit()
                
                await asyncio.sleep(3600)  # 每小時清理一次
                
            except Exception as e:
                logger.error(f"緩存清理錯誤: {e}")
                await asyncio.sleep(3600)
    
    async def request_service(self, service_type: str, request_data: Dict[str, Any], 
                            user_id: str) -> Dict[str, Any]:
        """請求服務"""
        try:
            # 檢查本地緩存
            cache_key = self._generate_cache_key(service_type, request_data)
            cached_response = self._get_cached_response(cache_key)
            
            if cached_response:
                logger.info(f"使用緩存響應: {cache_key}")
                self.statistics["tokens_saved"] += cached_response.get("tokens_saved", 0)
                return cached_response
            
            # 發送服務請求到雲Admin
            request_id = str(uuid.uuid4())
            service_request = self.protocol.create_message(
                MessageType.SERVICE_REQUEST,
                {
                    "request_id": request_id,
                    "user_id": user_id,
                    "service_type": service_type,
                    "request_data": request_data,
                    "edge_id": self.edge_id
                }
            )
            
            success = await self._send_message(service_request)
            if success:
                self.statistics["total_requests"] += 1
                return {
                    "success": True,
                    "request_id": request_id,
                    "status": "processing"
                }
            else:
                self.statistics["failed_requests"] += 1
                return {
                    "success": False,
                    "error": "無法發送請求到雲Admin"
                }
                
        except Exception as e:
            logger.error(f"請求服務失敗: {e}")
            self.statistics["failed_requests"] += 1
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_cache_key(self, service_type: str, request_data: Dict[str, Any]) -> str:
        """生成緩存鍵"""
        data_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(f"{service_type}:{data_str}".encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """獲取緩存響應"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """SELECT response_data, tokens_saved FROM service_cache 
                       WHERE cache_key = ? AND expires_at > ?""",
                    (cache_key, datetime.now())
                )
                result = cursor.fetchone()
                
                if result:
                    response_data = json.loads(result[0])
                    response_data["tokens_saved"] = result[1]
                    response_data["from_cache"] = True
                    return response_data
                    
        except Exception as e:
            logger.error(f"獲取緩存失敗: {e}")
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        uptime = datetime.now() - self.statistics["uptime_start"]
        
        return {
            **self.statistics,
            "sync_status": self.sync_status.value,
            "edge_id": self.edge_id,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime).split('.')[0]
        }
    
    async def sync_user_credits(self, user_id: str) -> Dict[str, Any]:
        """同步用戶積分"""
        try:
            sync_request = self.protocol.create_message(
                MessageType.CREDIT_SYNC,
                {
                    "user_id": user_id,
                    "action": "get_balance",
                    "edge_id": self.edge_id
                }
            )
            
            success = await self._send_message(sync_request)
            if success:
                return {
                    "success": True,
                    "message": "積分同步請求已發送"
                }
            else:
                return {
                    "success": False,
                    "error": "無法發送同步請求"
                }
                
        except Exception as e:
            logger.error(f"同步用戶積分失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# 使用示例
async def main():
    """主函數示例"""
    config = {
        "edge_id": "edge_001",
        "secret_key": "your_secret_key_here",
        "cloud_endpoint": "wss://api.powerauto.ai/ws",
        "db_path": "edge_admin.db"
    }
    
    edge_admin = EdgeAdminCore(config)
    
    # 註冊事件回調
    edge_admin.register_event_callback("connected", lambda data: print(f"已連接: {data}"))
    edge_admin.register_event_callback("credit_synced", lambda data: print(f"積分同步: {data}"))
    
    print("=== PowerAutomation 端雲協同系統啟動 ===")
    
    # 啟動端Admin
    await edge_admin.start()

if __name__ == "__main__":
    asyncio.run(main())

