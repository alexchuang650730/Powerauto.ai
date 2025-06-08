#!/usr/bin/env python3
"""
RL_SRT + 異步RL 與統一記憶模塊集成完整性檢查器
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class RLMemoryIntegrationChecker:
    """RL-記憶集成完整性檢查器"""
    
    def __init__(self):
        """初始化檢查器"""
        self.base_path = "/home/ubuntu/Powerauto.ai"
        self.check_results = {}
        
    def check_integration_completeness(self) -> Dict[str, Any]:
        """檢查集成完整性"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {},
            "integration_points": {},
            "data_flow_analysis": {},
            "missing_components": [],
            "recommendations": []
        }
        
        # 1. 檢查核心組件
        results["components"] = self._check_core_components()
        
        # 2. 檢查集成點
        results["integration_points"] = self._check_integration_points()
        
        # 3. 分析數據流
        results["data_flow_analysis"] = self._analyze_data_flow()
        
        # 4. 檢查記憶數據接口
        results["memory_interfaces"] = self._check_memory_interfaces()
        
        # 5. 評估整體完整性
        results["overall_status"] = self._evaluate_overall_status(results)
        
        return results
    
    def _check_core_components(self) -> Dict[str, Any]:
        """檢查核心組件"""
        components = {
            "rl_srt_mcp": {
                "path": "mcptool/adapters/rl_srt/rl_srt_mcp.py",
                "status": "unknown",
                "features": []
            },
            "rl_srt_dataflow_mcp": {
                "path": "mcptool/adapters/rl_srt_dataflow_mcp.py", 
                "status": "unknown",
                "features": []
            },
            "unified_memory_mcp": {
                "path": "mcptool/adapters/unified_memory_mcp.py",
                "status": "unknown",
                "features": []
            },
            "memory_query_engine": {
                "path": "memory-system/memory_query_engine.py",
                "status": "unknown",
                "features": []
            },
            "cloud_edge_data_mcp": {
                "path": "mcptool/adapters/cloud_edge_data_mcp.py",
                "status": "unknown",
                "features": []
            }
        }
        
        for component_name, component_info in components.items():
            full_path = os.path.join(self.base_path, component_info["path"])
            
            if os.path.exists(full_path):
                component_info["status"] = "exists"
                component_info["features"] = self._analyze_component_features(full_path)
            else:
                component_info["status"] = "missing"
        
        return components
    
    def _analyze_component_features(self, file_path: str) -> List[str]:
        """分析組件功能特性"""
        features = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 檢查關鍵功能
            feature_patterns = {
                "async_training": ["async", "asyncio", "_async_training"],
                "memory_integration": ["memory", "get_training_data", "interaction_data"],
                "data_flow": ["data_flow", "stream", "batch"],
                "rl_training": ["rl", "reinforcement", "reward", "train"],
                "srt_training": ["srt", "self_reward", "self-reward"],
                "cloud_edge": ["cloud", "edge", "federated"],
                "performance_monitoring": ["metrics", "performance", "monitor"]
            }
            
            for feature, patterns in feature_patterns.items():
                if any(pattern.lower() in content.lower() for pattern in patterns):
                    features.append(feature)
                    
        except Exception as e:
            logger.warning(f"分析文件失敗 {file_path}: {e}")
        
        return features
    
    def _check_integration_points(self) -> Dict[str, Any]:
        """檢查集成點"""
        integration_points = {
            "rl_to_memory": {
                "description": "RL系統從記憶模塊獲取交互數據",
                "status": "unknown",
                "implementation": []
            },
            "memory_to_rl": {
                "description": "記憶模塊向RL系統提供訓練數據",
                "status": "unknown", 
                "implementation": []
            },
            "async_data_pipeline": {
                "description": "異步數據管道處理",
                "status": "unknown",
                "implementation": []
            },
            "cloud_edge_sync": {
                "description": "雲端邊緣數據同步",
                "status": "unknown",
                "implementation": []
            }
        }
        
        # 檢查RL_SRT數據流文件中的集成實現
        dataflow_file = os.path.join(self.base_path, "mcptool/adapters/rl_srt_dataflow_mcp.py")
        if os.path.exists(dataflow_file):
            with open(dataflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 檢查記憶集成
            if "cloud_edge_data" in content and "get_training_data" in content:
                integration_points["rl_to_memory"]["status"] = "implemented"
                integration_points["rl_to_memory"]["implementation"].append("CloudEdgeDataMCP集成")
                
            if "async" in content and "training_loop" in content:
                integration_points["async_data_pipeline"]["status"] = "implemented"
                integration_points["async_data_pipeline"]["implementation"].append("異步訓練循環")
                
            if "federated" in content or "sync_with_cloud" in content:
                integration_points["cloud_edge_sync"]["status"] = "implemented"
                integration_points["cloud_edge_sync"]["implementation"].append("聯邦學習支持")
        
        return integration_points
    
    def _analyze_data_flow(self) -> Dict[str, Any]:
        """分析數據流"""
        data_flow = {
            "memory_data_sources": [],
            "rl_training_pipeline": [],
            "data_transformation": [],
            "feedback_loop": []
        }
        
        # 檢查記憶數據源
        memory_files = [
            "mcptool/adapters/unified_memory_mcp.py",
            "memory-system/memory_query_engine.py",
            "mcptool/adapters/supermemory_adapter/supermemory_mcp.py"
        ]
        
        for memory_file in memory_files:
            full_path = os.path.join(self.base_path, memory_file)
            if os.path.exists(full_path):
                data_flow["memory_data_sources"].append({
                    "file": memory_file,
                    "status": "available"
                })
        
        # 檢查RL訓練管道
        rl_files = [
            "mcptool/adapters/rl_srt/rl_srt_mcp.py",
            "mcptool/adapters/rl_srt_dataflow_mcp.py"
        ]
        
        for rl_file in rl_files:
            full_path = os.path.join(self.base_path, rl_file)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                pipeline_features = []
                if "async" in content:
                    pipeline_features.append("異步處理")
                if "batch" in content:
                    pipeline_features.append("批次處理")
                if "stream" in content:
                    pipeline_features.append("流式處理")
                    
                data_flow["rl_training_pipeline"].append({
                    "file": rl_file,
                    "features": pipeline_features
                })
        
        return data_flow
    
    def _check_memory_interfaces(self) -> Dict[str, Any]:
        """檢查記憶數據接口"""
        interfaces = {
            "interaction_data_api": {
                "description": "獲取用戶交互數據的API",
                "status": "unknown",
                "methods": []
            },
            "training_data_api": {
                "description": "獲取訓練數據的API", 
                "status": "unknown",
                "methods": []
            },
            "feedback_data_api": {
                "description": "獲取反饋數據的API",
                "status": "unknown",
                "methods": []
            }
        }
        
        # 檢查數據流文件中的接口實現
        dataflow_file = os.path.join(self.base_path, "mcptool/adapters/rl_srt_dataflow_mcp.py")
        if os.path.exists(dataflow_file):
            with open(dataflow_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 檢查訓練數據API
            if "get_training_data" in content:
                interfaces["training_data_api"]["status"] = "implemented"
                interfaces["training_data_api"]["methods"].append("get_training_data")
                
            # 檢查交互數據處理
            if "_prepare_rl_data" in content:
                interfaces["interaction_data_api"]["status"] = "implemented"
                interfaces["interaction_data_api"]["methods"].append("_prepare_rl_data")
                
            # 檢查反饋處理
            if "reward" in content and "quality_score" in content:
                interfaces["feedback_data_api"]["status"] = "implemented"
                interfaces["feedback_data_api"]["methods"].append("reward_extraction")
        
        return interfaces
    
    def _evaluate_overall_status(self, results: Dict[str, Any]) -> str:
        """評估整體狀態"""
        # 檢查核心組件完整性
        components = results["components"]
        existing_components = sum(1 for comp in components.values() if comp["status"] == "exists")
        total_components = len(components)
        
        # 檢查集成點實現
        integration_points = results["integration_points"]
        implemented_integrations = sum(1 for point in integration_points.values() if point["status"] == "implemented")
        total_integrations = len(integration_points)
        
        # 檢查接口完整性
        interfaces = results["memory_interfaces"]
        implemented_interfaces = sum(1 for iface in interfaces.values() if iface["status"] == "implemented")
        total_interfaces = len(interfaces)
        
        # 計算完整性分數
        component_score = existing_components / total_components
        integration_score = implemented_integrations / total_integrations if total_integrations > 0 else 0
        interface_score = implemented_interfaces / total_interfaces if total_interfaces > 0 else 0
        
        overall_score = (component_score + integration_score + interface_score) / 3
        
        if overall_score >= 0.8:
            return "complete"
        elif overall_score >= 0.6:
            return "mostly_complete"
        elif overall_score >= 0.4:
            return "partially_complete"
        else:
            return "incomplete"


def main():
    """主檢查函數"""
    print("🔍 RL_SRT + 異步RL 與統一記憶模塊集成完整性檢查\\n")
    
    checker = RLMemoryIntegrationChecker()
    results = checker.check_integration_completeness()
    
    # 顯示結果
    print(f"📊 整體狀態: {results['overall_status']}")
    print()
    
    print("🧩 核心組件:")
    for name, info in results["components"].items():
        status_emoji = "✅" if info["status"] == "exists" else "❌"
        print(f"  {status_emoji} {name}: {info['status']}")
        if info["features"]:
            print(f"     功能: {', '.join(info['features'])}")
    print()
    
    print("🔗 集成點:")
    for name, info in results["integration_points"].items():
        status_emoji = "✅" if info["status"] == "implemented" else "❓"
        print(f"  {status_emoji} {name}: {info['status']}")
        print(f"     {info['description']}")
        if info["implementation"]:
            print(f"     實現: {', '.join(info['implementation'])}")
    print()
    
    print("📡 記憶數據接口:")
    for name, info in results["memory_interfaces"].items():
        status_emoji = "✅" if info["status"] == "implemented" else "❓"
        print(f"  {status_emoji} {name}: {info['status']}")
        print(f"     {info['description']}")
        if info["methods"]:
            print(f"     方法: {', '.join(info['methods'])}")
    print()
    
    print("📈 數據流分析:")
    data_flow = results["data_flow_analysis"]
    print(f"  記憶數據源: {len(data_flow['memory_data_sources'])} 個")
    print(f"  RL訓練管道: {len(data_flow['rl_training_pipeline'])} 個")
    
    # 保存詳細結果
    with open("/home/ubuntu/Powerauto.ai/rl_memory_integration_check.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\\n📄 詳細結果已保存到: rl_memory_integration_check.json")

if __name__ == "__main__":
    main()

