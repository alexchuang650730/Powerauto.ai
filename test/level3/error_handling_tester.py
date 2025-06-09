#!/usr/bin/env python3
"""
MCP錯誤處理測試模組
全面測試MCP適配器的錯誤處理機制和異常情況處理

包括：
- 異常輸入處理測試
- 錯誤恢復機制測試
- 超時處理測試
- 資源不足處理測試
- 網絡錯誤處理測試
- 錯誤碼標準化測試
"""

import sys
import os
import time
import json
import logging
import threading
import signal
from typing import Dict, Any, List, Optional, Callable, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import traceback

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class ErrorTestCase:
    """錯誤測試用例"""
    name: str
    description: str
    input_data: Any
    expected_behavior: str
    error_type: str
    severity: str  # low, medium, high, critical

@dataclass
class ErrorHandlingResult:
    """錯誤處理測試結果"""
    test_case: str
    adapter_name: str
    passed: bool
    error_handled: bool
    error_type: str
    response: Any
    execution_time: float
    details: Dict[str, Any]

class MCPErrorHandlingTester:
    """MCP錯誤處理測試器"""
    
    def __init__(self):
        self.test_results = []
        self.error_test_cases = self._create_error_test_cases()
        self.timeout_duration = 10  # 秒
        
    def _create_error_test_cases(self) -> List[ErrorTestCase]:
        """創建錯誤測試用例"""
        return [
            # 輸入驗證錯誤
            ErrorTestCase(
                name="null_input",
                description="測試None輸入處理",
                input_data=None,
                expected_behavior="應該返回錯誤響應或拋出適當異常",
                error_type="validation_error",
                severity="high"
            ),
            ErrorTestCase(
                name="empty_dict",
                description="測試空字典輸入",
                input_data={},
                expected_behavior="應該處理空輸入並返回適當響應",
                error_type="validation_error",
                severity="medium"
            ),
            ErrorTestCase(
                name="invalid_type",
                description="測試無效數據類型",
                input_data="invalid_string_input",
                expected_behavior="應該驗證輸入類型並返回錯誤",
                error_type="type_error",
                severity="high"
            ),
            ErrorTestCase(
                name="malformed_json",
                description="測試格式錯誤的JSON數據",
                input_data='{"invalid": json, "missing": quote}',
                expected_behavior="應該處理JSON解析錯誤",
                error_type="parse_error",
                severity="medium"
            ),
            
            # 邏輯錯誤
            ErrorTestCase(
                name="missing_required_field",
                description="測試缺少必需字段",
                input_data={"incomplete": "data"},
                expected_behavior="應該檢查必需字段並返回錯誤",
                error_type="validation_error",
                severity="high"
            ),
            ErrorTestCase(
                name="invalid_field_value",
                description="測試無效字段值",
                input_data={"field": -999, "invalid_range": True},
                expected_behavior="應該驗證字段值範圍",
                error_type="validation_error",
                severity="medium"
            ),
            
            # 資源錯誤
            ErrorTestCase(
                name="large_data_input",
                description="測試大數據輸入處理",
                input_data={"large_data": "x" * 1000000},  # 1MB字符串
                expected_behavior="應該處理大數據或返回資源限制錯誤",
                error_type="resource_error",
                severity="medium"
            ),
            ErrorTestCase(
                name="recursive_data",
                description="測試遞歸數據結構",
                input_data=None,  # 將在測試時創建遞歸結構
                expected_behavior="應該檢測並處理遞歸數據",
                error_type="structure_error",
                severity="low"
            ),
            
            # 併發錯誤
            ErrorTestCase(
                name="concurrent_access",
                description="測試併發訪問處理",
                input_data={"concurrent_test": True},
                expected_behavior="應該正確處理併發請求",
                error_type="concurrency_error",
                severity="high"
            ),
            
            # 超時錯誤
            ErrorTestCase(
                name="timeout_simulation",
                description="測試超時處理",
                input_data={"simulate_delay": 15},  # 模擬15秒延遲
                expected_behavior="應該在合理時間內響應或超時",
                error_type="timeout_error",
                severity="high"
            )
        ]
    
    @contextmanager
    def timeout_context(self, seconds: int):
        """超時上下文管理器"""
        def timeout_handler(signum, frame):
            raise TimeoutError(f"操作超時 ({seconds}秒)")
        
        # 設置信號處理器
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def create_recursive_data(self, depth: int = 5) -> Dict[str, Any]:
        """創建遞歸數據結構"""
        if depth <= 0:
            return {"end": True}
        
        data = {
            "level": depth,
            "data": "test_data",
            "nested": self.create_recursive_data(depth - 1)
        }
        
        # 創建循環引用
        if depth == 5:
            data["self_reference"] = data
        
        return data
    
    def test_error_handling(self, adapter_name: str, adapter_instance: Any, test_case: ErrorTestCase) -> ErrorHandlingResult:
        """測試單個錯誤處理用例"""
        start_time = time.time()
        
        # 準備測試數據
        input_data = test_case.input_data
        if test_case.name == "recursive_data":
            input_data = self.create_recursive_data()
        
        details = {
            "test_case_name": test_case.name,
            "test_description": test_case.description,
            "input_type": type(input_data).__name__,
            "expected_behavior": test_case.expected_behavior
        }
        
        error_handled = False
        response = None
        passed = False
        
        try:
            # 根據測試用例類型選擇不同的測試方法
            if test_case.name == "timeout_simulation":
                # 超時測試
                with self.timeout_context(self.timeout_duration):
                    if hasattr(adapter_instance, 'process'):
                        response = adapter_instance.process(input_data)
                    else:
                        response = {"error": "No process method"}
                        
            elif test_case.name == "concurrent_access":
                # 併發測試
                response = self._test_concurrent_access(adapter_instance, input_data)
                
            else:
                # 普通錯誤處理測試
                if hasattr(adapter_instance, 'process'):
                    response = adapter_instance.process(input_data)
                else:
                    response = {"error": "No process method available"}
            
            # 分析響應
            if isinstance(response, dict):
                if "error" in response or response.get("status") == "error":
                    error_handled = True
                    passed = True
                    details["error_response"] = response
                elif response.get("status") == "success":
                    # 某些情況下成功處理也是正確的
                    if test_case.severity in ["low", "medium"]:
                        passed = True
                        details["success_response"] = response
                else:
                    details["unexpected_response"] = response
            else:
                details["non_dict_response"] = str(response)
                
        except TimeoutError as e:
            error_handled = True
            passed = True
            details["timeout_handled"] = str(e)
            response = {"error": "timeout", "message": str(e)}
            
        except Exception as e:
            error_handled = True
            # 對於高嚴重性錯誤，拋出異常是可接受的
            if test_case.severity in ["high", "critical"]:
                passed = True
            details["exception_type"] = type(e).__name__
            details["exception_message"] = str(e)
            details["traceback"] = traceback.format_exc()
            response = {"error": "exception", "type": type(e).__name__, "message": str(e)}
        
        execution_time = time.time() - start_time
        
        return ErrorHandlingResult(
            test_case=test_case.name,
            adapter_name=adapter_name,
            passed=passed,
            error_handled=error_handled,
            error_type=test_case.error_type,
            response=response,
            execution_time=execution_time,
            details=details
        )
    
    def _test_concurrent_access(self, adapter_instance: Any, input_data: Any) -> Dict[str, Any]:
        """測試併發訪問"""
        results = []
        errors = []
        
        def worker():
            try:
                if hasattr(adapter_instance, 'process'):
                    result = adapter_instance.process(input_data)
                    results.append(result)
                else:
                    results.append({"error": "No process method"})
            except Exception as e:
                errors.append(str(e))
        
        # 創建多個併發線程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join(timeout=5)
        
        return {
            "concurrent_results": len(results),
            "concurrent_errors": len(errors),
            "total_threads": len(threads),
            "success_rate": len(results) / len(threads) if threads else 0,
            "errors": errors[:3]  # 只保留前3個錯誤
        }
    
    def test_error_recovery(self, adapter_name: str, adapter_instance: Any) -> List[ErrorHandlingResult]:
        """測試錯誤恢復機制"""
        logger.info(f"測試錯誤恢復機制: {adapter_name}")
        
        recovery_results = []
        
        # 先觸發一個錯誤
        error_input = {"trigger_error": True, "invalid_data": None}
        
        try:
            if hasattr(adapter_instance, 'process'):
                error_response = adapter_instance.process(error_input)
        except Exception:
            pass  # 預期的錯誤
        
        # 然後測試是否能正常恢復
        normal_input = {"test": "recovery", "data": "normal_operation"}
        
        start_time = time.time()
        recovery_successful = False
        
        try:
            if hasattr(adapter_instance, 'process'):
                recovery_response = adapter_instance.process(normal_input)
                if isinstance(recovery_response, dict) and recovery_response.get("status") != "error":
                    recovery_successful = True
        except Exception as e:
            recovery_response = {"error": str(e)}
        
        execution_time = time.time() - start_time
        
        recovery_result = ErrorHandlingResult(
            test_case="error_recovery",
            adapter_name=adapter_name,
            passed=recovery_successful,
            error_handled=True,
            error_type="recovery_test",
            response=recovery_response,
            execution_time=execution_time,
            details={
                "description": "測試錯誤後的恢復能力",
                "recovery_successful": recovery_successful
            }
        )
        
        recovery_results.append(recovery_result)
        return recovery_results
    
    def run_error_handling_tests(self, adapter_name: str = None) -> List[ErrorHandlingResult]:
        """運行錯誤處理測試"""
        logger.info("開始MCP錯誤處理測試...")
        
        # 發現適配器
        try:
            from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
            registry = SafeMCPRegistry()
            adapters = registry.list_adapters()
            
            # 轉換為字典格式
            adapter_dict = {}
            if isinstance(adapters, list):
                for item in adapters:
                    if isinstance(item, tuple) and len(item) >= 2:
                        name, instance = item[0], item[1]
                        adapter_dict[name] = {"name": name, "instance": instance}
                    elif hasattr(item, 'name'):
                        adapter_dict[item.name] = {"name": item.name, "instance": item}
            elif isinstance(adapters, dict):
                adapter_dict = adapters
                
        except Exception as e:
            logger.error(f"無法從註冊表獲取適配器: {e}")
            return []
        
        # 選擇要測試的適配器
        if adapter_name:
            if adapter_name not in adapter_dict:
                logger.error(f"未找到適配器: {adapter_name}")
                return []
            test_adapters = {adapter_name: adapter_dict[adapter_name]}
        else:
            # 限制測試數量
            test_adapters = dict(list(adapter_dict.items())[:3])
        
        results = []
        
        for name, adapter_info in test_adapters.items():
            adapter_instance = adapter_info.get("instance")
            if not adapter_instance:
                logger.warning(f"無法獲取適配器實例: {name}")
                continue
            
            logger.info(f"測試適配器錯誤處理: {name}")
            
            # 運行所有錯誤測試用例
            for test_case in self.error_test_cases:
                try:
                    result = self.test_error_handling(name, adapter_instance, test_case)
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"錯誤處理測試失敗 {name}/{test_case.name}: {e}")
            
            # 測試錯誤恢復
            try:
                recovery_results = self.test_error_recovery(name, adapter_instance)
                results.extend(recovery_results)
            except Exception as e:
                logger.error(f"錯誤恢復測試失敗 {name}: {e}")
        
        self.test_results = results
        logger.info(f"錯誤處理測試完成，測試了 {len(test_adapters)} 個適配器")
        
        return results
    
    def generate_error_handling_report(self) -> str:
        """生成錯誤處理測試報告"""
        if not self.test_results:
            return "# MCP錯誤處理測試報告\n\n無測試結果可用。"
        
        # 統計信息
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        error_handled_tests = sum(1 for r in self.test_results if r.error_handled)
        
        # 按適配器分組
        adapter_results = {}
        for result in self.test_results:
            if result.adapter_name not in adapter_results:
                adapter_results[result.adapter_name] = []
            adapter_results[result.adapter_name].append(result)
        
        # 按錯誤類型分組
        error_type_stats = {}
        for result in self.test_results:
            error_type = result.error_type
            if error_type not in error_type_stats:
                error_type_stats[error_type] = {"total": 0, "passed": 0, "handled": 0}
            error_type_stats[error_type]["total"] += 1
            if result.passed:
                error_type_stats[error_type]["passed"] += 1
            if result.error_handled:
                error_type_stats[error_type]["handled"] += 1
        
        report = f"""
# MCP錯誤處理測試報告

## 📊 總體統計
- **測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **總測試數**: {total_tests}
- **通過測試數**: {passed_tests}
- **錯誤處理數**: {error_handled_tests}
- **通過率**: {(passed_tests/total_tests*100):.1f}%
- **錯誤處理率**: {(error_handled_tests/total_tests*100):.1f}%

## 📋 錯誤類型統計
"""
        
        for error_type, stats in error_type_stats.items():
            pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            handle_rate = (stats["handled"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 60 else "❌"
            
            report += f"- {status} **{error_type}**: {stats['passed']}/{stats['total']} 通過 ({pass_rate:.1f}%), {stats['handled']}/{stats['total']} 處理 ({handle_rate:.1f}%)\n"
        
        report += f"""
## 🔍 適配器測試結果
"""
        
        for adapter_name, results in adapter_results.items():
            adapter_passed = sum(1 for r in results if r.passed)
            adapter_total = len(results)
            adapter_pass_rate = (adapter_passed / adapter_total * 100) if adapter_total > 0 else 0
            status = "✅" if adapter_pass_rate >= 80 else "⚠️" if adapter_pass_rate >= 60 else "❌"
            
            report += f"""
### {status} {adapter_name} ({adapter_passed}/{adapter_total} 通過, {adapter_pass_rate:.1f}%)
"""
            
            for result in results:
                test_status = "✅" if result.passed else "❌"
                error_status = "🛡️" if result.error_handled else "⚠️"
                
                report += f"- {test_status} {error_status} **{result.test_case}** ({result.execution_time:.3f}s)\n"
                
                if not result.passed and result.details:
                    if "exception_message" in result.details:
                        report += f"  - 異常: {result.details['exception_message']}\n"
                    elif "unexpected_response" in result.details:
                        report += f"  - 意外響應: {result.details['unexpected_response']}\n"
        
        report += f"""
## 🎯 錯誤處理標準

### 測試用例說明
"""
        
        for test_case in self.error_test_cases:
            severity_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
            icon = severity_icon.get(test_case.severity, "⚪")
            
            report += f"- {icon} **{test_case.name}** ({test_case.severity}): {test_case.description}\n"
        
        report += f"""
### 評估標準
- **通過**: 正確處理錯誤並返回適當響應
- **錯誤處理**: 檢測到錯誤並採取適當行動
- **失敗**: 未能正確處理錯誤或產生意外行為

## 📈 改進建議

### 高優先級改進
"""
        
        # 分析常見問題
        failed_tests = [r for r in self.test_results if not r.passed]
        if failed_tests:
            common_failures = {}
            for result in failed_tests:
                test_case = result.test_case
                if test_case in common_failures:
                    common_failures[test_case] += 1
                else:
                    common_failures[test_case] = 1
            
            sorted_failures = sorted(common_failures.items(), key=lambda x: x[1], reverse=True)
            for test_case, count in sorted_failures[:5]:
                report += f"1. 改進 **{test_case}** 錯誤處理 (影響 {count} 個適配器)\n"
        
        report += f"""
### 錯誤處理最佳實踐
1. 實施統一的錯誤響應格式
2. 添加輸入驗證和清理機制
3. 實施超時和資源限制
4. 提供詳細的錯誤信息和恢復建議
5. 建立錯誤監控和告警機制

## 🏆 合規性評估

{'✅ 錯誤處理達到合規要求' if (passed_tests/total_tests) >= 0.8 else '⚠️ 錯誤處理需要改進' if (passed_tests/total_tests) >= 0.6 else '❌ 錯誤處理未達到合規要求'}

**整體通過率**: {(passed_tests/total_tests*100):.1f}%
**錯誤處理率**: {(error_handled_tests/total_tests*100):.1f}%
"""
        
        return report

if __name__ == "__main__":
    tester = MCPErrorHandlingTester()
    results = tester.run_error_handling_tests()
    
    # 生成報告
    report = tester.generate_error_handling_report()
    
    # 保存報告
    report_file = Path("mcp_error_handling_test_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ MCP錯誤處理測試完成")
    print(f"📄 報告已保存到: {report_file}")
    if results:
        passed_count = sum(1 for r in results if r.passed)
        handled_count = sum(1 for r in results if r.error_handled)
        print(f"🎯 測試結果: {passed_count}/{len(results)} 個測試通過")
        print(f"🛡️ 錯誤處理: {handled_count}/{len(results)} 個錯誤被正確處理")
    else:
        print("⚠️ 未找到可測試的適配器")

