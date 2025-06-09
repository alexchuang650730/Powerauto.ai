#!/usr/bin/env python3
"""
MCP標準化測試框架
提供統一的MCP適配器標準化測試和驗證功能

包括：
- 接口標準化測試
- 響應格式標準化
- 錯誤處理標準化
- 能力聲明標準化
- 文檔標準化
"""

import sys
import os
import json
import time
import logging
import inspect
import importlib
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class StandardTestResult:
    """標準化測試結果"""
    test_name: str
    adapter_name: str
    passed: bool
    score: float
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    execution_time: float

@dataclass
class MCPStandard:
    """MCP標準定義"""
    interface_methods: List[str]
    response_format: Dict[str, Any]
    error_codes: Dict[int, str]
    capability_format: Dict[str, Any]
    documentation_requirements: List[str]

class MCPStandardizedTestFramework:
    """MCP標準化測試框架"""
    
    def __init__(self):
        self.test_results = []
        self.standards = self._load_mcp_standards()
        self.adapters_registry = {}
        
        # 測試統計
        self.stats = {
            "total_adapters": 0,
            "tested_adapters": 0,
            "passed_adapters": 0,
            "failed_adapters": 0,
            "overall_compliance": 0.0,
            "test_categories": {
                "interface_standardization": {"passed": 0, "total": 0},
                "response_format": {"passed": 0, "total": 0},
                "error_handling": {"passed": 0, "total": 0},
                "capability_declaration": {"passed": 0, "total": 0},
                "documentation": {"passed": 0, "total": 0}
            }
        }
    
    def _load_mcp_standards(self) -> MCPStandard:
        """載入MCP標準定義"""
        return MCPStandard(
            interface_methods=[
                "process",
                "get_capabilities", 
                "get_status",
                "initialize",
                "cleanup"
            ],
            response_format={
                "status": str,
                "data": [dict, list, str, int, float, bool, type(None)],
                "message": str,
                "metadata": dict,
                "timestamp": str
            },
            error_codes={
                -32700: "Parse error",
                -32600: "Invalid Request", 
                -32601: "Method not found",
                -32602: "Invalid params",
                -32603: "Internal error",
                -32000: "Server error"
            },
            capability_format={
                "name": str,
                "version": str,
                "description": str,
                "capabilities": list,
                "supported_operations": list,
                "metadata": dict
            },
            documentation_requirements=[
                "README.md",
                "API documentation",
                "Usage examples",
                "Error handling guide"
            ]
        )
    
    def discover_adapters(self) -> Dict[str, Any]:
        """發現所有MCP適配器"""
        adapters = {}
        
        try:
            # 從註冊表發現適配器
            from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
            registry = SafeMCPRegistry()
            registered_adapters = registry.list_adapters()
            
            for adapter_name, adapter_info in registered_adapters.items():
                adapters[adapter_name] = {
                    "name": adapter_name,
                    "type": adapter_info.get("type", "unknown"),
                    "instance": adapter_info.get("instance"),
                    "metadata": adapter_info.get("metadata", {})
                }
                
        except Exception as e:
            logger.warning(f"無法從註冊表發現適配器: {e}")
        
        # 從文件系統發現適配器
        adapters_dir = project_root / "mcptool" / "adapters"
        if adapters_dir.exists():
            for adapter_file in adapters_dir.rglob("*_mcp.py"):
                adapter_name = adapter_file.stem
                if adapter_name not in adapters:
                    adapters[adapter_name] = {
                        "name": adapter_name,
                        "type": "file_based",
                        "path": str(adapter_file),
                        "metadata": {}
                    }
        
        self.adapters_registry = adapters
        self.stats["total_adapters"] = len(adapters)
        
        logger.info(f"發現 {len(adapters)} 個MCP適配器")
        return adapters
    
    def test_interface_standardization(self, adapter_name: str, adapter_instance: Any) -> StandardTestResult:
        """測試接口標準化"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        # 檢查必需方法
        missing_methods = []
        for method in self.standards.interface_methods:
            if not hasattr(adapter_instance, method):
                missing_methods.append(method)
        
        if missing_methods:
            errors.append(f"缺少必需方法: {missing_methods}")
        
        # 檢查方法簽名
        method_signatures = {}
        for method in self.standards.interface_methods:
            if hasattr(adapter_instance, method):
                try:
                    sig = inspect.signature(getattr(adapter_instance, method))
                    method_signatures[method] = str(sig)
                except Exception as e:
                    warnings.append(f"無法檢查方法 {method} 的簽名: {e}")
        
        details["method_signatures"] = method_signatures
        details["missing_methods"] = missing_methods
        
        # 計算分數
        total_methods = len(self.standards.interface_methods)
        implemented_methods = total_methods - len(missing_methods)
        score = implemented_methods / total_methods if total_methods > 0 else 0
        
        execution_time = time.time() - start_time
        
        return StandardTestResult(
            test_name="Interface Standardization",
            adapter_name=adapter_name,
            passed=len(missing_methods) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            details=details,
            execution_time=execution_time
        )
    
    def test_response_format(self, adapter_name: str, adapter_instance: Any) -> StandardTestResult:
        """測試響應格式標準化"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        # 測試process方法的響應格式
        if hasattr(adapter_instance, 'process'):
            try:
                # 使用簡單的測試輸入
                test_input = {"test": "standardization"}
                response = adapter_instance.process(test_input)
                
                # 檢查響應格式
                format_issues = self._validate_response_format(response)
                if format_issues:
                    errors.extend(format_issues)
                
                details["sample_response"] = response
                details["response_type"] = type(response).__name__
                
            except Exception as e:
                errors.append(f"process方法執行失敗: {str(e)}")
        else:
            errors.append("缺少process方法")
        
        # 測試get_capabilities方法的響應格式
        if hasattr(adapter_instance, 'get_capabilities'):
            try:
                capabilities = adapter_instance.get_capabilities()
                capability_issues = self._validate_capability_format(capabilities)
                if capability_issues:
                    warnings.extend(capability_issues)
                
                details["capabilities"] = capabilities
                
            except Exception as e:
                warnings.append(f"get_capabilities方法執行失敗: {str(e)}")
        
        # 計算分數
        score = 1.0 if len(errors) == 0 else 0.5 if len(warnings) == 0 else 0.0
        
        execution_time = time.time() - start_time
        
        return StandardTestResult(
            test_name="Response Format",
            adapter_name=adapter_name,
            passed=len(errors) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            details=details,
            execution_time=execution_time
        )
    
    def test_error_handling(self, adapter_name: str, adapter_instance: Any) -> StandardTestResult:
        """測試錯誤處理標準化"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        error_test_cases = [
            {"input": None, "expected": "處理None輸入"},
            {"input": {}, "expected": "處理空字典"},
            {"input": {"invalid": "data"}, "expected": "處理無效數據"},
            {"input": "invalid_string", "expected": "處理無效字符串"}
        ]
        
        error_handling_results = []
        
        if hasattr(adapter_instance, 'process'):
            for test_case in error_test_cases:
                try:
                    response = adapter_instance.process(test_case["input"])
                    
                    # 檢查是否正確處理錯誤
                    if isinstance(response, dict):
                        if response.get("status") == "error":
                            error_handling_results.append({
                                "test": test_case["expected"],
                                "passed": True,
                                "response": response
                            })
                        else:
                            error_handling_results.append({
                                "test": test_case["expected"],
                                "passed": False,
                                "response": response,
                                "issue": "未返回錯誤狀態"
                            })
                    else:
                        warnings.append(f"錯誤處理測試 '{test_case['expected']}' 返回非字典響應")
                        
                except Exception as e:
                    # 拋出異常也是一種錯誤處理方式
                    error_handling_results.append({
                        "test": test_case["expected"],
                        "passed": True,
                        "exception": str(e)
                    })
        else:
            errors.append("缺少process方法，無法測試錯誤處理")
        
        details["error_handling_results"] = error_handling_results
        
        # 計算分數
        if error_handling_results:
            passed_tests = sum(1 for result in error_handling_results if result["passed"])
            score = passed_tests / len(error_handling_results)
        else:
            score = 0.0
        
        execution_time = time.time() - start_time
        
        return StandardTestResult(
            test_name="Error Handling",
            adapter_name=adapter_name,
            passed=score >= 0.8,
            score=score,
            errors=errors,
            warnings=warnings,
            details=details,
            execution_time=execution_time
        )
    
    def test_capability_declaration(self, adapter_name: str, adapter_instance: Any) -> StandardTestResult:
        """測試能力聲明標準化"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        if hasattr(adapter_instance, 'get_capabilities'):
            try:
                capabilities = adapter_instance.get_capabilities()
                
                # 驗證能力聲明格式
                format_issues = self._validate_capability_format(capabilities)
                if format_issues:
                    errors.extend(format_issues)
                
                # 檢查能力聲明的完整性
                if isinstance(capabilities, list):
                    details["capabilities_count"] = len(capabilities)
                    details["capabilities_list"] = capabilities
                elif isinstance(capabilities, dict):
                    details["capabilities_keys"] = list(capabilities.keys())
                    details["capabilities_dict"] = capabilities
                else:
                    errors.append(f"能力聲明應該是list或dict，實際是: {type(capabilities)}")
                
            except Exception as e:
                errors.append(f"get_capabilities方法執行失敗: {str(e)}")
        else:
            errors.append("缺少get_capabilities方法")
        
        # 檢查是否有文檔說明能力
        if hasattr(adapter_instance, '__doc__') and adapter_instance.__doc__:
            details["has_documentation"] = True
            details["doc_length"] = len(adapter_instance.__doc__)
        else:
            warnings.append("缺少類文檔說明")
        
        # 計算分數
        score = 1.0 if len(errors) == 0 else 0.5 if len(warnings) == 0 else 0.0
        
        execution_time = time.time() - start_time
        
        return StandardTestResult(
            test_name="Capability Declaration",
            adapter_name=adapter_name,
            passed=len(errors) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            details=details,
            execution_time=execution_time
        )
    
    def test_documentation_standards(self, adapter_name: str, adapter_info: Dict[str, Any]) -> StandardTestResult:
        """測試文檔標準化"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        # 檢查適配器文件的文檔
        if "path" in adapter_info:
            adapter_path = Path(adapter_info["path"])
            
            # 檢查是否有README文件
            readme_files = list(adapter_path.parent.glob("README*"))
            if readme_files:
                details["readme_files"] = [str(f) for f in readme_files]
            else:
                warnings.append("缺少README文檔")
            
            # 檢查代碼文檔
            try:
                with open(adapter_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 檢查模塊文檔字符串
                if '"""' in content or "'''" in content:
                    details["has_module_docstring"] = True
                else:
                    warnings.append("缺少模塊文檔字符串")
                
                # 檢查類和方法文檔
                docstring_count = content.count('"""') + content.count("'''")
                details["docstring_count"] = docstring_count
                
                if docstring_count < 2:
                    warnings.append("文檔字符串數量不足")
                    
            except Exception as e:
                errors.append(f"無法讀取適配器文件: {e}")
        
        # 計算分數
        score = 1.0 if len(errors) == 0 and len(warnings) <= 1 else 0.5 if len(errors) == 0 else 0.0
        
        execution_time = time.time() - start_time
        
        return StandardTestResult(
            test_name="Documentation Standards",
            adapter_name=adapter_name,
            passed=len(errors) == 0 and len(warnings) <= 1,
            score=score,
            errors=errors,
            warnings=warnings,
            details=details,
            execution_time=execution_time
        )
    
    def _validate_response_format(self, response: Any) -> List[str]:
        """驗證響應格式"""
        issues = []
        
        if not isinstance(response, dict):
            issues.append(f"響應應該是字典，實際是: {type(response)}")
            return issues
        
        # 檢查必需字段
        required_fields = ["status"]
        for field in required_fields:
            if field not in response:
                issues.append(f"響應缺少必需字段: {field}")
        
        # 檢查字段類型
        if "status" in response and not isinstance(response["status"], str):
            issues.append(f"status字段應該是字符串，實際是: {type(response['status'])}")
        
        if "data" in response:
            data_type = type(response["data"])
            valid_types = (dict, list, str, int, float, bool, type(None))
            if not isinstance(response["data"], valid_types):
                issues.append(f"data字段類型無效: {data_type}")
        
        return issues
    
    def _validate_capability_format(self, capabilities: Any) -> List[str]:
        """驗證能力聲明格式"""
        issues = []
        
        if not isinstance(capabilities, (list, dict)):
            issues.append(f"能力聲明應該是list或dict，實際是: {type(capabilities)}")
            return issues
        
        if isinstance(capabilities, list):
            for i, cap in enumerate(capabilities):
                if not isinstance(cap, str):
                    issues.append(f"能力項 {i} 應該是字符串，實際是: {type(cap)}")
        
        elif isinstance(capabilities, dict):
            if "name" not in capabilities:
                issues.append("能力聲明字典缺少name字段")
        
        return issues
    
    def run_standardization_tests(self, adapter_name: str = None) -> List[StandardTestResult]:
        """運行標準化測試"""
        logger.info("開始MCP標準化測試...")
        
        # 發現適配器
        adapters = self.discover_adapters()
        
        # 選擇要測試的適配器
        if adapter_name:
            if adapter_name not in adapters:
                logger.error(f"未找到適配器: {adapter_name}")
                return []
            test_adapters = {adapter_name: adapters[adapter_name]}
        else:
            test_adapters = adapters
        
        results = []
        
        for name, adapter_info in test_adapters.items():
            logger.info(f"測試適配器: {name}")
            
            # 獲取適配器實例
            adapter_instance = adapter_info.get("instance")
            if not adapter_instance:
                logger.warning(f"無法獲取適配器實例: {name}")
                continue
            
            # 運行各項標準化測試
            test_methods = [
                self.test_interface_standardization,
                self.test_response_format,
                self.test_error_handling,
                self.test_capability_declaration
            ]
            
            adapter_results = []
            for test_method in test_methods:
                try:
                    result = test_method(name, adapter_instance)
                    adapter_results.append(result)
                    results.append(result)
                    
                    # 更新統計
                    category = result.test_name.lower().replace(" ", "_")
                    if category in self.stats["test_categories"]:
                        self.stats["test_categories"][category]["total"] += 1
                        if result.passed:
                            self.stats["test_categories"][category]["passed"] += 1
                            
                except Exception as e:
                    logger.error(f"測試 {test_method.__name__} 失敗: {e}")
            
            # 文檔標準化測試
            try:
                doc_result = self.test_documentation_standards(name, adapter_info)
                adapter_results.append(doc_result)
                results.append(doc_result)
                
                self.stats["test_categories"]["documentation"]["total"] += 1
                if doc_result.passed:
                    self.stats["test_categories"]["documentation"]["passed"] += 1
                    
            except Exception as e:
                logger.error(f"文檔標準化測試失敗: {e}")
            
            # 計算適配器整體通過狀態
            adapter_passed = all(r.passed for r in adapter_results)
            if adapter_passed:
                self.stats["passed_adapters"] += 1
            else:
                self.stats["failed_adapters"] += 1
            
            self.stats["tested_adapters"] += 1
        
        # 計算整體合規性
        if self.stats["tested_adapters"] > 0:
            self.stats["overall_compliance"] = self.stats["passed_adapters"] / self.stats["tested_adapters"]
        
        self.test_results = results
        logger.info(f"標準化測試完成，測試了 {self.stats['tested_adapters']} 個適配器")
        
        return results
    
    def generate_standardization_report(self) -> str:
        """生成標準化測試報告"""
        report = f"""
# MCP標準化測試報告

## 📊 總體統計
- **測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **總適配器數**: {self.stats['total_adapters']}
- **已測試適配器**: {self.stats['tested_adapters']}
- **通過適配器**: {self.stats['passed_adapters']}
- **失敗適配器**: {self.stats['failed_adapters']}
- **整體合規性**: {self.stats['overall_compliance']:.1%}

## 📋 測試類別統計
"""
        
        for category, stats in self.stats["test_categories"].items():
            if stats["total"] > 0:
                pass_rate = stats["passed"] / stats["total"]
                status = "✅" if pass_rate >= 0.9 else "⚠️" if pass_rate >= 0.7 else "❌"
                report += f"- {status} **{category.replace('_', ' ').title()}**: {stats['passed']}/{stats['total']} ({pass_rate:.1%})\n"
        
        report += f"""
## 🔍 詳細測試結果

### 適配器測試結果
"""
        
        # 按適配器分組結果
        adapter_results = {}
        for result in self.test_results:
            if result.adapter_name not in adapter_results:
                adapter_results[result.adapter_name] = []
            adapter_results[result.adapter_name].append(result)
        
        for adapter_name, results in adapter_results.items():
            overall_passed = all(r.passed for r in results)
            status = "✅" if overall_passed else "❌"
            avg_score = sum(r.score for r in results) / len(results) if results else 0
            
            report += f"""
#### {status} {adapter_name} (平均分數: {avg_score:.1%})
"""
            
            for result in results:
                test_status = "✅" if result.passed else "❌"
                report += f"- {test_status} **{result.test_name}**: {result.score:.1%}"
                
                if result.errors:
                    report += f" - 錯誤: {len(result.errors)}個"
                if result.warnings:
                    report += f" - 警告: {len(result.warnings)}個"
                
                report += f" ({result.execution_time:.3f}s)\n"
                
                # 顯示主要錯誤
                for error in result.errors[:2]:
                    report += f"  - ⚠️ {error}\n"
        
        report += f"""
## 🎯 改進建議

### 高優先級
"""
        
        # 分析常見問題
        common_errors = {}
        for result in self.test_results:
            for error in result.errors:
                if error in common_errors:
                    common_errors[error] += 1
                else:
                    common_errors[error] = 1
        
        # 顯示最常見的錯誤
        sorted_errors = sorted(common_errors.items(), key=lambda x: x[1], reverse=True)
        for error, count in sorted_errors[:5]:
            report += f"- **{error}** (影響 {count} 個測試)\n"
        
        report += f"""
### 標準化改進
1. 統一接口方法實現
2. 標準化響應格式
3. 完善錯誤處理機制
4. 規範能力聲明格式
5. 補充文檔說明

## 📈 合規性評估

{'✅ 系統達到標準化要求' if self.stats['overall_compliance'] >= 0.9 else '⚠️ 系統需要改進以達到標準化要求' if self.stats['overall_compliance'] >= 0.7 else '❌ 系統未達到標準化要求'}

**整體合規性分數**: {self.stats['overall_compliance']:.1%}
"""
        
        return report

if __name__ == "__main__":
    framework = MCPStandardizedTestFramework()
    results = framework.run_standardization_tests()
    
    # 生成報告
    report = framework.generate_standardization_report()
    
    # 保存報告
    report_file = Path("mcp_standardization_test_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ MCP標準化測試完成")
    print(f"📄 報告已保存到: {report_file}")
    print(f"🎯 整體合規性: {framework.stats['overall_compliance']:.1%}")
    print(f"📊 測試結果: {framework.stats['passed_adapters']}/{framework.stats['tested_adapters']} 個適配器通過")

