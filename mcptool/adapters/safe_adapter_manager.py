#!/usr/bin/env python3
"""
安全的MCP適配器管理器
解決循環依賴和初始化問題，提供穩定的適配器註冊和管理功能
"""

import asyncio
import logging
import threading
import traceback
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import json

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AdapterInfo:
    """適配器信息"""
    name: str
    id: str
    category: str
    status: str
    description: str
    capabilities: List[str]
    dependencies: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "category": self.category,
            "status": self.status,
            "description": self.description,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies or []
        }

class AdapterStatus(Enum):
    """適配器狀態"""
    AVAILABLE = "available"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"

class SafeAdapterManager:
    """安全的適配器管理器"""
    
    def __init__(self):
        self._adapters: Dict[str, AdapterInfo] = {}
        self._loaded_adapters: Dict[str, Any] = {}
        self._loading_stack: Set[str] = set()
        self._lock = threading.Lock()
        self._event_loop = None
        self._initialize_core_adapters()
    
    def _initialize_core_adapters(self):
        """初始化核心適配器信息"""
        core_adapters = [
            AdapterInfo(
                name="WebAgent Core",
                id="webagent_core",
                category="web",
                status=AdapterStatus.AVAILABLE.value,
                description="網頁操作和自動化核心引擎",
                capabilities=["web_browsing", "form_filling", "data_extraction"]
            ),
            AdapterInfo(
                name="Claude Adapter",
                id="claude_adapter",
                category="ai",
                status=AdapterStatus.AVAILABLE.value,
                description="Claude AI模型適配器",
                capabilities=["text_generation", "analysis", "reasoning"]
            ),
            AdapterInfo(
                name="Gemini Adapter",
                id="gemini_adapter",
                category="ai",
                status=AdapterStatus.AVAILABLE.value,
                description="Google Gemini AI模型適配器",
                capabilities=["text_generation", "multimodal", "analysis"]
            ),
            AdapterInfo(
                name="ArXiv Integration",
                id="arxiv_integration",
                category="research",
                status=AdapterStatus.AVAILABLE.value,
                description="ArXiv學術論文搜索和分析",
                capabilities=["paper_search", "academic_analysis"]
            ),
            AdapterInfo(
                name="Context Monitor",
                id="context_monitor",
                category="monitoring",
                status=AdapterStatus.AVAILABLE.value,
                description="上下文監控和管理",
                capabilities=["context_tracking", "memory_management"]
            ),
            AdapterInfo(
                name="Enhanced Fallback v3",
                id="enhanced_fallback_v3",
                category="fallback",
                status=AdapterStatus.AVAILABLE.value,
                description="增強的兜底機制v3",
                capabilities=["fallback_handling", "error_recovery"]
            )
        ]
        
        for adapter in core_adapters:
            self._adapters[adapter.id] = adapter
    
    def list_adapters(self, category: Optional[str] = None, status: Optional[str] = None) -> List[AdapterInfo]:
        """列出適配器"""
        with self._lock:
            adapters = list(self._adapters.values())
            
            if category:
                adapters = [a for a in adapters if a.category == category]
            
            if status:
                adapters = [a for a in adapters if a.status == status]
            
            return adapters
    
    def get_adapter_info(self, adapter_id: str) -> Optional[AdapterInfo]:
        """獲取適配器信息"""
        with self._lock:
            return self._adapters.get(adapter_id)
    
    def is_adapter_loaded(self, adapter_id: str) -> bool:
        """檢查適配器是否已加載"""
        with self._lock:
            return adapter_id in self._loaded_adapters
    
    def load_adapter(self, adapter_id: str) -> bool:
        """安全加載適配器"""
        with self._lock:
            # 檢查是否已加載
            if adapter_id in self._loaded_adapters:
                logger.info(f"適配器 {adapter_id} 已經加載")
                return True
            
            # 檢查是否在加載中（防止循環依賴）
            if adapter_id in self._loading_stack:
                logger.error(f"檢測到循環依賴: {adapter_id} 正在加載中")
                return False
            
            # 檢查適配器是否存在
            if adapter_id not in self._adapters:
                logger.error(f"適配器 {adapter_id} 不存在")
                return False
            
            adapter_info = self._adapters[adapter_id]
            
            try:
                # 標記為加載中
                self._loading_stack.add(adapter_id)
                adapter_info.status = AdapterStatus.LOADING.value
                
                logger.info(f"開始加載適配器: {adapter_id}")
                
                # 模擬適配器加載（實際實現中會導入真實的適配器類）
                loaded_adapter = self._create_mock_adapter(adapter_info)
                
                # 加載成功
                self._loaded_adapters[adapter_id] = loaded_adapter
                adapter_info.status = AdapterStatus.LOADED.value
                
                logger.info(f"適配器 {adapter_id} 加載成功")
                return True
                
            except Exception as e:
                logger.error(f"加載適配器 {adapter_id} 失敗: {str(e)}")
                adapter_info.status = AdapterStatus.ERROR.value
                return False
            
            finally:
                # 清理加載標記
                self._loading_stack.discard(adapter_id)
    
    def _create_mock_adapter(self, adapter_info: AdapterInfo) -> Dict[str, Any]:
        """創建模擬適配器（用於測試）"""
        return {
            "id": adapter_info.id,
            "name": adapter_info.name,
            "capabilities": adapter_info.capabilities,
            "status": "loaded",
            "mock": True
        }
    
    def unload_adapter(self, adapter_id: str) -> bool:
        """卸載適配器"""
        with self._lock:
            if adapter_id not in self._loaded_adapters:
                logger.warning(f"適配器 {adapter_id} 未加載")
                return False
            
            try:
                # 執行清理操作
                del self._loaded_adapters[adapter_id]
                
                if adapter_id in self._adapters:
                    self._adapters[adapter_id].status = AdapterStatus.AVAILABLE.value
                
                logger.info(f"適配器 {adapter_id} 卸載成功")
                return True
                
            except Exception as e:
                logger.error(f"卸載適配器 {adapter_id} 失敗: {str(e)}")
                return False
    
    def get_loaded_adapters(self) -> Dict[str, Any]:
        """獲取已加載的適配器"""
        with self._lock:
            return self._loaded_adapters.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        with self._lock:
            total_adapters = len(self._adapters)
            loaded_adapters = len(self._loaded_adapters)
            loading_adapters = len(self._loading_stack)
            
            status_counts = {}
            for adapter in self._adapters.values():
                status = adapter.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total_adapters": total_adapters,
                "loaded_adapters": loaded_adapters,
                "loading_adapters": loading_adapters,
                "status_counts": status_counts,
                "loading_stack": list(self._loading_stack),
                "event_loop_running": self._event_loop is not None
            }
    
    def register_adapter(self, adapter_info: AdapterInfo) -> bool:
        """註冊新適配器"""
        with self._lock:
            if adapter_info.id in self._adapters:
                logger.warning(f"適配器 {adapter_info.id} 已存在")
                return False
            
            self._adapters[adapter_info.id] = adapter_info
            logger.info(f"適配器 {adapter_info.id} 註冊成功")
            return True
    
    def unregister_adapter(self, adapter_id: str) -> bool:
        """取消註冊適配器"""
        with self._lock:
            if adapter_id not in self._adapters:
                logger.warning(f"適配器 {adapter_id} 不存在")
                return False
            
            # 先卸載
            if adapter_id in self._loaded_adapters:
                self.unload_adapter(adapter_id)
            
            # 取消註冊
            del self._adapters[adapter_id]
            logger.info(f"適配器 {adapter_id} 取消註冊成功")
            return True
    
    def export_config(self) -> str:
        """導出配置"""
        with self._lock:
            config = {
                "adapters": [adapter.to_dict() for adapter in self._adapters.values()],
                "system_status": self.get_system_status()
            }
            return json.dumps(config, indent=2, ensure_ascii=False)

