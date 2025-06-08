#!/usr/bin/env python3
"""
隔離MCP適配器測試器
在隔離環境中測試單個MCP適配器，避免循環依賴
"""

import sys
import os
import importlib
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any

class IsolatedMCPTester:
    """隔離MCP適配器測試器"""
    
    def __init__(self):
        self.test_results = {}
        
    def test_adapter_in_isolation(self, adapter_name: str, module_path: str) -> Dict[str, Any]:
        """在隔離進程中測試適配器"""
        
        # 創建測試腳本
        test_script = f'''
import sys
import os
import importlib
import traceback
from pathlib import Path

# 添加項目路徑但避免自動導入
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 禁用自動註冊
os.environ["DISABLE_AUTO_REGISTRATION"] = "1"
os.environ["MCP_ISOLATED_TEST"] = "1"

result = {{
    "name": "{adapter_name}",
    "module_path": "{module_path}",
    "import_success": False,
    "class_found": False,
    "init_success": False,
    "methods": [],
    "error": None,
    "class_name": None
}}

try:
    # 1. 測試導入
    print(f"導入模塊: {module_path}")
    module = importlib.import_module("{module_path}")
    result["import_success"] = True
    print("✅ 導入成功")
    
    # 2. 查找適配器類
    adapter_classes = []
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and 
            (attr_name.endswith('MCP') or attr_name.endswith('Adapter')) and 
            attr.__module__ == module.__name__):
            adapter_classes.append((attr_name, attr))
    
    if adapter_classes:
        class_name, adapter_class = adapter_classes[0]
        result["class_found"] = True
        result["class_name"] = class_name
        print(f"✅ 找到類: {{class_name}}")
        
        # 3. 測試初始化（簡單模式）
        try:
            # 嘗試無參數初始化
            adapter_instance = adapter_class()
            result["init_success"] = True
            print("✅ 初始化成功")
            
            # 4. 獲取方法列表
            methods = [name for name in dir(adapter_instance) 
                      if callable(getattr(adapter_instance, name)) 
                      and not name.startswith('_')]
            result["methods"] = methods
            print(f"✅ 找到方法: {{len(methods)}}個")
            
        except Exception as e:
            # 嘗試帶參數初始化
            try:
                adapter_instance = adapter_class(name="{adapter_name}")
                result["init_success"] = True
                print("✅ 初始化成功（帶參數）")
            except Exception as e2:
                result["error"] = f"初始化失敗: {{str(e)}}"
                print(f"❌ 初始化失敗: {{str(e)}}")
    else:
        result["error"] = "未找到適配器類"
        print("❌ 未找到適配器類")
        
except Exception as e:
    result["error"] = f"導入失敗: {{str(e)}}"
    print(f"❌ 導入失敗: {{str(e)}}")

# 輸出結果
import json
print("RESULT_JSON_START")
print(json.dumps(result, ensure_ascii=False))
print("RESULT_JSON_END")
'''
        
        # 將測試腳本寫入臨時文件
        test_file = f"/tmp/test_{adapter_name.replace(' ', '_').lower()}.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        try:
            # 在隔離進程中運行測試
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd="/home/ubuntu/Powerauto.ai"
            )
            
            # 解析結果
            output = result.stdout
            if "RESULT_JSON_START" in output and "RESULT_JSON_END" in output:
                json_start = output.find("RESULT_JSON_START") + len("RESULT_JSON_START\n")
                json_end = output.find("RESULT_JSON_END")
                json_str = output[json_start:json_end].strip()
                
                try:
                    test_result = json.loads(json_str)
                    return test_result
                except json.JSONDecodeError as e:
                    return {
                        "name": adapter_name,
                        "error": f"JSON解析失敗: {str(e)}",
                        "raw_output": output
                    }
            else:
                return {
                    "name": adapter_name,
                    "error": "未找到結果JSON",
                    "raw_output": output,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "name": adapter_name,
                "error": "測試超時（30秒）"
            }
        except Exception as e:
            return {
                "name": adapter_name,
                "error": f"進程執行失敗: {str(e)}"
            }
        finally:
            # 清理臨時文件
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def run_isolated_tests(self):
        """運行隔離測試"""
        print("🔒 隔離MCP適配器測試")
        print("=" * 40)
        
        # 關鍵適配器列表
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
            print(f"\n🧪 測試: {adapter_name}")
            print("-" * 30)
            
            result = self.test_adapter_in_isolation(adapter_name, module_path)
            self.test_results[adapter_name] = result
            
            if result.get("init_success", False):
                working_adapters.append(adapter_name)
                print(f"✅ {adapter_name} 運行正常")
                print(f"   類名: {result.get('class_name', 'Unknown')}")
                print(f"   方法數: {len(result.get('methods', []))}")
            else:
                failed_adapters.append(adapter_name)
                error = result.get('error', '未知錯誤')
                print(f"❌ {adapter_name} 運行異常")
                print(f"   錯誤: {error[:80]}...")
        
        # 生成報告
        print(f"\n📊 隔離測試結果")
        print("=" * 25)
        print(f"總測試數: {len(key_adapters)}")
        print(f"正常運行: {len(working_adapters)}")
        print(f"運行異常: {len(failed_adapters)}")
        
        if working_adapters:
            print(f"\n✅ 正常運行的適配器:")
            for adapter in working_adapters:
                result = self.test_results[adapter]
                class_name = result.get('class_name', 'Unknown')
                method_count = len(result.get('methods', []))
                print(f"   • {adapter} ({class_name}) - {method_count}個方法")
        
        if failed_adapters:
            print(f"\n❌ 運行異常的適配器:")
            for adapter in failed_adapters:
                result = self.test_results[adapter]
                error = result.get('error', '未知錯誤')
                print(f"   • {adapter}: {error[:60]}...")
        
        return working_adapters, failed_adapters

def main():
    """主函數"""
    tester = IsolatedMCPTester()
    working, failed = tester.run_isolated_tests()
    
    # 保存結果
    with open('isolated_mcp_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(tester.test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 測試結果已保存到: isolated_mcp_test_results.json")
    
    if len(working) >= len(failed):
        print(f"\n🎉 隔離測試成功！{len(working)}個適配器可以正常運行")
        return True
    else:
        print(f"\n⚠️ 需要修復！{len(failed)}個適配器無法正常運行")
        return False

if __name__ == "__main__":
    success = main()

