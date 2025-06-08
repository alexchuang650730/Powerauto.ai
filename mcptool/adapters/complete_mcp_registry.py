#!/usr/bin/env python3
"""
完整MCP適配器註冊表
基於實際存在的MCP適配器文件創建完整的適配器清單
"""

import asyncio
import logging
import threading
import traceback
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import json
import importlib
import sys
from pathlib import Path

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPAdapterInfo:
    """MCP適配器信息"""
    name: str
    id: str
    file_path: str
    category: str
    status: str
    description: str
    capabilities: List[str]
    dependencies: List[str] = None
    priority: int = 5  # 1-10, 10為最高優先級
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "file_path": self.file_path,
            "category": self.category,
            "status": self.status,
            "description": self.description,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies or [],
            "priority": self.priority
        }

class AdapterStatus(Enum):
    """適配器狀態"""
    AVAILABLE = "available"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"

class CompleteMCPAdapterRegistry:
    """完整MCP適配器註冊表"""
    
    def __init__(self):
        self._adapters: Dict[str, MCPAdapterInfo] = {}
        self._loaded_adapters: Dict[str, Any] = {}
        self._loading_stack: Set[str] = set()
        self._lock = threading.Lock()
        self._initialize_real_adapters()
    
    def _initialize_real_adapters(self):
        """初始化真實存在的MCP適配器"""
        
        # AI核心適配器
        ai_adapters = [
            MCPAdapterInfo(
                name="Claude MCP",
                id="claude_mcp",
                file_path="mcptool/adapters/claude_adapter/claude_mcp.py",
                category="ai_core",
                status=AdapterStatus.AVAILABLE.value,
                description="Claude AI模型集成適配器，提供高質量文本生成和推理能力",
                capabilities=["text_generation", "reasoning", "analysis", "conversation"],
                priority=9
            ),
            MCPAdapterInfo(
                name="Gemini MCP",
                id="gemini_mcp",
                file_path="mcptool/adapters/gemini_adapter/gemini_mcp.py",
                category="ai_core",
                status=AdapterStatus.AVAILABLE.value,
                description="Google Gemini AI模型適配器，支持多模態處理",
                capabilities=["text_generation", "multimodal", "analysis", "vision"],
                priority=9
            ),
            MCPAdapterInfo(
                name="Qwen3 8B Local MCP",
                id="qwen3_8b_local_mcp",
                file_path="mcptool/adapters/qwen3_8b_local_mcp.py",
                category="ai_core",
                status=AdapterStatus.AVAILABLE.value,
                description="本地Qwen3 8B模型適配器，提供離線AI能力",
                capabilities=["text_generation", "local_processing", "privacy_safe"],
                priority=7
            )
        ]
        
        # 核心工具適配器
        tool_adapters = [
            MCPAdapterInfo(
                name="KiloCode MCP",
                id="kilocode_mcp",
                file_path="mcptool/adapters/kilocode_adapter/kilocode_mcp.py",
                category="tool_core",
                status=AdapterStatus.AVAILABLE.value,
                description="動態代碼生成和執行引擎，支持實時代碼創建和優化",
                capabilities=["code_generation", "code_execution", "dynamic_tools", "optimization"],
                priority=10
            ),
            MCPAdapterInfo(
                name="RL-SRT MCP",
                id="rl_srt_mcp",
                file_path="mcptool/adapters/rl_srt/rl_srt_mcp.py",
                category="tool_core",
                status=AdapterStatus.AVAILABLE.value,
                description="強化學習與自我獎勵訓練系統，提供持續學習和改進能力",
                capabilities=["reinforcement_learning", "self_reward", "continuous_improvement", "adaptation"],
                priority=10
            ),
            MCPAdapterInfo(
                name="RL-SRT DataFlow MCP",
                id="rl_srt_dataflow_mcp",
                file_path="mcptool/adapters/rl_srt_dataflow_mcp.py",
                category="tool_core",
                status=AdapterStatus.AVAILABLE.value,
                description="RL數據流處理器，管理強化學習的數據流和處理管道",
                capabilities=["data_flow", "rl_pipeline", "stream_processing"],
                priority=8
            )
        ]
        
        # 智能引擎適配器
        engine_adapters = [
            MCPAdapterInfo(
                name="Intelligent Workflow Engine MCP",
                id="intelligent_workflow_engine_mcp",
                file_path="mcptool/adapters/intelligent_workflow_engine_mcp.py",
                category="intelligent_engine",
                status=AdapterStatus.AVAILABLE.value,
                description="智能工作流引擎，自動化複雜任務流程",
                capabilities=["workflow_automation", "task_orchestration", "intelligent_routing"],
                priority=9
            ),
            MCPAdapterInfo(
                name="Smart Routing MCP",
                id="smart_routing_mcp",
                file_path="mcptool/adapters/smart_routing_mcp.py",
                category="intelligent_engine",
                status=AdapterStatus.AVAILABLE.value,
                description="智能路由系統，動態選擇最佳處理路徑",
                capabilities=["smart_routing", "path_optimization", "load_balancing"],
                priority=8
            ),
            MCPAdapterInfo(
                name="Unified Smart Tool Engine MCP",
                id="unified_smart_tool_engine_mcp",
                file_path="mcptool/adapters/unified_smart_tool_engine_mcp.py",
                category="intelligent_engine",
                status=AdapterStatus.AVAILABLE.value,
                description="統一智能工具引擎，集成多種工具能力",
                capabilities=["tool_integration", "unified_interface", "smart_selection"],
                priority=9
            ),
            MCPAdapterInfo(
                name="Sequential Thinking MCP",
                id="sequential_thinking_mcp",
                file_path="mcptool/adapters/sequential_thinking_adapter/sequential_thinking_mcp.py",
                category="intelligent_engine",
                status=AdapterStatus.AVAILABLE.value,
                description="序列思維處理器，提供步驟化推理能力",
                capabilities=["sequential_reasoning", "step_by_step", "logical_chain"],
                priority=8
            )
        ]
        
        # 數據與記憶適配器
        memory_adapters = [
            MCPAdapterInfo(
                name="Unified Memory MCP",
                id="unified_memory_mcp",
                file_path="mcptool/adapters/unified_memory_mcp.py",
                category="memory_data",
                status=AdapterStatus.AVAILABLE.value,
                description="統一記憶系統，管理長期和短期記憶",
                capabilities=["memory_management", "context_retention", "knowledge_storage"],
                priority=9
            ),
            MCPAdapterInfo(
                name="SuperMemory MCP",
                id="supermemory_mcp",
                file_path="mcptool/adapters/supermemory_adapter/supermemory_mcp.py",
                category="memory_data",
                status=AdapterStatus.AVAILABLE.value,
                description="超級記憶系統，提供高級記憶和檢索功能",
                capabilities=["advanced_memory", "semantic_search", "knowledge_graph"],
                priority=8
            ),
            MCPAdapterInfo(
                name="Infinite Context MCP",
                id="infinite_context_mcp",
                file_path="mcptool/adapters/infinite_context_adapter/infinite_context_mcp.py",
                category="memory_data",
                status=AdapterStatus.AVAILABLE.value,
                description="無限上下文處理器，突破上下文長度限制",
                capabilities=["infinite_context", "context_compression", "long_term_memory"],
                priority=8
            ),
            MCPAdapterInfo(
                name="Thought Action Recorder MCP",
                id="thought_action_recorder_mcp",
                file_path="mcptool/adapters/thought_action_recorder_mcp.py",
                category="memory_data",
                status=AdapterStatus.AVAILABLE.value,
                description="思維行動記錄器，記錄和分析決策過程",
                capabilities=["thought_recording", "action_tracking", "decision_analysis"],
                priority=7
            )
        ]
        
        # 監控與優化適配器
        monitoring_adapters = [
            MCPAdapterInfo(
                name="Context Monitor MCP",
                id="context_monitor_mcp",
                file_path="mcptool/adapters/context_monitor_mcp.py",
                category="monitoring",
                status=AdapterStatus.AVAILABLE.value,
                description="上下文監控器，實時監控系統狀態",
                capabilities=["context_monitoring", "system_health", "performance_tracking"],
                priority=7
            ),
            MCPAdapterInfo(
                name="Cloud Edge Data MCP",
                id="cloud_edge_data_mcp",
                file_path="mcptool/adapters/cloud_edge_data_mcp.py",
                category="monitoring",
                status=AdapterStatus.AVAILABLE.value,
                description="雲邊數據處理器，管理分佈式數據流",
                capabilities=["cloud_edge", "distributed_processing", "data_sync"],
                priority=6
            ),
            MCPAdapterInfo(
                name="Config Manager MCP",
                id="config_manager_mcp",
                file_path="mcptool/adapters/unified_config_manager/config_manager_mcp.py",
                category="monitoring",
                status=AdapterStatus.AVAILABLE.value,
                description="配置管理器，統一管理系統配置",
                capabilities=["config_management", "settings_sync", "environment_control"],
                priority=6
            )
        ]
        
        # Agent優化適配器
        agent_adapters = [
            MCPAdapterInfo(
                name="Content Template Optimization MCP",
                id="content_template_optimization_mcp",
                file_path="mcptool/adapters/agent/content_template_optimization_mcp.py",
                category="agent_optimization",
                status=AdapterStatus.AVAILABLE.value,
                description="內容模板優化器，優化輸出內容格式",
                capabilities=["content_optimization", "template_management", "format_control"],
                priority=6
            ),
            MCPAdapterInfo(
                name="Context Matching Optimization MCP",
                id="context_matching_optimization_mcp",
                file_path="mcptool/adapters/agent/context_matching_optimization_mcp.py",
                category="agent_optimization",
                status=AdapterStatus.AVAILABLE.value,
                description="上下文匹配優化器，提升上下文理解準確性",
                capabilities=["context_matching", "semantic_alignment", "relevance_scoring"],
                priority=7
            ),
            MCPAdapterInfo(
                name="Prompt Optimization MCP",
                id="prompt_optimization_mcp",
                file_path="mcptool/adapters/agent/prompt_optimization_mcp.py",
                category="agent_optimization",
                status=AdapterStatus.AVAILABLE.value,
                description="提示詞優化器，自動優化AI提示詞",
                capabilities=["prompt_optimization", "query_enhancement", "response_improvement"],
                priority=7
            )
        ]
        
        # 集成適配器
        integration_adapters = [
            MCPAdapterInfo(
                name="Zapier MCP",
                id="zapier_mcp",
                file_path="mcptool/adapters/zapier_adapter/zapier_mcp.py",
                category="integration",
                status=AdapterStatus.AVAILABLE.value,
                description="Zapier集成適配器，連接外部服務和自動化",
                capabilities=["external_integration", "automation", "webhook_support"],
                priority=6
            ),
            MCPAdapterInfo(
                name="ACI Dev MCP",
                id="aci_dev_mcp",
                file_path="mcptool/adapters/enhanced_aci_dev_adapter/aci_dev_mcp.py",
                category="integration",
                status=AdapterStatus.AVAILABLE.value,
                description="ACI開發適配器，支持容器化部署",
                capabilities=["container_deployment", "aci_integration", "cloud_deployment"],
                priority=5
            ),
            MCPAdapterInfo(
                name="Dev Deploy Loop Coordinator MCP",
                id="dev_deploy_loop_coordinator_mcp",
                file_path="mcptool/adapters/dev_deploy_loop_coordinator_mcp.py",
                category="integration",
                status=AdapterStatus.AVAILABLE.value,
                description="開發部署循環協調器，管理CI/CD流程",
                capabilities=["cicd_coordination", "deployment_automation", "dev_ops"],
                priority=5
            ),
            MCPAdapterInfo(
                name="Release Discovery MCP",
                id="release_discovery_mcp",
                file_path="mcptool/adapters/release_discovery_mcp.py",
                category="integration",
                status=AdapterStatus.AVAILABLE.value,
                description="發布發現器，自動發現和管理軟件發布",
                capabilities=["release_management", "version_discovery", "update_tracking"],
                priority=5
            )
        ]
        
        # 註冊所有適配器
        all_adapters = (
            ai_adapters + tool_adapters + engine_adapters + 
            memory_adapters + monitoring_adapters + agent_adapters + 
            integration_adapters
        )
        
        for adapter in all_adapters:
            self._adapters[adapter.id] = adapter
        
        logger.info(f"初始化完成，註冊了 {len(all_adapters)} 個MCP適配器")
    
    def list_adapters(self, category: Optional[str] = None, status: Optional[str] = None) -> List[MCPAdapterInfo]:
        """列出適配器"""
        with self._lock:
            adapters = list(self._adapters.values())
            
            if category:
                adapters = [a for a in adapters if a.category == category]
            
            if status:
                adapters = [a for a in adapters if a.status == status]
            
            # 按優先級排序
            adapters.sort(key=lambda x: x.priority, reverse=True)
            return adapters
    
    def get_adapter_info(self, adapter_id: str) -> Optional[MCPAdapterInfo]:
        """獲取適配器信息"""
        with self._lock:
            return self._adapters.get(adapter_id)
    
    def get_high_priority_adapters(self, min_priority: int = 8) -> List[MCPAdapterInfo]:
        """獲取高優先級適配器"""
        with self._lock:
            return [a for a in self._adapters.values() if a.priority >= min_priority]
    
    def get_adapters_by_capability(self, capability: str) -> List[MCPAdapterInfo]:
        """根據能力獲取適配器"""
        with self._lock:
            return [a for a in self._adapters.values() if capability in a.capabilities]
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        with self._lock:
            total_adapters = len(self._adapters)
            loaded_adapters = len(self._loaded_adapters)
            loading_adapters = len(self._loading_stack)
            
            # 按分類統計
            category_counts = {}
            priority_counts = {}
            
            for adapter in self._adapters.values():
                category = adapter.category
                priority = adapter.priority
                
                category_counts[category] = category_counts.get(category, 0) + 1
                priority_counts[f"priority_{priority}"] = priority_counts.get(f"priority_{priority}", 0) + 1
            
            return {
                "total_adapters": total_adapters,
                "loaded_adapters": loaded_adapters,
                "loading_adapters": loading_adapters,
                "category_counts": category_counts,
                "priority_counts": priority_counts,
                "loading_stack": list(self._loading_stack)
            }
    
    def export_config(self) -> str:
        """導出配置"""
        with self._lock:
            config = {
                "adapters": [adapter.to_dict() for adapter in self._adapters.values()],
                "system_status": self.get_system_status()
            }
            return json.dumps(config, indent=2, ensure_ascii=False)

