#!/usr/bin/env python3
"""
十層測試架構索引和管理器
提供統一的測試層級管理和執行接口
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class TenLayerTestManager:
    """十層測試架構管理器"""
    
    def __init__(self, test_root: str = None):
        self.test_root = Path(test_root or Path(__file__).parent)
        self.layers = {
            1: {
                "name": "單元測試 + 代碼質量",
                "category": "基礎層",
                "description": "函數級別測試和代碼質量檢查",
                "path": self.test_root / "level1",
                "dependencies": [],
                "tools": ["pytest", "coverage", "pylint", "black"],
                "pass_criteria": {
                    "test_coverage": 90,
                    "code_quality": 8.0,
                    "all_tests_pass": True
                }
            },
            2: {
                "name": "集成測試 + 智能體協作",
                "category": "業務層",
                "description": "模塊間集成和智能體協作測試",
                "path": self.test_root / "level2",
                "dependencies": [1],
                "tools": ["pytest-integration", "API測試框架"],
                "pass_criteria": {
                    "integration_success": 95,
                    "api_response_time": 2.0,
                    "collaboration_rate": 95
                }
            },
            3: {
                "name": "MCP合規測試 + 標準化驗證",
                "category": "業務層",
                "description": "MCP協議合規性和標準化驗證",
                "path": self.test_root / "level3",
                "dependencies": [1, 2],
                "tools": ["MCP協議驗證器", "標準化測試框架"],
                "pass_criteria": {
                    "mcp_compliance": 90,
                    "standardization": 100,
                    "error_handling": 100
                }
            },
            4: {
                "name": "端到端測試 + 用戶場景",
                "category": "業務層",
                "description": "完整用戶流程和場景測試",
                "path": self.test_root / "level4",
                "dependencies": [1, 2, 3],
                "tools": ["Selenium", "Playwright", "場景測試框架"],
                "pass_criteria": {
                    "e2e_success": 95,
                    "user_experience": 4.5,
                    "scenario_coverage": 90
                }
            },
            5: {
                "name": "性能測試 + 四層兜底性能",
                "category": "戰術層",
                "description": "系統性能和兜底機制測試",
                "path": self.test_root / "level5",
                "dependencies": [1, 2, 3, 4],
                "tools": ["JMeter", "Locust", "性能監控工具"],
                "pass_criteria": {
                    "response_time": 500,
                    "load_capacity": 10,
                    "fallback_effectiveness": 100
                }
            },
            6: {
                "name": "安全測試 + 企業級安全",
                "category": "戰術層",
                "description": "安全漏洞掃描和企業級安全驗證",
                "path": self.test_root / "level6",
                "dependencies": [1, 2, 3, 4, 5],
                "tools": ["OWASP ZAP", "安全掃描工具"],
                "pass_criteria": {
                    "security_vulnerabilities": 0,
                    "permission_control": 100,
                    "data_encryption": 100
                },
                "owner": "用戶負責"
            },
            7: {
                "name": "兼容性測試 + 編輯器集成",
                "category": "戰術層",
                "description": "跨平台兼容性和編輯器集成測試",
                "path": self.test_root / "level7",
                "dependencies": [1, 2, 3, 4, 5],
                "tools": ["跨平台測試框架", "編輯器測試工具"],
                "pass_criteria": {
                    "platform_support": 100,
                    "editor_integration": 100,
                    "cross_env_consistency": 98
                }
            },
            8: {
                "name": "壓力測試 + 護城河驗證",
                "category": "戰略層",
                "description": "極限壓力測試和系統韌性驗證",
                "path": self.test_root / "level8",
                "dependencies": [1, 2, 3, 4, 5, 7],
                "tools": ["壓力測試工具", "混沌工程框架"],
                "pass_criteria": {
                    "stress_resistance": 100,
                    "resilience_mechanism": 100,
                    "recovery_time": 5
                }
            },
            9: {
                "name": "GAIA基準測試 + 競對比較",
                "category": "戰略層",
                "description": "GAIA基準測試和競爭對手比較",
                "path": self.test_root / "level9",
                "dependencies": [1, 2, 3, 4, 5, 7, 8],
                "tools": ["GAIA測試框架", "性能比較工具"],
                "pass_criteria": {
                    "gaia_accuracy": 75,
                    "competitive_advantage": True,
                    "industry_ranking": 10
                }
            },
            10: {
                "name": "AI能力評估 + 標準基準測試",
                "category": "戰略層",
                "description": "AI能力全面評估和標準基準測試",
                "path": self.test_root / "level10",
                "dependencies": [1, 2, 3, 4, 5, 7, 8, 9],
                "tools": ["AI評估框架", "基準測試工具"],
                "pass_criteria": {
                    "ai_capability": 90,
                    "benchmark_pass": 100,
                    "intelligence_level": "L4"
                },
                "owner": "用戶負責"
            }
        }
        
        self.execution_results = {}
        
    def get_layer_info(self, layer_id: int) -> Dict[str, Any]:
        """獲取指定層級的信息"""
        return self.layers.get(layer_id, {})
    
    def list_all_layers(self) -> Dict[int, Dict[str, Any]]:
        """列出所有測試層級"""
        return self.layers
    
    def get_execution_order(self) -> List[int]:
        """獲取測試執行順序（基於依賴關係）"""
        order = []
        remaining = set(self.layers.keys())
        
        while remaining:
            # 找到沒有未滿足依賴的層級
            ready = []
            for layer_id in remaining:
                dependencies = self.layers[layer_id]["dependencies"]
                if all(dep in order for dep in dependencies):
                    ready.append(layer_id)
            
            if not ready:
                # 如果沒有準備好的層級，可能存在循環依賴
                ready = [min(remaining)]
            
            # 按層級ID排序
            ready.sort()
            order.extend(ready)
            remaining -= set(ready)
        
        return order
    
    def check_layer_readiness(self, layer_id: int) -> Dict[str, Any]:
        """檢查層級是否準備就緒"""
        layer = self.layers.get(layer_id)
        if not layer:
            return {"ready": False, "error": "Layer not found"}
        
        readiness = {
            "ready": True,
            "layer_id": layer_id,
            "layer_name": layer["name"],
            "issues": []
        }
        
        # 檢查路徑是否存在
        if not layer["path"].exists():
            readiness["ready"] = False
            readiness["issues"].append(f"Path does not exist: {layer['path']}")
        
        # 檢查依賴是否滿足
        for dep in layer["dependencies"]:
            if dep not in self.execution_results or not self.execution_results[dep].get("passed", False):
                readiness["ready"] = False
                readiness["issues"].append(f"Dependency layer {dep} not passed")
        
        # 檢查是否有測試文件
        if layer["path"].exists():
            test_files = list(layer["path"].glob("*.py"))
            if not test_files:
                readiness["issues"].append("No test files found")
        
        return readiness
    
    def generate_test_report(self) -> str:
        """生成測試架構報告"""
        report = f"""
