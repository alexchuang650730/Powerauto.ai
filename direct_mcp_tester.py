#!/usr/bin/env python3
"""
直接MCP適配器測試器
直接在當前環境中測試MCP適配器，但禁用自動註冊
"""

import sys
import os
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any

# 禁用自動註冊和循環依賴
os.environ["DISABLE_AUTO_REGISTRATION"] = "1"
os.environ["MCP_ISOLATED_TEST"] = "1"
os.environ["PYTHONPATH"] = "/home/ubuntu/Powerauto.ai"

# 設置最小日誌級別
logging.basicConfig(level=logging.CRITICAL)

# 添加項目路徑
sys.path.insert(0, "/home/ubuntu/Powerauto.ai")

class DirectMCPTester:
    """直接MCP適配器測試器"""
    
    def __init__(self):
        self.test_results = {}
        
    def test_adapter_direct(self, adapter_name: str, module_path: str) -> Dict[str, Any]:
        """直接測試適配器"""
        result = {
            "name": adapter_name,
            "module_path": module_path,
            "import_success": False,
            "class_found": False,
            "init_success": False,
            "methods": [],
            "error": None,
            "class_name": None
        }
        
        try:
            print(f"🔧 測試: {adapter_name}")
            
            # 1. 測試導入
            print(f"   📥 導入: {module_path}")
            
            # 清理之前的導入
            if module_path in sys.modules:
                del sys.modules[module_path]
            
            module = importlib.import_module(module_path)
            result["import_success"] = True
            print(f"   ✅ 導入成功")
            
            # 2. 查找適配器類
            adapter_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    (attr_name.endswith('MCP') or attr_name.endswith('Adapter')) and 
                    hasattr(attr, '__module__') and
                    attr.__module__ == module.__name__):
                    adapter_classes.append((attr_name, attr))
            
            if not adapter_classes:
                # 嘗試查找其他可能的類
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        not attr_name.startswith('_') and
                        hasattr(attr, '__module__') and
                        attr.__module__ == module.__name__):
                        adapter_classes.append((attr_name, attr))
            
            if adapter_classes:
                class_name, adapter_class = adapter_classes[0]
                result["class_found"] = True
                result["class_name"] = class_name
                print(f"   🎯 找到類: {class_name}")
                
                # 3. 測試初始化
                print(f"   🚀 初始化...")
                try:
                    # 嘗試無參數初始化
                    adapter_instance = adapter_class()
                    result["init_success"] = True
                    print(f"   ✅ 初始化成功")
                    
                    # 4. 獲取方法列表
                    methods = [name for name in dir(adapter_instance) 
                              if callable(getattr(adapter_instance, name)) 
                              and not name.startswith('_')]
                    result["methods"] = methods[:20]  # 限制方法數量
                    print(f"   📋 方法數: {len(methods)}")
                    
                except Exception as e:
                    # 嘗試帶參數初始化
                    try:
                        adapter_instance = adapter_class(name=adapter_name)
                        result["init_success"] = True
                        print(f"   ✅ 初始化成功（帶參數）")
                    except Exception as e2:
                        result["error"] = f"初始化失敗: {str(e)}"
                        print(f"   ❌ 初始化失敗: {str(e)[:50]}...")
            else:
                result["error"] = "未找到適配器類"
                print(f"   ❌ 未找到適配器類")
                
        except Exception as e:
            result["error"] = f"導入失敗: {str(e)}"
            print(f"   ❌ 導入失敗: {str(e)[:50]}...")
        
        return result
    
    def run_direct_tests(self):
        """運行直接測試"""
        print("🎯 直接MCP適配器測試")
        print("=" * 35)
        
        # 關鍵適配器列表（使用相對路徑）
        key_adapters = [
            ("KiloCode MCP", "mcptool.adapters.kilocode_adapter.kilocode_mcp"),
            ("RL-SRT MCP", "mcptool.adapters.rl_srt.rl_srt_mcp"),
            ("Claude MCP", "mcptool.adapters.claude_adapter.claude_mcp"),
            ("Gemini MCP", "mcptool.adapters.gemini_adapter.gemini_mcp"),
            ("Smart Routing MCP", "mcptool.adapters.smart_routing_mcp"),
            ("Unified Memory MCP", "mcptool.adapters.unified_memory_mcp"),
            ("Sequential Thinking MCP", "mcptool.adapters.sequential_thinking_adapter.sequential_thinking_mcp"),
            ("SuperMemory MCP", "mcptool.adapters.supermemory_adapter.supermemory_mcp"),
            ("Context Monitor MCP", "mcptool.adapters.context_monitor_mcp"),
            ("Thought Action Recorder MCP", "mcptool.adapters.thought_action_recorder_mcp")
        ]
        
        working_adapters = []
        failed_adapters = []
        
        for adapter_name, module_path in key_adapters:
            result = self.test_adapter_direct(adapter_name, module_path)
            self.test_results[adapter_name] = result
            
            if result.get("init_success", False):
                working_adapters.append(adapter_name)
                print(f"   🎉 {adapter_name} 運行正常\n")
            else:
                failed_adapters.append(adapter_name)
                print(f"   ⚠️ {adapter_name} 運行異常\n")
        
        # 生成報告
        print("📊 直接測試結果")
        print("=" * 20)
        print(f"總測試數: {len(key_adapters)}")
        print(f"正常運行: {len(working_adapters)}")
        print(f"運行異常: {len(failed_adapters)}")
        
        if working_adapters:
            print(f"\n✅ 正常運行的適配器:")
            for adapter in working_adapters:
                result = self.test_results[adapter]
                class_name = result.get('class_name', 'Unknown')
                method_count = len(result.get('methods', []))
                print(f"   • {adapter}")
                print(f"     類名: {class_name}")
                print(f"     方法數: {method_count}")
                if result.get('methods'):
                    print(f"     主要方法: {', '.join(result['methods'][:5])}")
        
        if failed_adapters:
            print(f"\n❌ 運行異常的適配器:")
            for adapter in failed_adapters:
                result = self.test_results[adapter]
                error = result.get('error', '未知錯誤')
                stage = "導入" if not result.get('import_success') else "初始化"
                print(f"   • {adapter} ({stage}失敗)")
                print(f"     錯誤: {error[:80]}...")
        
        return working_adapters, failed_adapters

def main():
    """主函數"""
    tester = DirectMCPTester()
    working, failed = tester.run_direct_tests()
    
    # 保存結果
    import json
    with open('direct_mcp_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 測試結果已保存到: direct_mcp_test_results.json")
    
    # 創建工具註冊表
    if working:
        print(f"\n🔧 創建可用工具註冊表...")
        registry = {
            "available_tools": [],
            "tool_count": len(working),
            "test_timestamp": "2025-06-08"
        }
        
        for adapter_name in working:
            result = tester.test_results[adapter_name]
            tool_info = {
                "name": adapter_name,
                "class_name": result.get('class_name'),
                "module_path": result.get('module_path'),
                "method_count": len(result.get('methods', [])),
                "methods": result.get('methods', [])[:10],  # 前10個方法
                "status": "available"
            }
            registry["available_tools"].append(tool_info)
        
        with open('available_mcp_tools_registry.json', 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f"📋 可用工具註冊表已保存到: available_mcp_tools_registry.json")
    
    if len(working) >= len(failed):
        print(f"\n🎉 測試成功！{len(working)}個適配器可以正常運行")
        return True
    else:
        print(f"\n⚠️ 需要修復！{len(failed)}個適配器無法正常運行")
        return False

if __name__ == "__main__":
    success = main()