# 全局實例
_complete_mcp_registry = None
_registry_lock = threading.Lock()

def get_complete_mcp_registry() -> CompleteMCPAdapterRegistry:
    """獲取完整MCP適配器註冊表的全局實例"""
    global _complete_mcp_registry
    
    if _complete_mcp_registry is None:
        with _registry_lock:
            if _complete_mcp_registry is None:
                _complete_mcp_registry = CompleteMCPAdapterRegistry()
    
    return _complete_mcp_registry

if __name__ == "__main__":
    # 測試代碼
    registry = get_complete_mcp_registry()
    
    print("🔍 完整MCP適配器註冊表測試")
    print("=" * 60)
    
    # 顯示系統狀態
    status = registry.get_system_status()
    print(f"📊 系統狀態:")
    print(f"   總適配器: {status['total_adapters']}")
    print(f"   分類統計: {status['category_counts']}")
    
    # 顯示高優先級適配器
    print(f"\n🚀 高優先級適配器 (≥8):")
    high_priority = registry.get_high_priority_adapters(8)
    for adapter in high_priority:
        print(f"   ⭐ {adapter.name} (優先級: {adapter.priority})")
        print(f"      能力: {', '.join(adapter.capabilities)}")
    
    # 按分類顯示
    categories = ["ai_core", "tool_core", "intelligent_engine", "memory_data"]
    for category in categories:
        adapters = registry.list_adapters(category=category)
        print(f"\n🏷️ {category.upper()}類別 ({len(adapters)}個):")
        for adapter in adapters[:3]:  # 只顯示前3個
            print(f"   • {adapter.name} - {adapter.description[:50]}...")
    
    print("\n✅ 測試完成")

