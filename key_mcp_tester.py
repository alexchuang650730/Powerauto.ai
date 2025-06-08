#!/usr/bin/env python3
"""
關鍵MCP適配器快速測試
專門測試KiloCode、RL-SRT等重要適配器的運行狀態
"""

import sys
import os
import importlib
import traceback
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 設置日誌
logging.basicConfig(level=logging.WARNING)  # 減少日誌輸出
logger = logging.getLogger(__name__)

class KeyMCPTester:
    """關鍵MCP適配器測試器"""
    
    def __init__(self):
        self.test_results = {}
        
    def test_single_adapter(self, adapter_name: str, module_path: str) -> Dict[str, Any]:
        """測試單個適配器"""
        result = {
            "name": adapter_name,
            "import_success": False,
            "init_success": False,
            "class_found": False,
            "error": None,
            "class_name": None,
            "methods": []
        }
        
        try:
            print(f"🔧 測試 {adapter_name}")
            
            # 1. 測試導入
            print(f"   📥 導入模塊: {module_path}")
            module = importlib.import_module(module_path)
            result["import_success"] = True
            print(f"   ✅ 導入成功")
            
            # 2. 查找適配器類
            adapter_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    (attr_name.endswith('MCP') or attr_name.endswith('Adapter')) and 
                    attr.__module__ == module.__name__):
                    adapter_classes.append((attr_name, attr))
            
            if not adapter_classes:
                result["error"] = "未找到適配器類"
                print(f"   ❌ 未找到適配器類")
                return result
            
            # 使用第一個找到的類
            class_name, adapter_class = adapter_classes[0]
            result["class_found"] = True
            result["class_name"] = class_name
            print(f"   🎯 找到類: {class_name}")
            
            # 3. 測試初始化
            print(f"   🚀 初始化適配器...")
            try:
                adapter_instance = adapter_class()
                result["init_success"] = True
                print(f"   ✅ 初始化成功")
                
                # 4. 檢查可用方法
                methods = [name for name in dir(adapter_instance) 
                          if callable(getattr(adapter_instance, name)) 
                          and not name.startswith('_')]
                result["methods"] = methods[:10]  # 只記錄前10個方法
                print(f"   📋 可用方法: {', '.join(methods[:5])}...")
                
            except Exception as e:
                result["error"] = f"初始化失敗: {str(e)}"
                print(f"   ❌ 初始化失敗: {str(e)}")
                
        except Exception as e:
            result["error"] = f"導入失敗: {str(e)}"
            print(f"   ❌ 導入失敗: {str(e)}")
        
        return result
    
    def run_key_tests(self):
        """運行關鍵適配器測試"""
        print("🔍 關鍵MCP適配器快速測試")
        print("=" * 50)
        
        # 定義關鍵適配器
        key_adapters = [
            ("KiloCode MCP", "mcptool.adapters.kilocode_adapter.kilocode_mcp"),
            ("RL-SRT MCP", "mcptool.adapters.rl_srt.rl_srt_mcp"),
            ("Claude MCP", "mcptool.adapters.claude_adapter.claude_mcp"),
            ("Gemini MCP", "mcptool.adapters.gemini_adapter.gemini_mcp"),
            ("Smart Routing MCP", "mcptool.adapters.smart_routing_mcp"),
            ("Unified Memory MCP", "mcptool.adapters.unified_memory_mcp"),
            ("Sequential Thinking MCP", "mcptool.adapters.sequential_thinking_adapter.sequential_thinking_mcp"),
            ("Intelligent Workflow Engine MCP", "mcptool.adapters.intelligent_workflow_engine_mcp"),
            ("WebAgent Core", "mcptool.adapters.core.webagent_core"),
            ("SuperMemory MCP", "mcptool.adapters.supermemory_adapter.supermemory_mcp")
        ]
        
        working_adapters = []
        failed_adapters = []
        
        for adapter_name, module_path in key_adapters:
            result = self.test_single_adapter(adapter_name, module_path)
            self.test_results[adapter_name] = result
            
            if result["init_success"]:
                working_adapters.append(adapter_name)
                print(f"   🎉 {adapter_name} 運行正常\n")
            else:
                failed_adapters.append(adapter_name)
                print(f"   ⚠️ {adapter_name} 運行異常\n")
        
        # 生成摘要報告
        print("📊 測試結果摘要")
        print("=" * 30)
        print(f"總測試數: {len(key_adapters)}")
        print(f"正常運行: {len(working_adapters)}")
        print(f"運行異常: {len(failed_adapters)}")
        
        if working_adapters:
            print(f"\n✅ 正常運行的適配器:")
            for adapter in working_adapters:
                result = self.test_results[adapter]
                print(f"   • {adapter} ({result['class_name']})")
        
        if failed_adapters:
            print(f"\n❌ 運行異常的適配器:")
            for adapter in failed_adapters:
                result = self.test_results[adapter]
                error = result.get('error', '未知錯誤')
                print(f"   • {adapter}: {error[:60]}...")
        
        return working_adapters, failed_adapters

def main():
    """主函數"""
    tester = KeyMCPTester()
    working, failed = tester.run_key_tests()
    
    # 保存結果
    import json
    with open('key_mcp_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 測試結果已保存到: key_mcp_test_results.json")
    
    if len(working) >= len(failed):
        print(f"\n🎉 測試成功！{len(working)}個關鍵適配器正常運行")
        return True
    else:
        print(f"\n⚠️ 需要關注！{len(failed)}個關鍵適配器運行異常")
        return False

if __name__ == "__main__":
    success = main()

