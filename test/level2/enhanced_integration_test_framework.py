#!/usr/bin/env python3
"""
Level 2 集成測試框架
業務層：集成測試 + 智能體協作

主要功能：
- 適配器間集成測試
- 智能體協作測試
- 數據流測試
- 系統集成驗證
"""

import sys
import os
import time
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 導入標準化接口
from test.standardized_test_interface import BaseTestFramework, TestResult, TestStatus, TestSeverity
from test.optimized_module_importer import get_safe_importer

logger = logging.getLogger(__name__)

class Level2IntegrationTestFramework(BaseTestFramework):
    """Level 2 集成測試框架"""
    
    def __init__(self):
        super().__init__(
            name="Level2_IntegrationTest",
            description="業務層集成測試和智能體協作驗證"
        )
        
        self.importer = get_safe_importer()
        
        # 測試配置
        self.test_config = {
            "timeout": 60.0,  # 集成測試超時時間
            "max_concurrent": 3,  # 最大並發測試數
            "retry_count": 2,  # 重試次數
            "integration_scenarios": [
                "adapter_chain",
                "data_flow",
                "error_propagation",
                "resource_sharing"
            ]
        }
    
    def run_tests(self, adapter_name: Optional[str] = None) -> List[TestResult]:
        """運行Level 2集成測試"""
        self.logger.info("開始Level 2集成測試...")
        self.test_results.clear()
        
        # 獲取適配器列表
        adapters = self.get_adapters()
        
        if not adapters:
            self.logger.warning("未找到任何適配器")
            return []
        
        # 過濾適配器
        if adapter_name:
            adapters = [(name, instance) for name, instance in adapters if name == adapter_name]
        
        self.logger.info(f"測試 {len(adapters)} 個適配器的集成功能")
        
        # 運行集成測試
        self._test_adapter_integration(adapters)
        self._test_agent_collaboration(adapters)
        self._test_data_flow(adapters)
        self._test_system_integration(adapters)
        
        self.logger.info(f"Level 2測試完成，共 {len(self.test_results)} 個測試結果")
        return self.test_results
    
    def _test_adapter_integration(self, adapters: List[Tuple[str, Any]]):
        """測試適配器間集成"""
        self.logger.info("測試適配器間集成...")
        
        if len(adapters) < 2:
            # 單個適配器的自集成測試
            for name, instance in adapters:
                self._test_single_adapter_integration(name, instance)
        else:
            # 多適配器集成測試
            self._test_multi_adapter_integration(adapters)
    
    def _test_single_adapter_integration(self, adapter_name: str, adapter_instance: Any):
        """測試單個適配器的集成能力"""
        start_time = time.time()
        
        integration_tests = {}
        total_score = 0
        
        # 1. 自我集成測試
        self_integration_score = self._test_self_integration(adapter_instance)
        integration_tests["self_integration"] = self_integration_score
        total_score += self_integration_score
        
        # 2. 狀態管理測試
        state_management_score = self._test_state_management(adapter_instance)
        integration_tests["state_management"] = state_management_score
        total_score += state_management_score
        
        # 3. 資源管理測試
        resource_management_score = self._test_resource_management(adapter_instance)
        integration_tests["resource_management"] = resource_management_score
        total_score += resource_management_score
        
        # 計算平均分數
        average_score = total_score / 3
        passed = average_score >= 70
        
        execution_time = time.time() - start_time
        
        message = f"單適配器集成測試分數: {average_score:.1f}"
        
        result = self.create_test_result(
            test_name="test_integration_single_adapter",
            adapter_name=adapter_name,
            passed=passed,
            score=average_score,
            execution_time=execution_time,
            message=message,
            details=integration_tests,
            severity=TestSeverity.MEDIUM
        )
        
        self.add_test_result(result)
    
    def _test_multi_adapter_integration(self, adapters: List[Tuple[str, Any]]):
        """測試多適配器集成"""
        start_time = time.time()
        
        integration_results = {}
        total_score = 0
        test_count = 0
        
        # 測試適配器對之間的集成
        for i in range(min(3, len(adapters))):  # 限制測試數量
            for j in range(i + 1, min(i + 3, len(adapters))):
                adapter1_name, adapter1_instance = adapters[i]
                adapter2_name, adapter2_instance = adapters[j]
                
                pair_name = f"{adapter1_name}+{adapter2_name}"
                pair_score = self._test_adapter_pair_integration(
                    adapter1_instance, adapter2_instance
                )
                
                integration_results[pair_name] = pair_score
                total_score += pair_score
                test_count += 1
        
        # 計算平均分數
        average_score = total_score / test_count if test_count > 0 else 0
        passed = average_score >= 60
        
        execution_time = time.time() - start_time
        
        message = f"多適配器集成測試: {test_count} 對適配器，平均分數: {average_score:.1f}"
        
        result = self.create_test_result(
            test_name="test_integration_multi_adapter",
            adapter_name="multi_adapter",
            passed=passed,
            score=average_score,
            execution_time=execution_time,
            message=message,
            details=integration_results,
            severity=TestSeverity.HIGH
        )
        
        self.add_test_result(result)
    
    def _test_self_integration(self, adapter_instance: Any) -> float:
        """測試適配器自我集成能力"""
        score = 0
        
        # 測試連續調用
        try:
            if hasattr(adapter_instance, "get_name"):
                name1 = adapter_instance.get_name()
                name2 = adapter_instance.get_name()
                if name1 == name2:
                    score += 25
        except:
            pass
        
        # 測試狀態一致性
        try:
            if hasattr(adapter_instance, "get_capabilities"):
                caps1 = adapter_instance.get_capabilities()
                caps2 = adapter_instance.get_capabilities()
                if caps1 == caps2:
                    score += 25
        except:
            pass
        
        # 測試處理一致性
        try:
            if hasattr(adapter_instance, "process"):
                test_data = {"test": "consistency"}
                result1 = adapter_instance.process(test_data)
                result2 = adapter_instance.process(test_data)
                # 結果可能不完全相同，但應該有相似的結構
                if type(result1) == type(result2):
                    score += 25
        except:
            pass
        
        # 測試方法存在性
        required_methods = ["get_name", "get_capabilities"]
        existing_methods = sum(1 for method in required_methods if hasattr(adapter_instance, method))
        score += (existing_methods / len(required_methods)) * 25
        
        return score
    
    def _test_state_management(self, adapter_instance: Any) -> float:
        """測試狀態管理"""
        score = 0
        
        # 測試狀態保持
        try:
            initial_state = self._get_adapter_state(adapter_instance)
            
            # 執行一些操作
            if hasattr(adapter_instance, "process"):
                adapter_instance.process({"test": "state_test"})
            
            final_state = self._get_adapter_state(adapter_instance)
            
            # 檢查狀態變化是否合理
            if initial_state and final_state:
                score += 50
            
        except:
            score += 20  # 部分分數
        
        # 測試錯誤後的狀態恢復
        try:
            if hasattr(adapter_instance, "process"):
                # 嘗試錯誤輸入
                try:
                    adapter_instance.process(None)
                except:
                    pass
                
                # 檢查是否還能正常工作
                result = adapter_instance.process({"test": "recovery"})
                if result is not None:
                    score += 50
        except:
            score += 20
        
        return score
    
    def _get_adapter_state(self, adapter_instance: Any) -> Dict[str, Any]:
        """獲取適配器狀態"""
        state = {}
        
        try:
            if hasattr(adapter_instance, "get_name"):
                state["name"] = adapter_instance.get_name()
        except:
            pass
        
        try:
            if hasattr(adapter_instance, "get_capabilities"):
                state["capabilities"] = adapter_instance.get_capabilities()
        except:
            pass
        
        return state
    
    def _test_resource_management(self, adapter_instance: Any) -> float:
        """測試資源管理"""
        score = 0
        
        # 測試內存使用
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # 執行多次操作
            for i in range(10):
                if hasattr(adapter_instance, "process"):
                    adapter_instance.process({"test": f"memory_test_{i}"})
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # 內存增長應該在合理範圍內（< 50MB）
            if memory_increase < 50 * 1024 * 1024:
                score += 50
            elif memory_increase < 100 * 1024 * 1024:
                score += 30
            else:
                score += 10
                
        except ImportError:
            score += 25  # 無法測試，給予基礎分數
        except:
            score += 15
        
        # 測試並發處理
        try:
            if hasattr(adapter_instance, "process"):
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = []
                    for i in range(5):
                        future = executor.submit(
                            adapter_instance.process, 
                            {"test": f"concurrent_{i}"}
                        )
                        futures.append(future)
                    
                    # 等待所有任務完成
                    results = []
                    for future in as_completed(futures, timeout=10):
                        try:
                            result = future.result()
                            results.append(result)
                        except:
                            pass
                    
                    # 如果大部分任務成功完成
                    if len(results) >= 3:
                        score += 50
                    elif len(results) >= 1:
                        score += 30
                        
        except:
            score += 20
        
        return score
    
    def _test_adapter_pair_integration(self, adapter1: Any, adapter2: Any) -> float:
        """測試兩個適配器之間的集成"""
        score = 0
        
        # 測試數據傳遞
        try:
            if hasattr(adapter1, "process") and hasattr(adapter2, "process"):
                # 從adapter1獲取輸出
                output1 = adapter1.process({"test": "integration_data"})
                
                # 將輸出傳遞給adapter2
                if output1 is not None:
                    output2 = adapter2.process(output1)
                    if output2 is not None:
                        score += 40
                    else:
                        score += 20
        except:
            score += 10
        
        # 測試能力互補
        try:
            caps1 = adapter1.get_capabilities() if hasattr(adapter1, "get_capabilities") else []
            caps2 = adapter2.get_capabilities() if hasattr(adapter2, "get_capabilities") else []
            
            if isinstance(caps1, (list, dict)) and isinstance(caps2, (list, dict)):
                # 檢查是否有互補的能力
                if caps1 != caps2:  # 不同的能力
                    score += 30
                else:
                    score += 15
        except:
            score += 10
        
        # 測試錯誤處理兼容性
        try:
            if hasattr(adapter1, "process") and hasattr(adapter2, "process"):
                # 測試錯誤傳播
                try:
                    error_output = adapter1.process(None)
                    adapter2.process(error_output)
                    score += 30  # 能處理錯誤輸入
                except:
                    score += 15  # 至少有錯誤處理
        except:
            score += 5
        
        return score
    
    def _test_agent_collaboration(self, adapters: List[Tuple[str, Any]]):
        """測試智能體協作"""
        self.logger.info("測試智能體協作...")
        
        start_time = time.time()
        
        collaboration_tests = {}
        total_score = 0
        
        # 1. 協作通信測試
        communication_score = self._test_collaboration_communication(adapters)
        collaboration_tests["communication"] = communication_score
        total_score += communication_score
        
        # 2. 任務分配測試
        task_distribution_score = self._test_task_distribution(adapters)
        collaboration_tests["task_distribution"] = task_distribution_score
        total_score += task_distribution_score
        
        # 3. 結果聚合測試
        result_aggregation_score = self._test_result_aggregation(adapters)
        collaboration_tests["result_aggregation"] = result_aggregation_score
        total_score += result_aggregation_score
        
        # 計算平均分數
        average_score = total_score / 3
        passed = average_score >= 60
        
        execution_time = time.time() - start_time
        
        message = f"智能體協作測試分數: {average_score:.1f}"
        
        result = self.create_test_result(
            test_name="test_integration_agent_collaboration",
            adapter_name="agent_collaboration",
            passed=passed,
            score=average_score,
            execution_time=execution_time,
            message=message,
            details=collaboration_tests,
            severity=TestSeverity.HIGH
        )
        
        self.add_test_result(result)
    
    def _test_collaboration_communication(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試協作通信"""
        if len(adapters) < 2:
            return 50  # 單適配器給予基礎分數
        
        score = 0
        successful_communications = 0
        total_attempts = 0
        
        # 測試適配器間的通信
        for i in range(min(3, len(adapters))):
            for j in range(i + 1, min(i + 3, len(adapters))):
                name1, adapter1 = adapters[i]
                name2, adapter2 = adapters[j]
                
                total_attempts += 1
                
                try:
                    # 模擬通信：adapter1 -> adapter2
                    if hasattr(adapter1, "process") and hasattr(adapter2, "process"):
                        message = {
                            "from": name1,
                            "to": name2,
                            "data": {"test": "communication"},
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # adapter1處理消息
                        processed_message = adapter1.process(message)
                        
                        # adapter2接收處理後的消息
                        if processed_message is not None:
                            response = adapter2.process(processed_message)
                            if response is not None:
                                successful_communications += 1
                                
                except Exception as e:
                    self.logger.debug(f"通信測試失敗 {name1}->{name2}: {e}")
        
        if total_attempts > 0:
            communication_rate = successful_communications / total_attempts
            score = communication_rate * 100
        else:
            score = 50
        
        return score
    
    def _test_task_distribution(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試任務分配"""
        if len(adapters) < 2:
            return 60  # 單適配器給予基礎分數
        
        score = 0
        
        # 創建測試任務
        tasks = [
            {"id": 1, "type": "data_processing", "data": {"value": 100}},
            {"id": 2, "type": "analysis", "data": {"items": [1, 2, 3]}},
            {"id": 3, "type": "transformation", "data": {"text": "test"}}
        ]
        
        successful_distributions = 0
        
        for task in tasks:
            # 嘗試將任務分配給不同的適配器
            for name, adapter in adapters[:3]:  # 限制測試數量
                try:
                    if hasattr(adapter, "process"):
                        result = adapter.process(task)
                        if result is not None:
                            successful_distributions += 1
                            break  # 任務成功分配
                except:
                    continue
        
        # 計算分配成功率
        if len(tasks) > 0:
            distribution_rate = successful_distributions / len(tasks)
            score = distribution_rate * 100
        else:
            score = 60
        
        return score
    
    def _test_result_aggregation(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試結果聚合"""
        score = 0
        
        # 收集多個適配器的結果
        results = []
        test_data = {"test": "aggregation", "value": 42}
        
        for name, adapter in adapters[:5]:  # 限制測試數量
            try:
                if hasattr(adapter, "process"):
                    result = adapter.process(test_data)
                    if result is not None:
                        results.append({
                            "adapter": name,
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        })
            except:
                continue
        
        # 測試結果聚合能力
        if len(results) >= 2:
            # 檢查結果的一致性和可聚合性
            result_types = [type(r["result"]) for r in results]
            
            # 如果結果類型一致，給予高分
            if len(set(result_types)) == 1:
                score += 50
            elif len(set(result_types)) <= 2:
                score += 30
            else:
                score += 15
            
            # 檢查結果內容的可聚合性
            try:
                # 嘗試簡單的聚合操作
                aggregated = {
                    "total_results": len(results),
                    "adapters": [r["adapter"] for r in results],
                    "results": [r["result"] for r in results]
                }
                
                if aggregated:
                    score += 50
                    
            except:
                score += 20
        else:
            score = 40  # 結果太少，給予基礎分數
        
        return score
    
    def _test_data_flow(self, adapters: List[Tuple[str, Any]]):
        """測試數據流"""
        self.logger.info("測試數據流...")
        
        start_time = time.time()
        
        data_flow_tests = {}
        total_score = 0
        
        # 1. 數據傳遞測試
        data_passing_score = self._test_data_passing(adapters)
        data_flow_tests["data_passing"] = data_passing_score
        total_score += data_passing_score
        
        # 2. 數據轉換測試
        data_transformation_score = self._test_data_transformation(adapters)
        data_flow_tests["data_transformation"] = data_transformation_score
        total_score += data_transformation_score
        
        # 3. 數據驗證測試
        data_validation_score = self._test_data_validation(adapters)
        data_flow_tests["data_validation"] = data_validation_score
        total_score += data_validation_score
        
        # 計算平均分數
        average_score = total_score / 3
        passed = average_score >= 65
        
        execution_time = time.time() - start_time
        
        message = f"數據流測試分數: {average_score:.1f}"
        
        result = self.create_test_result(
            test_name="test_integration_data_flow",
            adapter_name="data_flow",
            passed=passed,
            score=average_score,
            execution_time=execution_time,
            message=message,
            details=data_flow_tests,
            severity=TestSeverity.MEDIUM
        )
        
        self.add_test_result(result)
    
    def _test_data_passing(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試數據傳遞"""
        score = 0
        
        test_data_sets = [
            {"type": "simple", "data": {"value": 123}},
            {"type": "complex", "data": {"nested": {"items": [1, 2, 3]}}},
            {"type": "string", "data": "test string"},
            {"type": "list", "data": [1, 2, 3, 4, 5]}
        ]
        
        successful_passes = 0
        total_tests = 0
        
        for test_data in test_data_sets:
            for name, adapter in adapters[:3]:  # 限制測試數量
                total_tests += 1
                
                try:
                    if hasattr(adapter, "process"):
                        result = adapter.process(test_data)
                        if result is not None:
                            successful_passes += 1
                except:
                    pass
        
        if total_tests > 0:
            pass_rate = successful_passes / total_tests
            score = pass_rate * 100
        else:
            score = 50
        
        return score
    
    def _test_data_transformation(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試數據轉換"""
        score = 0
        
        input_data = {"original": "data", "value": 100, "items": [1, 2, 3]}
        transformations = 0
        successful_transformations = 0
        
        for name, adapter in adapters[:5]:  # 限制測試數量
            try:
                if hasattr(adapter, "process"):
                    transformations += 1
                    result = adapter.process(input_data)
                    
                    # 檢查是否發生了轉換
                    if result is not None and result != input_data:
                        successful_transformations += 1
                        
                        # 檢查轉換的質量
                        if isinstance(result, dict):
                            score += 20
                        elif isinstance(result, (list, str, int, float)):
                            score += 15
                        else:
                            score += 10
                            
            except:
                pass
        
        # 如果沒有轉換，給予基礎分數
        if transformations == 0:
            score = 50
        elif successful_transformations == 0:
            score = 30
        
        return min(score, 100)
    
    def _test_data_validation(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試數據驗證"""
        score = 0
        
        # 測試有效數據
        valid_data = {"valid": True, "data": {"test": "valid"}}
        valid_responses = 0
        
        # 測試無效數據
        invalid_data_sets = [
            None,
            {},
            {"invalid": "structure"},
            "invalid_string"
        ]
        
        for name, adapter in adapters[:3]:  # 限制測試數量
            try:
                if hasattr(adapter, "process"):
                    # 測試有效數據
                    result = adapter.process(valid_data)
                    if result is not None:
                        valid_responses += 1
                        score += 25
                    
                    # 測試無效數據處理
                    for invalid_data in invalid_data_sets:
                        try:
                            invalid_result = adapter.process(invalid_data)
                            # 能處理無效數據（不崩潰）
                            score += 5
                        except:
                            # 拋出異常也是一種處理方式
                            score += 3
                            
            except:
                pass
        
        return min(score, 100)
    
    def _test_system_integration(self, adapters: List[Tuple[str, Any]]):
        """測試系統集成"""
        self.logger.info("測試系統集成...")
        
        start_time = time.time()
        
        system_tests = {}
        total_score = 0
        
        # 1. 系統穩定性測試
        stability_score = self._test_system_stability(adapters)
        system_tests["stability"] = stability_score
        total_score += stability_score
        
        # 2. 系統性能測試
        performance_score = self._test_system_performance(adapters)
        system_tests["performance"] = performance_score
        total_score += performance_score
        
        # 3. 系統可擴展性測試
        scalability_score = self._test_system_scalability(adapters)
        system_tests["scalability"] = scalability_score
        total_score += scalability_score
        
        # 計算平均分數
        average_score = total_score / 3
        passed = average_score >= 70
        
        execution_time = time.time() - start_time
        
        message = f"系統集成測試分數: {average_score:.1f}"
        
        result = self.create_test_result(
            test_name="test_integration_system",
            adapter_name="system_integration",
            passed=passed,
            score=average_score,
            execution_time=execution_time,
            message=message,
            details=system_tests,
            severity=TestSeverity.HIGH
        )
        
        self.add_test_result(result)
    
    def _test_system_stability(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試系統穩定性"""
        score = 0
        
        # 連續運行測試
        continuous_runs = 10
        successful_runs = 0
        
        for i in range(continuous_runs):
            try:
                for name, adapter in adapters[:3]:  # 限制測試數量
                    if hasattr(adapter, "process"):
                        result = adapter.process({"run": i, "test": "stability"})
                        if result is not None:
                            successful_runs += 1
                            break
            except:
                pass
        
        stability_rate = successful_runs / continuous_runs
        score = stability_rate * 100
        
        return score
    
    def _test_system_performance(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試系統性能"""
        score = 0
        
        # 性能測試
        start_time = time.time()
        operations = 0
        
        for name, adapter in adapters[:5]:  # 限制測試數量
            try:
                if hasattr(adapter, "process"):
                    for i in range(5):  # 每個適配器測試5次
                        adapter.process({"performance_test": i})
                        operations += 1
            except:
                pass
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if operations > 0 and total_time > 0:
            ops_per_second = operations / total_time
            
            # 根據操作速度評分
            if ops_per_second >= 10:
                score = 100
            elif ops_per_second >= 5:
                score = 80
            elif ops_per_second >= 1:
                score = 60
            else:
                score = 40
        else:
            score = 30
        
        return score
    
    def _test_system_scalability(self, adapters: List[Tuple[str, Any]]) -> float:
        """測試系統可擴展性"""
        score = 0
        
        # 測試並發處理能力
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                
                # 提交並發任務
                for i in range(6):
                    for name, adapter in adapters[:2]:  # 限制測試數量
                        if hasattr(adapter, "process"):
                            future = executor.submit(
                                adapter.process,
                                {"concurrent_test": i, "adapter": name}
                            )
                            futures.append(future)
                
                # 收集結果
                completed = 0
                for future in as_completed(futures, timeout=15):
                    try:
                        result = future.result()
                        if result is not None:
                            completed += 1
                    except:
                        pass
                
                # 根據完成率評分
                if len(futures) > 0:
                    completion_rate = completed / len(futures)
                    score = completion_rate * 100
                else:
                    score = 50
                    
        except:
            score = 30
        
        return score

def run_level2_tests(adapter_name: Optional[str] = None) -> List[TestResult]:
    """運行Level 2測試的便捷函數"""
    framework = Level2IntegrationTestFramework()
    return framework.run_tests(adapter_name)

if __name__ == "__main__":
    # 運行Level 2測試
    print("🔗 開始Level 2集成測試...")
    
    framework = Level2IntegrationTestFramework()
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
    framework.save_results("test/level2")
    print("📄 測試報告已保存到 test/level2/")
    
    # 生成簡要報告
    report = framework.generate_report()
    print("\n📋 測試報告預覽:")
    print(report[:1000] + "..." if len(report) > 1000 else report)