# 全局實例
_safe_adapter_manager = None
_manager_lock = threading.Lock()

def get_safe_adapter_manager() -> SafeAdapterManager:
    """獲取安全適配器管理器的全局實例"""
    global _safe_adapter_manager
    
    if _safe_adapter_manager is None:
        with _manager_lock:
            if _safe_adapter_manager is None:
                _safe_adapter_manager = SafeAdapterManager()
    
    return _safe_adapter_manager

if __name__ == "__main__":
    # 測試代碼
    manager = get_safe_adapter_manager()
    
    print("🔍 安全適配器管理器測試")
    print("=" * 50)
    
    # 列出所有適配器
    adapters = manager.list_adapters()
    print(f"📋 可用適配器數量: {len(adapters)}")
    
    for adapter in adapters:
        print(f"  - {adapter.name} ({adapter.id}) - {adapter.status}")
    
    print("\n🔧 測試適配器加載")
    print("-" * 30)
    
    # 測試加載適配器
    test_adapters = ["webagent_core", "claude_adapter", "gemini_adapter"]
    
    for adapter_id in test_adapters:
        success = manager.load_adapter(adapter_id)
        print(f"  {adapter_id}: {'✅ 成功' if success else '❌ 失敗'}")
    
    print("\n📊 系統狀態")
    print("-" * 20)
    status = manager.get_system_status()
    print(f"  總適配器: {status['total_adapters']}")
    print(f"  已加載: {status['loaded_adapters']}")
    print(f"  加載中: {status['loading_adapters']}")
    
    print("\n✅ 測試完成")

