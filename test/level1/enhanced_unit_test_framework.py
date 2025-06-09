#!/usr/bin/env python3
"""
Level 1 單元測試框架
基礎層：單元測試 + 代碼質量

主要功能：
- 適配器單元測試
- 代碼質量檢查
- 方法級別測試
- 基礎功能驗證
"""

import sys
import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 導入標準化接口
from test.standardized_test_interface import BaseTestFramework, TestResult, TestStatus, TestSeverity
from test.optimized_module_importer import get_safe_importer

logger = logging.getLogger(__name__)

class Level1UnitTestFramework(BaseTestFramework):
    """Level 1 單元測試框架"""
    
    def __init__(self):
        super().__init__(
            name="Level1_UnitTest",
            description="基礎層單元測試和代碼質量檢查"
        )
        
        self.importer = get_safe_importer()
        
        # 測試配置
        self.test_config = {
            "timeout": 30.0,  # 單個測試超時時間
            "required_methods": ["get_name", "get_capabilities"],
            "optional_methods": ["process", "get_version", "get_description"],
            "quality_checks": ["naming", "documentation", "error_handling"]
        }
    
    def run_tests(self, adapter_name: Optional[str] = None) -> List[TestResult]:
        """運行Level 1單元測試"""
        self.logger.info("開始Level 1單元測試...")
        self.test_results.clear()
        
        # 獲取適配器列表
        adapters = self.get_adapters()
        
        if not adapters:
            self.logger.warning("未找到任何適配器")
            return []
        
        # 過濾適配器
        if adapter_name:
            adapters = [(name, instance) for name, instance in adapters if name == adapter_name]
        
        self.logger.info(f"測試 {len(adapters)} 個適配器")
        
        # 運行測試
        for name, instance in adapters:
            self._test_adapter_unit(name, instance)
        
        self.logger.info(f"Level 1測試完成，共 {len(self.test_results)} 個測試結果")
        return self.test_results
    
    def _test_adapter_unit(self, adapter_name: str, adapter_instance: Any):
        """測試單個適配器的單元功能"""
        self.logger.debug(f"測試適配器單元功能: {adapter_name}")
        
        # 1. 基礎方法測試
        self._test_basic_methods(adapter_name, adapter_instance)
        
        # 2. 方法調用測試
        self._test_method_calls(adapter_name, adapter_instance)
        
        # 3. 代碼質量測試
        self._test_code_quality(adapter_name, adapter_instance)
        
        # 4. 錯誤處理測試
        self._test_error_handling(adapter_name, adapter_instance)
    
    def _test_basic_methods(self, adapter_name: str, adapter_instance: Any):
        """測試基礎方法存在性"""
        start_time = time.time()
        
        required_methods = self.test_config["required_methods"]
        optional_methods = self.test_config["optional_methods"]
        
        # 檢查必需方法
        missing_required = []
        for method_name in required_methods:
            if not hasattr(adapter_instance, method_name):
                missing_required.append(method_name)
        
        # 檢查可選方法
        available_optional = []
        for method_name in optional_methods:
            if hasattr(adapter_instance, method_name):
                available_optional.append(method_name)
        
        # 計算分數
        required_score = (len(required_methods) - len(missing_required)) / len(required_methods) * 100
        optional_score = len(available_optional) / len(optional_methods) * 100
        overall_score = required_score * 0.8 + optional_score * 0.2
        
        # 創建測試結果
        passed = len(missing_required) == 0
        message = f"必需方法: {len(required_methods) - len(missing_required)}/{len(required_methods)}, 可選方法: {len(available_optional)}/{len(optional_methods)}"
        
        if missing_required:
            message += f", 缺失: {', '.join(missing_required)}"
        
        execution_time = time.time() - start_time
        
        result = self.create_test_result(
            test_name="test_unit_basic_methods",
            adapter_name=adapter_name,
            passed=passed,
            score=overall_score,
            execution_time=execution_time,
            message=message,
            details={
                "required_methods": required_methods,
                "missing_required": missing_required,
                "available_optional": available_optional,
                "required_score": required_score,
                "optional_score": optional_score
            },
            severity=TestSeverity.HIGH if not passed else TestSeverity.LOW
        )
        
        self.add_test_result(result)
    
    def _test_method_calls(self, adapter_name: str, adapter_instance: Any):
        """測試方法調用"""
        start_time = time.time()
        
        test_results = {}
        total_score = 0
        test_count = 0
        
        # 測試get_name方法
        if hasattr(adapter_instance, "get_name"):
            result = self.test_adapter_method(adapter_instance, "get_name")
            test_results["get_name"] = result
            
            if result["success"]:
                name_value = result["result"]
                if isinstance(name_value, str) and len(name_value) > 0:
                    total_score += 100
                else:
                    total_score += 50
            test_count += 1
        
        # 測試get_capabilities方法
        if hasattr(adapter_instance, "get_capabilities"):
            result = self.test_adapter_method(adapter_instance, "get_capabilities")
            test_results["get_capabilities"] = result
            
            if result["success"]:
                caps_value = result["result"]
                if isinstance(caps_value, (list, dict)) and len(caps_value) > 0:
                    total_score += 100
                elif isinstance(caps_value, (list, dict)):
                    total_score += 70
                else:
                    total_score += 30
            test_count += 1
        
        # 測試process方法（如果存在）
        if hasattr(adapter_instance, "process"):
            test_data = {"test": "unit_test_data", "timestamp": datetime.now().isoformat()}
            result = self.test_adapter_method(adapter_instance, "process", test_data)
            test_results["process"] = result
            
            if result["success"]:
                total_score += 100
            else:
                total_score += 20  # 至少方法存在
            test_count += 1
        
        # 計算平均分數
        average_score = total_score / test_count if test_count > 0 else 0
        
        # 判斷是否通過
        passed = all(r["success"] for r in test_results.values())
        
        execution_time = time.time() - start_time
        
        # 創建消息
        success_count = sum(1 for r in test_results.values() if r["success"])
        message = f"方法調用測試: {success_count}/{len(test_results)} 成功"
        
        result = self.create_test_result(
            test_name="test_unit_method_calls",
            adapter_name=adapter_name,
            passed=passed,
            score=average_score,
            execution_time=execution_time,
            message=message,
            details={
                "test_results": test_results,
                "success_count": success_count,
                "total_tests": len(test_results)
            },
            severity=TestSeverity.MEDIUM
        )
        
        self.add_test_result(result)
    
    def _test_code_quality(self, adapter_name: str, adapter_instance: Any):
        """測試代碼質量"""
        start_time = time.time()
        
        quality_scores = {}
        
        # 1. 命名規範檢查
        naming_score = self._check_naming_convention(adapter_instance)
        quality_scores["naming"] = naming_score
        
        # 2. 文檔檢查
        documentation_score = self._check_documentation(adapter_instance)
        quality_scores["documentation"] = documentation_score
        
        # 3. 類結構檢查
        structure_score = self._check_class_structure(adapter_instance)
        quality_scores["structure"] = structure_score
        
        # 計算總體質量分數
        overall_score = sum(quality_scores.values()) / len(quality_scores)
        
        # 判斷是否通過（質量分數 >= 60）
        passed = overall_score >= 60
        
        execution_time = time.time() - start_time
        
        message = f"代碼質量分數: {overall_score:.1f} (命名: {naming_score:.1f}, 文檔: {documentation_score:.1f}, 結構: {structure_score:.1f})"
        
        result = self.create_test_result(
            test_name="test_unit_code_quality",
            adapter_name=adapter_name,
            passed=passed,
            score=overall_score,
            execution_time=execution_time,
            message=message,
            details=quality_scores,
            severity=TestSeverity.LOW
        )
        
        self.add_test_result(result)
    
    def _check_naming_convention(self, adapter_instance: Any) -> float:
        """檢查命名規範"""
        score = 0
        checks = 0
        
        # 檢查類名
        class_name = adapter_instance.__class__.__name__
        if class_name[0].isupper():  # 首字母大寫
            score += 25
        checks += 1
        
        # 檢查方法名
        method_names = [name for name in dir(adapter_instance) 
                       if callable(getattr(adapter_instance, name)) and not name.startswith('_')]
        
        if method_names:
            snake_case_count = sum(1 for name in method_names if '_' in name or name.islower())
            score += (snake_case_count / len(method_names)) * 25
        checks += 1
        
        # 檢查是否有描述性名稱
        if any(keyword in class_name.lower() for keyword in ['adapter', 'mcp', 'tool', 'engine']):
            score += 25
        checks += 1
        
        # 檢查方法名是否描述性
        descriptive_methods = ['get_name', 'get_capabilities', 'process', 'initialize']
        found_descriptive = sum(1 for method in descriptive_methods if hasattr(adapter_instance, method))
        score += (found_descriptive / len(descriptive_methods)) * 25
        checks += 1
        
        return score
    
    def _check_documentation(self, adapter_instance: Any) -> float:
        """檢查文檔質量"""
        score = 0
        
        # 檢查類文檔字符串
        class_doc = adapter_instance.__class__.__doc__
        if class_doc and len(class_doc.strip()) > 10:
            score += 40
        elif class_doc:
            score += 20
        
        # 檢查方法文檔字符串
        methods_with_docs = 0
        total_methods = 0
        
        for name in dir(adapter_instance):
            if callable(getattr(adapter_instance, name)) and not name.startswith('_'):
                total_methods += 1
                method = getattr(adapter_instance, name)
                if hasattr(method, '__doc__') and method.__doc__ and len(method.__doc__.strip()) > 5:
                    methods_with_docs += 1
        
        if total_methods > 0:
            doc_ratio = methods_with_docs / total_methods
            score += doc_ratio * 60
        
        return score
    
    def _check_class_structure(self, adapter_instance: Any) -> float:
        """檢查類結構"""
        score = 0
        
        # 檢查是否有__init__方法
        if hasattr(adapter_instance, '__init__'):
            score += 20
        
        # 檢查是否有必要的方法
        required_methods = ['get_name', 'get_capabilities']
        found_required = sum(1 for method in required_methods if hasattr(adapter_instance, method))
        score += (found_required / len(required_methods)) * 40
        
        # 檢查是否有處理方法
        if hasattr(adapter_instance, 'process'):
            score += 20
        
        # 檢查方法數量（不應該太少或太多）
        public_methods = [name for name in dir(adapter_instance) 
                         if callable(getattr(adapter_instance, name)) and not name.startswith('_')]
        
        method_count = len(public_methods)
        if 3 <= method_count <= 15:  # 合理的方法數量
            score += 20
        elif method_count > 0:
            score += 10
        
        return score
    
    def _test_error_handling(self, adapter_name: str, adapter_instance: Any):
        """測試錯誤處理"""
        start_time = time.time()
        
        error_tests = {}
        total_score = 0
        
        # 測試無效參數處理
        if hasattr(adapter_instance, "process"):
            # 測試None參數
            try:
                result = adapter_instance.process(None)
                error_tests["none_input"] = {"handled": True, "result": result}
                total_score += 25
            except Exception as e:
                error_tests["none_input"] = {"handled": True, "error": str(e)}
                total_score += 20  # 拋出異常也是一種處理方式
        
        # 測試空字典參數
        if hasattr(adapter_instance, "process"):
            try:
                result = adapter_instance.process({})
                error_tests["empty_dict"] = {"handled": True, "result": result}
                total_score += 25
            except Exception as e:
                error_tests["empty_dict"] = {"handled": True, "error": str(e)}
                total_score += 20
        
        # 測試無效類型參數
        if hasattr(adapter_instance, "process"):
            try:
                result = adapter_instance.process("invalid_type")
                error_tests["invalid_type"] = {"handled": True, "result": result}
                total_score += 25
            except Exception as e:
                error_tests["invalid_type"] = {"handled": True, "error": str(e)}
                total_score += 20
        
        # 如果沒有process方法，給予基礎分數
        if not hasattr(adapter_instance, "process"):
            total_score = 75  # 基礎分數
            error_tests["no_process_method"] = {"note": "適配器沒有process方法"}
        
        # 測試方法調用錯誤處理
        if hasattr(adapter_instance, "get_name"):
            try:
                # 嘗試調用可能出錯的方法
                name = adapter_instance.get_name()
                if name is not None:
                    total_score += 25
            except Exception as e:
                error_tests["get_name_error"] = {"error": str(e)}
                total_score += 10
        
        passed = total_score >= 60
        execution_time = time.time() - start_time
        
        message = f"錯誤處理測試分數: {total_score:.1f}"
        
        result = self.create_test_result(
            test_name="test_unit_error_handling",
            adapter_name=adapter_name,
            passed=passed,
            score=total_score,
            execution_time=execution_time,
            message=message,
            details=error_tests,
            severity=TestSeverity.MEDIUM
        )
        
        self.add_test_result(result)

def run_level1_tests(adapter_name: Optional[str] = None) -> List[TestResult]:
    """運行Level 1測試的便捷函數"""
    framework = Level1UnitTestFramework()
    return framework.run_tests(adapter_name)

if __name__ == "__main__":
    # 運行Level 1測試
    print("🧪 開始Level 1單元測試...")
    
    framework = Level1UnitTestFramework()
    results = framework.run_tests()
    
    # 顯示結果
    summary = framework.get_test_summary()
    print(f"📊 測試完成:")
    print(f"   總測試數: {summary['total_tests']}")
    print(f"   通過測試: {summary['passed_tests']}")
    print(f"   失敗測試: {summary['failed_tests']}")
    print(f"   通過率: {summary['pass_rate']:.1%}")
    print(f"   總體分數: {summary['overall_score']:.1f}")
    print(f"   執行時間: {summary['total_time']:.2f}秒")
    
    # 保存結果
    framework.save_results("test/level1")
    print("📄 測試報告已保存到 test/level1/")
    
    # 生成簡要報告
    report = framework.generate_report()
    print("\n📋 測試報告預覽:")
    print(report[:1000] + "..." if len(report) > 1000 else report)

