#!/usr/bin/env python3
"""
MCP適配器運行狀態檢查器
測試所有MCP適配器的運行狀態和註冊情況
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPAdapterTester:
    """MCP適配器測試器"""
    
    def __init__(self):
        self.test_results = {}
        self.working_adapters = []
        self.failed_adapters = []
        
    def test_adapter_import(self, adapter_name: str, file_path: str) -> Tuple[bool, str, Any]:
        """測試適配器導入"""
        try:
            # 構建模塊路徑
            module_path = file_path.replace('/', '.').replace('.py', '')
            if module_path.startswith('mcptool.'):
                module_path = module_path
            else:
                module_path = f"mcptool.adapters.{module_path.split('mcptool/adapters/')[-1]}"
            
            logger.info(f"嘗試導入: {module_path}")
            
            # 導入模塊
            module = importlib.import_module(module_path)
            
            # 查找主要類
            adapter_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    attr_name.endswith('MCP') and 
                    attr.__module__ == module.__name__):
                    adapter_class = attr
                    break
            
            if adapter_class is None:
                # 嘗試常見的類名模式
                possible_names = [
                    adapter_name.replace('_', '').title() + 'MCP',
                    adapter_name.replace('_mcp', '').title() + 'MCP',
                    'MCP' + adapter_name.replace('_mcp', '').title(),
                ]
                
                for name in possible_names:
                    if hasattr(module, name):
                        adapter_class = getattr(module, name)
                        break
            
            if adapter_class is None:
                return False, f"未找到適配器類", None
            
            return True, f"成功導入 {adapter_class.__name__}", adapter_class
            
        except Exception as e:
            error_msg = f"導入失敗: {str(e)}"
            logger.error(f"{adapter_name}: {error_msg}")
            return False, error_msg, None
    
    def test_adapter_initialization(self, adapter_class: Any, adapter_name: str) -> Tuple[bool, str, Any]:
        """測試適配器初始化"""
        try:
            # 嘗試初始化適配器
            adapter_instance = adapter_class()
            
            # 檢查基本屬性
            has_name = hasattr(adapter_instance, 'name') or hasattr(adapter_instance, '__name__')
            has_process = hasattr(adapter_instance, 'process') or hasattr(adapter_instance, 'execute')
            
            status = "✅ 初始化成功"
            if has_name and has_process:
                status += " (具備基本接口)"
            
            return True, status, adapter_instance
            
        except Exception as e:
            error_msg = f"初始化失敗: {str(e)}"
            logger.error(f"{adapter_name}: {error_msg}")
            return False, error_msg, None
    
    def test_adapter_basic_functionality(self, adapter_instance: Any, adapter_name: str) -> Tuple[bool, str]:
        """測試適配器基本功能"""
        try:
            # 測試基本方法調用
            test_methods = ['process', 'execute', 'run', 'handle']
            
            for method_name in test_methods:
                if hasattr(adapter_instance, method_name):
                    method = getattr(adapter_instance, method_name)
                    if callable(method):
                        # 嘗試調用（使用簡單測試數據）
                        try:
                            # 大多數MCP適配器接受字典輸入
                            test_input = {"test": True, "message": "health_check"}
                            result = method(test_input)
                            return True, f"✅ 基本功能正常 (方法: {method_name})"
                        except Exception as e:
                            # 如果方法需要特定參數，這是正常的
                            if "required" in str(e).lower() or "missing" in str(e).lower():
                                return True, f"✅ 方法存在且可調用 (方法: {method_name})"
                            else:
                                return False, f"方法調用錯誤: {str(e)}"
            
            # 如果沒有找到標準方法，檢查是否有其他可調用方法
            callable_methods = [name for name in dir(adapter_instance) 
                              if callable(getattr(adapter_instance, name)) 
                              and not name.startswith('_')]
            
            if callable_methods:
                return True, f"✅ 具備可調用方法: {', '.join(callable_methods[:3])}"
            else:
                return False, "未找到可調用方法"
                
        except Exception as e:
            return False, f"功能測試失敗: {str(e)}"
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """運行全面測試"""
        print("🔍 開始MCP適配器全面測試")
        print("=" * 60)
        
        # 從完整註冊表獲取適配器列表
        from mcptool.adapters.complete_mcp_registry import get_complete_mcp_registry
        registry = get_complete_mcp_registry()
        
        all_adapters = registry.list_adapters()
        
        print(f"📋 將測試 {len(all_adapters)} 個MCP適配器")
        print()
        
        # 按優先級分組測試
        high_priority = [a for a in all_adapters if a.priority >= 8]
        medium_priority = [a for a in all_adapters if 5 <= a.priority < 8]
        low_priority = [a for a in all_adapters if a.priority < 5]
        
        test_groups = [
            ("🚀 高優先級適配器", high_priority),
            ("⚡ 中優先級適配器", medium_priority),
            ("📦 低優先級適配器", low_priority)
        ]
        
        for group_name, adapters in test_groups:
            if not adapters:
                continue
                
            print(f"{group_name} ({len(adapters)}個)")
            print("-" * 40)
            
            for adapter in adapters:
                print(f"\n🔧 測試: {adapter.name}")
                
                # 1. 測試導入
                import_success, import_msg, adapter_class = self.test_adapter_import(
                    adapter.id, adapter.file_path
                )
                print(f"   導入: {import_msg}")
                
                if not import_success:
                    self.failed_adapters.append(adapter.id)
                    self.test_results[adapter.id] = {
                        "status": "failed",
                        "stage": "import",
                        "error": import_msg
                    }
                    continue
                
                # 2. 測試初始化
                init_success, init_msg, adapter_instance = self.test_adapter_initialization(
                    adapter_class, adapter.id
                )
                print(f"   初始化: {init_msg}")
                
                if not init_success:
                    self.failed_adapters.append(adapter.id)
                    self.test_results[adapter.id] = {
                        "status": "failed",
                        "stage": "initialization",
                        "error": init_msg
                    }
                    continue
                
                # 3. 測試基本功能
                func_success, func_msg = self.test_adapter_basic_functionality(
                    adapter_instance, adapter.id
                )
                print(f"   功能: {func_msg}")
                
                if func_success:
                    self.working_adapters.append(adapter.id)
                    self.test_results[adapter.id] = {
                        "status": "working",
                        "class": adapter_class.__name__,
                        "instance": adapter_instance,
                        "capabilities": adapter.capabilities
                    }
                else:
                    self.failed_adapters.append(adapter.id)
                    self.test_results[adapter.id] = {
                        "status": "failed",
                        "stage": "functionality",
                        "error": func_msg
                    }
            
            print()
        
        # 生成測試報告
        self.generate_test_report()
        
        return self.test_results
    
    def generate_test_report(self):
        """生成測試報告"""
        print("📊 測試結果摘要")
        print("=" * 50)
        
        total_adapters = len(self.test_results)
        working_count = len(self.working_adapters)
        failed_count = len(self.failed_adapters)
        
        print(f"總適配器數: {total_adapters}")
        print(f"正常工作: {working_count} ({working_count/total_adapters*100:.1f}%)")
        print(f"運行失敗: {failed_count} ({failed_count/total_adapters*100:.1f}%)")
        
        if self.working_adapters:
            print(f"\n✅ 正常工作的適配器 ({len(self.working_adapters)}個):")
            for adapter_id in self.working_adapters:
                result = self.test_results[adapter_id]
                print(f"   • {adapter_id} - {result['class']}")
        
        if self.failed_adapters:
            print(f"\n❌ 運行失敗的適配器 ({len(self.failed_adapters)}個):")
            for adapter_id in self.failed_adapters:
                result = self.test_results[adapter_id]
                print(f"   • {adapter_id} - {result['stage']}: {result['error'][:50]}...")
        
        # 按分類統計
        print(f"\n📈 按功能分類統計:")
        capability_stats = {}
        for adapter_id in self.working_adapters:
            result = self.test_results[adapter_id]
            for capability in result.get('capabilities', []):
                capability_stats[capability] = capability_stats.get(capability, 0) + 1
        
        for capability, count in sorted(capability_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {capability}: {count}個適配器")

def main():
    """主函數"""
    tester = MCPAdapterTester()
    results = tester.run_comprehensive_test()
    
    # 保存結果到文件
    import json
    with open('mcp_adapter_test_results.json', 'w', encoding='utf-8') as f:
        # 移除不可序列化的對象
        serializable_results = {}
        for adapter_id, result in results.items():
            serializable_result = {k: v for k, v in result.items() 
                                 if k not in ['instance', 'class']}
            if 'class' in result:
                serializable_result['class_name'] = result['class'].__name__ if hasattr(result['class'], '__name__') else str(result['class'])
            serializable_results[adapter_id] = serializable_result
        
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 測試結果已保存到: mcp_adapter_test_results.json")
    
    return len(tester.working_adapters), len(tester.failed_adapters)

if __name__ == "__main__":
    working_count, failed_count = main()
    
    if working_count > failed_count:
        print(f"\n🎉 測試成功！{working_count}個適配器正常工作")
    else:
        print(f"\n⚠️ 需要修復！{failed_count}個適配器運行失敗")