# 十層測試架構報告

## 📊 架構概覽
生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏗️ 層級結構

"""
        
        for layer_id in sorted(self.layers.keys()):
            layer = self.layers[layer_id]
            status = "✅" if layer["path"].exists() else "❌"
            owner = layer.get("owner", "系統負責")
            
            report += f"""### Level {layer_id}: {layer['name']} ({layer['category']})
- **狀態**: {status}
- **負責方**: {owner}
- **描述**: {layer['description']}
- **路徑**: `{layer['path']}`
- **依賴**: {layer['dependencies'] if layer['dependencies'] else '無'}
- **工具**: {', '.join(layer['tools'])}

"""
        
        report += f"""
## 🔄 執行順序
推薦執行順序: {' → '.join(map(str, self.get_execution_order()))}

## 📋 層級分類
- **基礎層**: Level 1
- **業務層**: Level 2, 3, 4
- **戰術層**: Level 5, 6, 7
- **戰略層**: Level 8, 9, 10

## 🎯 通過標準
每個層級都有明確的通過標準，詳見各層級的README.md文件。

## 📝 使用說明
1. 按照執行順序運行測試
2. 確保前置依賴層級通過
3. 查看各層級的詳細說明
4. 根據測試結果進行改進
"""
        
        return report
    
    def scan_test_files(self) -> Dict[int, List[str]]:
        """掃描各層級的測試文件"""
        test_files = {}
        
        for layer_id, layer in self.layers.items():
            files = []
            if layer["path"].exists():
                # Python測試文件
                py_files = list(layer["path"].glob("*.py"))
                files.extend([f.name for f in py_files])
                
                # Markdown文檔
                md_files = list(layer["path"].glob("*.md"))
                files.extend([f.name for f in md_files])
                
                # JSON配置文件
                json_files = list(layer["path"].glob("*.json"))
                files.extend([f.name for f in json_files])
            
            test_files[layer_id] = files
        
        return test_files

if __name__ == "__main__":
    manager = TenLayerTestManager()
    
    # 生成架構報告
    report = manager.generate_test_report()
    
    # 保存報告
    report_file = Path("ten_layer_test_architecture_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 掃描測試文件
    test_files = manager.scan_test_files()
    
    print("🏗️ 十層測試架構管理器")
    print(f"📄 架構報告已保存到: {report_file}")
    print(f"🔄 推薦執行順序: {' → '.join(map(str, manager.get_execution_order()))}")
    
    print("\n📁 各層級測試文件:")
    for layer_id, files in test_files.items():
        layer_name = manager.layers[layer_id]["name"]
        print(f"  Level {layer_id} ({layer_name}): {len(files)} 個文件")
        for file in files[:3]:  # 只顯示前3個文件
            print(f"    - {file}")
        if len(files) > 3:
            print(f"    - ... 還有 {len(files) - 3} 個文件")
    
    print(f"\n✅ 十層測試架構重組完成！")

