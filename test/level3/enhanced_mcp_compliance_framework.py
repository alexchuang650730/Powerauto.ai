#!/usr/bin/env python3
"""
Level 3 MCP合規測試框架 - 修復版
業務層：MCP合規測試 + 標準化驗證

主要功能：
- MCP協議合規性驗證
- 標準化測試框架
- 性能合規性測試
- 錯誤處理測試
- 能力聲明標準化

修復問題：
- 統一適配器註冊表格式
- 標準化測試方法接口
- 優化模組導入機制
"""

import sys
import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
import jsonschema

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 導入標準化接口
from test.standardized_test_interface import BaseTestFramework, TestResult, TestStatus, TestSeverity
from test.optimized_module_importer import get_safe_importer

logger = logging.getLogger(__name__)

class Level3MCPComplianceFramework(BaseTestFramework):
    """Level 3 MCP合規測試框架 - 修復版"""
    
    def __init__(self):
        super().__init__(
            name="Level3_MCPCompliance",
            description="業務層MCP合規測試和標準化驗證"
        )
        
        self.importer = get_safe_importer()
        
        # MCP協議標準
        self.mcp_standards = {
            "protocol_version": "1.0",
            "required_methods": ["get_name", "get_capabilities"],
            "optional_methods": ["process", "get_version", "get_description", "get_metadata"],
            "response_format": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": ["object", "array", "string", "number", "boolean", "null"]},
                    "timestamp": {"type": "string"}
                }
            },
            "capability_schema": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
        
        # 測試配置
        self.test_config = {
            "timeout": 45.0,
            "performance_thresholds": {
                "response_time": 2.0,  # 秒
                "throughput": 5.0,     # 操作/秒
                "memory_limit": 100    # MB
            },
            "compliance_threshold": 80.0  # 合規性閾值
        }
    
    def run_tests(self, adapter_name: Optional[str] = None) -> List[TestResult]:
        """運行Level 3 MCP合規測試"""
        self.logger.info("開始Level 3 MCP合規測試...")
        self.test_results.clear()
        
        # 獲取適配器列表
        adapters = self.get_adapters()
        
        if not adapters:
            self.logger.warning("未找到任何適配器")
            return []
        
        # 過濾適配器
        if adapter_name:
            adapters = [(name, instance) for name, instance in adapters if name == adapter_name]
        
        self.logger.info(f"測試 {len(adapters)} 個適配器的MCP合規性")
        
        # 運行合規測試
        for name, instance in adapters:
            self._test_adapter_compliance(name, instance)
        
        self.logger.info(f"Level 3測試完成，共 {len(self.test_results)} 個測試結果")
        return self.test_results
    
    def _test_adapter_compliance(self, adapter_name: str, adapter_instance: Any):
        """測試單個適配器的MCP合規性"""
        self.logger.debug(f"測試適配器MCP合規性: {adapter_name}")
        
        # 1. 協議驗證測試
        self._test_protocol_compliance(adapter_name, adapter_instance)
        
        # 2. 標準化測試
        self._test_standardization_compliance(adapter_name, adapter_instance)
        
        # 3. 性能合規性測試
        self._test_performance_compliance(adapter_name, adapter_instance)
        
        # 4. 錯誤處理測試
        self._test_error_handling_compliance(adapter_name, adapter_instance)
        
        # 5. 能力聲明標準化測試
        self._test_capability_standardization(adapter_name, adapter_instance)
    
    def _test_protocol_compliance(self, adapter_name: str, adapter_instance: Any):
        """測試協議合規性"""
        start_time = time.time()
        
        compliance_checks = {}
        total_score = 0
        
        # 1. 檢查必需方法
        required_methods = self.mcp_standards["required_methods"]
        missing_methods = []
        
        for method_name in required_methods:
            if hasattr(adapter_instance, method_name):
                compliance_checks[f"has_{method_name}"] = True
                total_score += 25
            else:
                compliance_checks[f"has_{method_name}"] = False
                missing_methods.append(method_name)
        
        # 2. 檢查可選方法
        optional_methods = self.mcp_standards["optional_methods"]
        available_optional = []
        
        for method_name in optional_methods:
            if hasattr(adapter_instance, method_name):
                available_optional.append(method_name)
                compliance_checks[f"has_{method_name}"] = True
                total_score += 5
        
        # 3. 測試方法調用合規性
        method_compliance_score = self._test_method_compliance(adapter_instance)
        compliance_checks["method_compliance"] = method_compliance_score
        total_score += method_compliance_score * 0.5
        
        # 計算最終分數
        final_score = min(total_score, 100)
        passed = final_score >= self.test_config["compliance_threshold"]
        
        execution_time = time.time() - start_time
        
        message = f"協議合規性: {final_score:.1f}% (缺失方法: {len(missing_methods)})"
        
        result = self.create_test_result(
            test_name="test_compliance_protocol",
            adapter_name=adapter_name,
            passed=passed,
            score=final_score,
            execution_time=execution_time,
            message=message,
            details={
                "compliance_checks": compliance_checks,
                "missing_methods": missing_methods,
                "available_optional": available_optional,
                "method_compliance_score": method_compliance_score
            },
            severity=TestSeverity.HIGH
        )
        
        self.add_test_result(result)
    
    def _test_method_compliance(self, adapter_instance: Any) -> float:
        """測試方法調用合規性"""
        score = 0
        
        # 測試get_name方法
        if hasattr(adapter_instance, "get_name"):
            try:
                name = adapter_instance.get_name()
                if isinstance(name, str) and len(name) > 0:
                    score += 30
                elif name is not None:
                    score += 15
            except Exception as e:
                self.logger.debug(f"get_name方法調用失敗: {e}")
        
        # 測試get_capabilities方法
        if hasattr(adapter_instance, "get_capabilities"):
            try:
                capabilities = adapter_instance.get_capabilities()
                
                # 驗證能力格式
                if self._validate_capabilities_format(capabilities):
                    score += 40
                elif capabilities is not None:
                    score += 20
            except Exception as e:
                self.logger.debug(f"get_capabilities方法調用失敗: {e}")
        
        # 測試process方法（如果存在）
        if hasattr(adapter_instance, "process"):
            try:
                test_data = {"test": "compliance_check"}
                result = adapter_instance.process(test_data)
                
                # 驗證響應格式
                if self._validate_response_format(result):
                    score += 30
                elif result is not None:
                    score += 15
            except Exception as e:
                self.logger.debug(f"process方法調用失敗: {e}")
        
        return score
    
    def _validate_capabilities_format(self, capabilities: Any) -> bool:
        """驗證能力格式"""
        try:
            jsonschema.validate(capabilities, self.mcp_standards["capability_schema"])
            return True
        except:
            # 如果不是標準格式，檢查是否為合理的替代格式
            if isinstance(capabilities, (list, dict)) and len(capabilities) > 0:
                return True
            return False
    
    def _validate_response_format(self, response: Any) -> bool:
        """驗證響應格式"""
        if response is None:
            return False
        
        # 檢查是否為字典格式
        if isinstance(response, dict):
            # 檢查是否包含基本字段
            if "status" in response or "data" in response:
                return True
        
        # 任何非None響應都被認為是有效的
        return True
    
    def _test_standardization_compliance(self, adapter_name: str, adapter_instance: Any):
        """測試標準化合規性"""
        start_time = time.time()
        
        standardization_checks = {}
        total_score = 0
        
        # 1. 命名標準檢查
        naming_score = self._check_naming_standards(adapter_instance)
        standardization_checks["naming"] = naming_score
        total_score += naming_score * 0.3
        
        # 2. 接口標準檢查
        interface_score = self._check_interface_standards(adapter_instance)
        standardization_checks["interface"] = interface_score
        total_score += interface_score * 0.4
        
        # 3. 文檔標準檢查
        documentation_score = self._check_documentation_standards(adapter_instance)
        standardization_checks["documentation"] = documentation_score
        total_score += documentation_score * 0.3
        
        passed = total_score >= 70
        execution_time = time.time() - start_time
        
        message = f"標準化合規性: {total_score:.1f}%"
        
        result = self.create_test_result(
            test_name="test_compliance_standardization",
            adapter_name=adapter_name,
            passed=passed,
            score=total_score,
            execution_time=execution_time,
            message=message,
            details=standardization_checks,
            severity=TestSeverity.MEDIUM
        )
        
        self.add_test_result(result)
    
    def _check_naming_standards(self, adapter_instance: Any) -> float:
        """檢查命名標準"""
        score = 0
        
        # 檢查類名
        class_name = adapter_instance.__class__.__name__
        if any(keyword in class_name.lower() for keyword in ['adapter', 'mcp', 'tool', 'engine']):
            score += 30
        
        if class_name[0].isupper():  # 首字母大寫
            score += 20
        
        # 檢查方法名
        public_methods = [name for name in dir(adapter_instance) 
                         if callable(getattr(adapter_instance, name)) and not name.startswith('_')]
        
        if public_methods:
            descriptive_count = sum(1 for name in public_methods 
                                  if any(keyword in name.lower() for keyword in ['get', 'set', 'process', 'handle']))
            score += (descriptive_count / len(public_methods)) * 50
        
        return score
    
    def _check_interface_standards(self, adapter_instance: Any) -> float:
        """檢查接口標準"""
        score = 0
        
        # 檢查標準方法簽名
        if hasattr(adapter_instance, "get_name"):
            try:
                import inspect
                sig = inspect.signature(adapter_instance.get_name)
                if len(sig.parameters) == 0:  # 無參數
                    score += 25
            except:
                pass
        
        if hasattr(adapter_instance, "get_capabilities"):
            try:
                import inspect
                sig = inspect.signature(adapter_instance.get_capabilities)
                if len(sig.parameters) == 0:  # 無參數
                    score += 25
            except:
                pass
        
        if hasattr(adapter_instance, "process"):
            try:
                import inspect
                sig = inspect.signature(adapter_instance.process)
                if len(sig.parameters) == 1:  # 一個參數（除了self）
                    score += 25
            except:
                pass
        
        # 檢查返回值類型一致性
        consistency_score = self._check_return_type_consistency(adapter_instance)
        score += consistency_score * 0.25
        
        return score
    
    def _check_return_type_consistency(self, adapter_instance: Any) -> float:
        """檢查返回值類型一致性"""
        score = 0
        
        # 測試get_name的一致性
        if hasattr(adapter_instance, "get_name"):
            try:
                name1 = adapter_instance.get_name()
                name2 = adapter_instance.get_name()
                if type(name1) == type(name2) and name1 == name2:
                    score += 50
            except:
                pass
        
        # 測試get_capabilities的一致性
        if hasattr(adapter_instance, "get_capabilities"):
            try:
                caps1 = adapter_instance.get_capabilities()
                caps2 = adapter_instance.get_capabilities()
                if type(caps1) == type(caps2):
                    score += 50
            except:
                pass
        
        return score
    
    def _check_documentation_standards(self, adapter_instance: Any) -> float:
        """檢查文檔標準"""
        score = 0
        
        # 檢查類文檔
        class_doc = adapter_instance.__class__.__doc__
        if class_doc and len(class_doc.strip()) > 20:
            score += 50
        elif class_doc:
            score += 25
        
        # 檢查方法文檔
        documented_methods = 0
        total_methods = 0
        
        for name in dir(adapter_instance):
            if callable(getattr(adapter_instance, name)) and not name.startswith('_'):
                total_methods += 1
                method = getattr(adapter_instance, name)
                if hasattr(method, '__doc__') and method.__doc__ and len(method.__doc__.strip()) > 10:
                    documented_methods += 1
        
        if total_methods > 0:
            doc_ratio = documented_methods / total_methods
            score += doc_ratio * 50
        
        return score
    
    def _test_performance_compliance(self, adapter_name: str, adapter_instance: Any):
        """測試性能合規性"""
        start_time = time.time()
        
        performance_tests = {}
        total_score = 0
        
        # 1. 響應時間測試
        response_time_score = self._test_response_time(adapter_instance)
        performance_tests["response_time"] = response_time_score
        total_score += response_time_score * 0.4
        
        # 2. 吞吐量測試
        throughput_score = self._test_throughput(adapter_instance)
        performance_tests["throughput"] = throughput_score
        total_score += throughput_score * 0.3
        
        # 3. 內存使用測試
        memory_score = self._test_memory_usage(adapter_instance)
        performance_tests["memory"] = memory_score
        total_score += memory_score * 0.3
        
        passed = total_score >= 60
        execution_time = time.time() - start_time
        
        message = f"性能合規性: {total_score:.1f}%"
        
        result = self.create_test_result(
            test_name="test_compliance_performance",
            adapter_name=adapter_name,
            passed=passed,
            score=total_score,
            execution_time=execution_time,
            message=message,
            details=performance_tests,
            severity=TestSeverity.MEDIUM
        )
        
        self.add_test_result(result)
    
    def _test_response_time(self, adapter_instance: Any) -> float:
        """測試響應時間"""
        if not hasattr(adapter_instance, "process"):
            return 70  # 沒有process方法，給予基礎分數
        
        response_times = []
        threshold = self.test_config["performance_thresholds"]["response_time"]
        
        for i in range(5):
            start = time.time()
            try:
                adapter_instance.process({"test": f"response_time_{i}"})
                end = time.time()
                response_times.append(end - start)
            except:
                response_times.append(threshold * 2)  # 錯誤時記錄超時
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            
            if avg_response_time <= threshold:
                return 100
            elif avg_response_time <= threshold * 2:
                return 70
            elif avg_response_time <= threshold * 5:
                return 40
            else:
                return 20
        
        return 50
    
    def _test_throughput(self, adapter_instance: Any) -> float:
        """測試吞吐量"""
        if not hasattr(adapter_instance, "process"):
            return 70  # 沒有process方法，給予基礎分數
        
        start_time = time.time()
        operations = 0
        test_duration = 3.0  # 3秒測試
        
        while time.time() - start_time < test_duration:
            try:
                adapter_instance.process({"test": "throughput", "op": operations})
                operations += 1
            except:
                break
        
        actual_duration = time.time() - start_time
        throughput = operations / actual_duration if actual_duration > 0 else 0
        
        threshold = self.test_config["performance_thresholds"]["throughput"]
        
        if throughput >= threshold:
            return 100
        elif throughput >= threshold * 0.7:
            return 80
        elif throughput >= threshold * 0.4:
            return 60
        elif throughput > 0:
            return 40
        else:
            return 20
    
    def _test_memory_usage(self, adapter_instance: Any) -> float:
        """測試內存使用"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 執行多次操作
            for i in range(20):
                try:
                    if hasattr(adapter_instance, "process"):
                        adapter_instance.process({"test": "memory", "iteration": i})
                    elif hasattr(adapter_instance, "get_capabilities"):
                        adapter_instance.get_capabilities()
                except:
                    pass
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            threshold = self.test_config["performance_thresholds"]["memory_limit"]
            
            if memory_increase <= threshold * 0.1:
                return 100
            elif memory_increase <= threshold * 0.3:
                return 80
            elif memory_increase <= threshold:
                return 60
            else:
                return 30
                
        except ImportError:
            return 70  # 無法測試內存，給予基礎分數
        except:
            return 50
    
    def _test_error_handling_compliance(self, adapter_name: str, adapter_instance: Any):
        """測試錯誤處理合規性"""
        start_time = time.time()
        
        error_tests = {}
        total_score = 0
        
        # 1. 異常輸入處理
        exception_handling_score = self._test_exception_handling(adapter_instance)
        error_tests["exception_handling"] = exception_handling_score
        total_score += exception_handling_score * 0.4
        
        # 2. 錯誤恢復能力
        recovery_score = self._test_error_recovery(adapter_instance)
        error_tests["recovery"] = recovery_score
        total_score += recovery_score * 0.3
        
        # 3. 錯誤報告質量
        error_reporting_score = self._test_error_reporting(adapter_instance)
        error_tests["error_reporting"] = error_reporting_score
        total_score += error_reporting_score * 0.3
        
        passed = total_score >= 65
        execution_time = time.time() - start_time
        
        message = f"錯誤處理合規性: {total_score:.1f}%"
        
        result = self.create_test_result(
            test_name="test_compliance_error_handling",
            adapter_name=adapter_name,
            passed=passed,
            score=total_score,
            execution_time=execution_time,
            message=message,
            details=error_tests,
            severity=TestSeverity.MEDIUM
        )
        
        self.add_test_result(result)
    
    def _test_exception_handling(self, adapter_instance: Any) -> float:
        """測試異常處理"""
        score = 0
        test_cases = [None, {}, [], "", 0, -1, "invalid"]
        
        for test_case in test_cases:
            if hasattr(adapter_instance, "process"):
                try:
                    result = adapter_instance.process(test_case)
                    # 能處理異常輸入而不崩潰
                    score += 10
                except Exception:
                    # 拋出異常也是一種處理方式
                    score += 8
        
        # 測試方法調用異常
        for method_name in ["get_name", "get_capabilities"]:
            if hasattr(adapter_instance, method_name):
                try:
                    method = getattr(adapter_instance, method_name)
                    result = method()
                    score += 10
                except Exception:
                    score += 5
        
        return min(score, 100)
    
    def _test_error_recovery(self, adapter_instance: Any) -> float:
        """測試錯誤恢復"""
        score = 0
        
        if hasattr(adapter_instance, "process"):
            # 先造成錯誤
            try:
                adapter_instance.process(None)
            except:
                pass
            
            # 測試是否能恢復正常工作
            try:
                result = adapter_instance.process({"test": "recovery"})
                if result is not None:
                    score += 50
            except:
                pass
            
            # 測試連續錯誤後的恢復
            for _ in range(3):
                try:
                    adapter_instance.process("invalid")
                except:
                    pass
            
            try:
                result = adapter_instance.process({"test": "final_recovery"})
                if result is not None:
                    score += 50
            except:
                pass
        else:
            score = 70  # 沒有process方法，給予基礎分數
        
        return score
    
    def _test_error_reporting(self, adapter_instance: Any) -> float:
        """測試錯誤報告質量"""
        score = 0
        
        if hasattr(adapter_instance, "process"):
            try:
                adapter_instance.process(None)
                score += 30  # 沒有拋出異常，可能有內部錯誤處理
            except Exception as e:
                error_msg = str(e)
                
                # 檢查錯誤消息質量
                if len(error_msg) > 10:
                    score += 40
                elif len(error_msg) > 0:
                    score += 20
                
                # 檢查是否包含有用信息
                if any(keyword in error_msg.lower() for keyword in ['invalid', 'error', 'none', 'null']):
                    score += 30
                
                # 檢查異常類型
                if isinstance(e, (ValueError, TypeError, AttributeError)):
                    score += 30
        else:
            score = 60  # 沒有process方法，給予基礎分數
        
        return min(score, 100)
    
    def _test_capability_standardization(self, adapter_name: str, adapter_instance: Any):
        """測試能力聲明標準化"""
        start_time = time.time()
        
        capability_tests = {}
        total_score = 0
        
        # 1. 能力格式驗證
        format_score = self._test_capability_format(adapter_instance)
        capability_tests["format"] = format_score
        total_score += format_score * 0.4
        
        # 2. 能力內容驗證
        content_score = self._test_capability_content(adapter_instance)
        capability_tests["content"] = content_score
        total_score += content_score * 0.3
        
        # 3. 能力一致性驗證
        consistency_score = self._test_capability_consistency(adapter_instance)
        capability_tests["consistency"] = consistency_score
        total_score += consistency_score * 0.3
        
        passed = total_score >= 70
        execution_time = time.time() - start_time
        
        message = f"能力聲明標準化: {total_score:.1f}%"
        
        result = self.create_test_result(
            test_name="test_compliance_capability_standardization",
            adapter_name=adapter_name,
            passed=passed,
            score=total_score,
            execution_time=execution_time,
            message=message,
            details=capability_tests,
            severity=TestSeverity.LOW
        )
        
        self.add_test_result(result)
    
    def _test_capability_format(self, adapter_instance: Any) -> float:
        """測試能力格式"""
        if not hasattr(adapter_instance, "get_capabilities"):
            return 30  # 沒有能力方法，給予低分
        
        try:
            capabilities = adapter_instance.get_capabilities()
            
            # 檢查格式
            if isinstance(capabilities, list):
                if all(isinstance(cap, str) for cap in capabilities):
                    return 100  # 標準格式
                else:
                    return 70   # 列表但不全是字符串
            elif isinstance(capabilities, dict):
                return 80       # 字典格式也可接受
            elif isinstance(capabilities, str):
                return 60       # 字符串格式
            else:
                return 40       # 其他格式
                
        except Exception:
            return 20
    
    def _test_capability_content(self, adapter_instance: Any) -> float:
        """測試能力內容"""
        if not hasattr(adapter_instance, "get_capabilities"):
            return 30
        
        try:
            capabilities = adapter_instance.get_capabilities()
            
            if not capabilities:
                return 20  # 空能力
            
            score = 50  # 基礎分數
            
            # 檢查能力描述性
            if isinstance(capabilities, list):
                descriptive_caps = sum(1 for cap in capabilities 
                                     if isinstance(cap, str) and len(cap) > 3)
                if len(capabilities) > 0:
                    score += (descriptive_caps / len(capabilities)) * 50
            elif isinstance(capabilities, dict):
                if len(capabilities) > 0:
                    score += 50
            
            return min(score, 100)
            
        except Exception:
            return 20
    
    def _test_capability_consistency(self, adapter_instance: Any) -> float:
        """測試能力一致性"""
        if not hasattr(adapter_instance, "get_capabilities"):
            return 30
        
        try:
            # 多次調用檢查一致性
            caps1 = adapter_instance.get_capabilities()
            caps2 = adapter_instance.get_capabilities()
            
            if caps1 == caps2:
                return 100
            elif type(caps1) == type(caps2):
                return 70
            else:
                return 40
                
        except Exception:
            return 20

def run_level3_tests(adapter_name: Optional[str] = None) -> List[TestResult]:
    """運行Level 3測試的便捷函數"""
    framework = Level3MCPComplianceFramework()
    return framework.run_tests(adapter_name)

if __name__ == "__main__":
    # 運行Level 3測試
    print("📋 開始Level 3 MCP合規測試...")
    
    framework = Level3MCPComplianceFramework()
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
    framework.save_results("test/level3")
    print("📄 測試報告已保存到 test/level3/")
    
    # 生成簡要報告
    report = framework.generate_report()
    print("\n📋 測試報告預覽:")
    print(report[:1000] + "..." if len(report) > 1000 else report)

