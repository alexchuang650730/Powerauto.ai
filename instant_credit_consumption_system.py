#!/usr/bin/env python3
"""
PowerAutomation 即時積分消費系統
實現用戶充值後立即可消費積分的完整機制
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
import sqlite3
import threading
import hashlib
import hmac
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CreditConsumptionSystem")

class TransactionType(Enum):
    """交易類型"""
    RECHARGE = "recharge"           # 充值
    CONSUMPTION = "consumption"     # 消費
    REFUND = "refund"              # 退款
    BONUS = "bonus"                # 獎勵
    TRANSFER = "transfer"          # 轉帳

class TransactionStatus(Enum):
    """交易狀態"""
    PENDING = "pending"            # 待處理
    COMPLETED = "completed"        # 已完成
    FAILED = "failed"             # 失敗
    CANCELLED = "cancelled"       # 已取消

@dataclass
class CreditTransaction:
    """積分交易記錄"""
    transaction_id: str
    user_id: str
    transaction_type: TransactionType
    amount: float
    balance_before: float
    balance_after: float
    status: TransactionStatus
    description: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
class CreditDatabase:
    """積分數據庫管理"""
    
    def __init__(self, db_path: str = "credits.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """初始化數據庫"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    credit_balance REAL DEFAULT 0.0,
                    total_recharged REAL DEFAULT 0.0,
                    total_consumed REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    balance_before REAL NOT NULL,
                    balance_after REAL NOT NULL,
                    status TEXT NOT NULL,
                    description TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consumption_logs (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    credits_cost REAL NOT NULL,
                    edge_tokens_saved INTEGER DEFAULT 0,
                    cloud_tokens_used INTEGER DEFAULT 0,
                    efficiency_ratio REAL DEFAULT 0.0,
                    request_data TEXT,
                    response_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()
    
    def get_user_balance(self, user_id: str) -> float:
        """獲取用戶積分餘額"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT credit_balance FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0.0
    
    def create_user(self, user_id: str, username: str, email: str) -> bool:
        """創建用戶"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO users (user_id, username, email) 
                       VALUES (?, ?, ?)""",
                    (user_id, username, email)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def update_balance(self, user_id: str, new_balance: float) -> bool:
        """更新用戶餘額"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """UPDATE users SET credit_balance = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE user_id = ?""",
                (new_balance, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def add_transaction(self, transaction: CreditTransaction) -> bool:
        """添加交易記錄"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO transactions 
                       (transaction_id, user_id, transaction_type, amount, 
                        balance_before, balance_after, status, description, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        transaction.transaction_id,
                        transaction.user_id,
                        transaction.transaction_type.value,
                        transaction.amount,
                        transaction.balance_before,
                        transaction.balance_after,
                        transaction.status.value,
                        transaction.description,
                        json.dumps(transaction.metadata)
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"添加交易記錄失敗: {e}")
            return False
    
    def get_transactions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """獲取用戶交易記錄"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT * FROM transactions WHERE user_id = ? 
                   ORDER BY created_at DESC LIMIT ?""",
                (user_id, limit)
            )
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def add_consumption_log(self, log_data: Dict[str, Any]) -> bool:
        """添加消費日誌"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO consumption_logs 
                       (log_id, user_id, service_type, tokens_used, credits_cost,
                        edge_tokens_saved, cloud_tokens_used, efficiency_ratio,
                        request_data, response_data)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        log_data.get("log_id", str(uuid.uuid4())),
                        log_data["user_id"],
                        log_data["service_type"],
                        log_data["tokens_used"],
                        log_data["credits_cost"],
                        log_data.get("edge_tokens_saved", 0),
                        log_data.get("cloud_tokens_used", 0),
                        log_data.get("efficiency_ratio", 0.0),
                        json.dumps(log_data.get("request_data", {})),
                        json.dumps(log_data.get("response_data", {}))
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"添加消費日誌失敗: {e}")
            return False

class CreditManager:
    """積分管理器"""
    
    def __init__(self, db_path: str = "credits.db"):
        self.db = CreditDatabase(db_path)
        self.lock = threading.Lock()
        
        # 積分消費規則配置
        self.consumption_rules = {
            "ai_chat": {"rate": 0.001, "description": "AI對話服務"},
            "code_generation": {"rate": 0.005, "description": "代碼生成服務"},
            "data_analysis": {"rate": 0.003, "description": "數據分析服務"},
            "workflow_automation": {"rate": 0.002, "description": "工作流自動化"},
            "enterprise_features": {"rate": 0.01, "description": "企業級功能"},
            "api_calls": {"rate": 0.0001, "description": "API調用"}
        }
        
        # 端雲協同效率配置
        self.edge_cloud_efficiency = {
            "cache_hit_ratio": 0.3,      # 緩存命中率
            "edge_processing_ratio": 0.6, # 端側處理比例
            "token_saving_ratio": 0.4     # token節省比例
        }
    
    async def recharge_credits(self, user_id: str, amount: float, 
                              payment_method: str = "unknown") -> Dict[str, Any]:
        """充值積分"""
        with self.lock:
            try:
                # 獲取當前餘額
                current_balance = self.db.get_user_balance(user_id)
                new_balance = current_balance + amount
                
                # 創建交易記錄
                transaction = CreditTransaction(
                    transaction_id=str(uuid.uuid4()),
                    user_id=user_id,
                    transaction_type=TransactionType.RECHARGE,
                    amount=amount,
                    balance_before=current_balance,
                    balance_after=new_balance,
                    status=TransactionStatus.COMPLETED,
                    description=f"充值積分 - {payment_method}",
                    metadata={"payment_method": payment_method},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # 更新餘額和記錄交易
                if self.db.update_balance(user_id, new_balance):
                    self.db.add_transaction(transaction)
                    
                    logger.info(f"用戶 {user_id} 充值成功: {amount} 積分")
                    return {
                        "success": True,
                        "transaction_id": transaction.transaction_id,
                        "balance_before": current_balance,
                        "balance_after": new_balance,
                        "amount": amount
                    }
                else:
                    return {"success": False, "error": "更新餘額失敗"}
                    
            except Exception as e:
                logger.error(f"充值失敗: {e}")
                return {"success": False, "error": str(e)}
    
    async def consume_credits(self, user_id: str, service_type: str, 
                             tokens_used: int, request_data: Dict = None) -> Dict[str, Any]:
        """消費積分"""
        with self.lock:
            try:
                # 檢查服務類型
                if service_type not in self.consumption_rules:
                    return {"success": False, "error": "未知服務類型"}
                
                # 計算消費金額
                rate = self.consumption_rules[service_type]["rate"]
                base_cost = tokens_used * rate
                
                # 計算端雲協同節省
                edge_savings = self._calculate_edge_savings(tokens_used, service_type)
                actual_cost = base_cost - edge_savings["credits_saved"]
                
                # 檢查餘額
                current_balance = self.db.get_user_balance(user_id)
                if current_balance < actual_cost:
                    return {
                        "success": False, 
                        "error": "積分不足",
                        "required": actual_cost,
                        "available": current_balance
                    }
                
                # 執行消費
                new_balance = current_balance - actual_cost
                
                # 創建交易記錄
                transaction = CreditTransaction(
                    transaction_id=str(uuid.uuid4()),
                    user_id=user_id,
                    transaction_type=TransactionType.CONSUMPTION,
                    amount=actual_cost,
                    balance_before=current_balance,
                    balance_after=new_balance,
                    status=TransactionStatus.COMPLETED,
                    description=f"消費積分 - {self.consumption_rules[service_type]['description']}",
                    metadata={
                        "service_type": service_type,
                        "tokens_used": tokens_used,
                        "base_cost": base_cost,
                        "edge_savings": edge_savings,
                        "actual_cost": actual_cost
                    },
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # 更新餘額和記錄
                if self.db.update_balance(user_id, new_balance):
                    self.db.add_transaction(transaction)
                    
                    # 記錄消費日誌
                    consumption_log = {
                        "log_id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "service_type": service_type,
                        "tokens_used": tokens_used,
                        "credits_cost": actual_cost,
                        "edge_tokens_saved": edge_savings["tokens_saved"],
                        "cloud_tokens_used": tokens_used - edge_savings["tokens_saved"],
                        "efficiency_ratio": edge_savings["efficiency_ratio"],
                        "request_data": request_data or {},
                        "response_data": {"transaction_id": transaction.transaction_id}
                    }
                    self.db.add_consumption_log(consumption_log)
                    
                    logger.info(f"用戶 {user_id} 消費成功: {actual_cost} 積分")
                    return {
                        "success": True,
                        "transaction_id": transaction.transaction_id,
                        "balance_before": current_balance,
                        "balance_after": new_balance,
                        "cost": actual_cost,
                        "base_cost": base_cost,
                        "savings": edge_savings
                    }
                else:
                    return {"success": False, "error": "更新餘額失敗"}
                    
            except Exception as e:
                logger.error(f"消費失敗: {e}")
                return {"success": False, "error": str(e)}
    
    def _calculate_edge_savings(self, tokens_used: int, service_type: str) -> Dict[str, Any]:
        """計算端雲協同節省"""
        # 基於服務類型和配置計算節省
        cache_hit = self.edge_cloud_efficiency["cache_hit_ratio"]
        edge_ratio = self.edge_cloud_efficiency["edge_processing_ratio"]
        saving_ratio = self.edge_cloud_efficiency["token_saving_ratio"]
        
        # 計算實際節省的token數量
        tokens_saved = int(tokens_used * edge_ratio * saving_ratio)
        
        # 計算節省的積分
        rate = self.consumption_rules[service_type]["rate"]
        credits_saved = tokens_saved * rate
        
        # 計算效率比例
        efficiency_ratio = tokens_saved / tokens_used if tokens_used > 0 else 0
        
        return {
            "tokens_saved": tokens_saved,
            "credits_saved": credits_saved,
            "efficiency_ratio": efficiency_ratio,
            "edge_processing": True,
            "cache_utilized": cache_hit > 0.2
        }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """獲取用戶統計信息"""
        try:
            balance = self.db.get_user_balance(user_id)
            transactions = self.db.get_transactions(user_id, 10)
            
            # 計算統計數據
            total_recharged = sum(
                t["amount"] for t in transactions 
                if t["transaction_type"] == "recharge"
            )
            total_consumed = sum(
                t["amount"] for t in transactions 
                if t["transaction_type"] == "consumption"
            )
            
            return {
                "user_id": user_id,
                "current_balance": balance,
                "total_recharged": total_recharged,
                "total_consumed": total_consumed,
                "recent_transactions": transactions[:5],
                "account_status": "active" if balance > 0 else "low_balance"
            }
        except Exception as e:
            logger.error(f"獲取用戶統計失敗: {e}")
            return {"error": str(e)}

class CreditAPI:
    """積分API服務"""
    
    def __init__(self, credit_manager: CreditManager):
        self.credit_manager = credit_manager
        self.api_keys = {}  # API密鑰管理
    
    def generate_api_key(self, user_id: str) -> str:
        """生成API密鑰"""
        api_key = hashlib.sha256(f"{user_id}_{time.time()}".encode()).hexdigest()
        self.api_keys[api_key] = user_id
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """驗證API密鑰"""
        return self.api_keys.get(api_key)
    
    async def handle_recharge_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理充值請求"""
        try:
            user_id = request_data["user_id"]
            amount = float(request_data["amount"])
            payment_method = request_data.get("payment_method", "unknown")
            
            if amount <= 0:
                return {"success": False, "error": "充值金額必須大於0"}
            
            result = await self.credit_manager.recharge_credits(
                user_id, amount, payment_method
            )
            return result
            
        except Exception as e:
            return {"success": False, "error": f"請求處理失敗: {e}"}
    
    async def handle_consumption_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理消費請求"""
        try:
            user_id = request_data["user_id"]
            service_type = request_data["service_type"]
            tokens_used = int(request_data["tokens_used"])
            
            if tokens_used <= 0:
                return {"success": False, "error": "token使用量必須大於0"}
            
            result = await self.credit_manager.consume_credits(
                user_id, service_type, tokens_used, request_data
            )
            return result
            
        except Exception as e:
            return {"success": False, "error": f"請求處理失敗: {e}"}
    
    def handle_balance_query(self, user_id: str) -> Dict[str, Any]:
        """處理餘額查詢"""
        try:
            stats = self.credit_manager.get_user_stats(user_id)
            return {"success": True, "data": stats}
        except Exception as e:
            return {"success": False, "error": f"查詢失敗: {e}"}

# 使用示例
async def main():
    """主函數示例"""
    # 初始化系統
    credit_manager = CreditManager()
    credit_api = CreditAPI(credit_manager)
    
    # 創建測試用戶
    user_id = "test_user_001"
    credit_manager.db.create_user(user_id, "testuser", "test@example.com")
    
    print("=== PowerAutomation 即時積分消費系統測試 ===")
    
    # 測試充值
    print("\n1. 測試充值功能")
    recharge_result = await credit_manager.recharge_credits(user_id, 100.0, "credit_card")
    print(f"充值結果: {recharge_result}")
    
    # 測試消費
    print("\n2. 測試消費功能")
    consumption_result = await credit_manager.consume_credits(
        user_id, "ai_chat", 1000, {"query": "測試AI對話"}
    )
    print(f"消費結果: {consumption_result}")
    
    # 查詢用戶統計
    print("\n3. 用戶統計信息")
    stats = credit_manager.get_user_stats(user_id)
    print(f"用戶統計: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 測試不足餘額的情況
    print("\n4. 測試餘額不足")
    large_consumption = await credit_manager.consume_credits(
        user_id, "enterprise_features", 50000
    )
    print(f"大額消費結果: {large_consumption}")

if __name__ == "__main__":
    asyncio.run(main())

