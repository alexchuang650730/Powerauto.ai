#!/usr/bin/env python3
"""
MCP性能合規性測試模組
測試MCP適配器的性能指標和合規性要求

包括：
- 響應時間測試
- 吞吐量測試
- 併發性能測試
- 記憶體使用測試
- CPU使用率測試
- 性能基準對比
"""

import sys
import os
import time
import psutil
import threading
import asyncio
import statistics
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指標"""
    response_time_ms: float
    throughput_rps: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success_rate: float
    error_count: int
    concurrent_requests: int
    test_duration_seconds: float

@dataclass
class PerformanceTestResult:
    """性能測試結果"""
    test_name: str
    adapter_name: str
    passed: bool
    metrics: PerformanceMetrics
    benchmark_comparison: Dict[str, Any]
    details: Dict[str, Any]
    execution_time: float

class MCPPerformanceComplianceTester:
    """MCP性能合規性測試器"""
    
    def __init__(self):
        self.test_results = []
        self.performance_standards = self._load_performance_standards()
        self.baseline_metrics = {}
        
    def _load_performance_standards(self) -> Dict[str, Any]:
        """載入性能標準"""
        return {
            "response_time": {
                "excellent": 100,  # ms
                "good": 500,
                "acceptable": 1000,
                "poor": 2000
            },
            "throughput": {
                "excellent": 100,  # requests per second
                "good": 50,
                "acceptable": 20,
                "poor": 10
            },
            "memory_usage": {
                "excellent": 50,   # MB
                "good": 100,
                "acceptable": 200,
                "poor": 500
            },
            "cpu_usage": {
                "excellent": 10,   # percent
                "good": 25,
                "acceptable": 50,
                "poor": 80
            },
            "success_rate": {
                "excellent": 99.9,  # percent
                "good": 99.0,
                "acceptable": 95.0,
                "poor": 90.0
            },
            "concurrent_users": {
                "light": 10,
                "medium": 50,
                "heavy": 100,
                "extreme": 200
            }
        }
    
    def measure_response_time(self, adapter_instance: Any, test_data: Dict[str, Any], iterations: int = 100) -> Dict[str, float]:
        """測量響應時間"""
        response_times = []
        errors = 0
        
        for i in range(iterations):
            start_time = time.time()
            try:
                if hasattr(adapter_instance, 'process'):
                    result = adapter_instance.process(test_data)
                else:
                    # 如果沒有process方法，嘗試其他方法
                    if hasattr(adapter_instance, '__call__'):
                        result = adapter_instance(test_data)
                    else:
                        raise AttributeError("No callable method found")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # 轉換為毫秒
                response_times.append(response_time)
                
            except Exception as e:
                errors += 1
                logger.warning(f"響應時間測試第{i+1}次迭代失敗: {e}")
        
        if not response_times:
            return {
                "avg_response_time": float('inf'),
                "min_response_time": float('inf'),
                "max_response_time": float('inf'),
                "p95_response_time": float('inf'),
                "p99_response_time": float('inf'),
                "error_rate": 100.0
            }
        
        return {
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times),
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times),
            "error_rate": (errors / iterations) * 100
        }
    
    def measure_throughput(self, adapter_instance: Any, test_data: Dict[str, Any], duration_seconds: int = 30) -> Dict[str, float]:
        """測量吞吐量"""
        start_time = time.time()
        end_time = start_time + duration_seconds
        request_count = 0
        error_count = 0
        
        while time.time() < end_time:
            try:
                if hasattr(adapter_instance, 'process'):
                    result = adapter_instance.process(test_data)
                else:
                    if hasattr(adapter_instance, '__call__'):
                        result = adapter_instance(test_data)
                    else:
                        raise AttributeError("No callable method found")
                
                request_count += 1
                
            except Exception as e:
                error_count += 1
                logger.warning(f"吞吐量測試請求失敗: {e}")
        
        actual_duration = time.time() - start_time
        throughput = request_count / actual_duration if actual_duration > 0 else 0
        
        return {
            "requests_per_second": throughput,
            "total_requests": request_count,
            "total_errors": error_count,
            "test_duration": actual_duration,
            "success_rate": ((request_count - error_count) / request_count * 100) if request_count > 0 else 0
        }
    
    def measure_concurrent_performance(self, adapter_instance: Any, test_data: Dict[str, Any], concurrent_users: int = 10, requests_per_user: int = 10) -> Dict[str, Any]:
        """測量併發性能"""
        def worker_function(user_id: int) -> Dict[str, Any]:
            """工作線程函數"""
            response_times = []
            errors = 0
            
            for i in range(requests_per_user):
                start_time = time.time()
                try:
                    if hasattr(adapter_instance, 'process'):
                        result = adapter_instance.process(test_data)
                    else:
                        if hasattr(adapter_instance, '__call__'):
                            result = adapter_instance(test_data)
                        else:
                            raise AttributeError("No callable method found")
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    response_times.append(response_time)
                    
                except Exception as e:
                    errors += 1
            
            return {
                "user_id": user_id,
                "response_times": response_times,
                "errors": errors,
                "avg_response_time": statistics.mean(response_times) if response_times else float('inf')
            }
        
        # 執行併發測試
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker_function, i) for i in range(concurrent_users)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        
        # 彙總結果
        all_response_times = []
        total_errors = 0
        total_requests = 0
        
        for result in results:
            all_response_times.extend(result["response_times"])
            total_errors += result["errors"]
            total_requests += len(result["response_times"]) + result["errors"]
        
        return {
            "concurrent_users": concurrent_users,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "success_rate": ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 0,
            "avg_response_time": statistics.mean(all_response_times) if all_response_times else float('inf'),
            "max_response_time": max(all_response_times) if all_response_times else float('inf'),
            "min_response_time": min(all_response_times) if all_response_times else float('inf'),
            "test_duration": end_time - start_time,
            "throughput": total_requests / (end_time - start_time) if (end_time - start_time) > 0 else 0
        }
    
    def measure_resource_usage(self, adapter_instance: Any, test_data: Dict[str, Any], duration_seconds: int = 60) -> Dict[str, float]:
        """測量資源使用情況"""
        process = psutil.Process()
        
        # 記錄初始資源使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        
        memory_samples = []
        cpu_samples = []
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        # 在背景執行請求
        def background_requests():
            while time.time() < end_time:
                try:
                    if hasattr(adapter_instance, 'process'):
                        result = adapter_instance.process(test_data)
                    else:
                        if hasattr(adapter_instance, '__call__'):
                            result = adapter_instance(test_data)
                    time.sleep(0.1)  # 避免過度負載
                except Exception:
                    pass
        
        # 啟動背景請求線程
        request_thread = threading.Thread(target=background_requests)
        request_thread.start()
        
        # 監控資源使用
        while time.time() < end_time:
            try:
                memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                cpu_usage = process.cpu_percent()
                
                memory_samples.append(memory_usage)
                cpu_samples.append(cpu_usage)
                
                time.sleep(1)  # 每秒採樣一次
            except Exception as e:
                logger.warning(f"資源監控失敗: {e}")
        
        # 等待背景線程結束
        request_thread.join(timeout=5)
        
        return {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": max(memory_samples) if memory_samples else initial_memory,
            "avg_memory_mb": statistics.mean(memory_samples) if memory_samples else initial_memory,
            "memory_growth_mb": (max(memory_samples) - initial_memory) if memory_samples else 0,
            "avg_cpu_percent": statistics.mean(cpu_samples) if cpu_samples else 0,
            "peak_cpu_percent": max(cpu_samples) if cpu_samples else 0,
            "samples_count": len(memory_samples)
        }
    
    def test_performance_compliance(self, adapter_name: str, adapter_instance: Any) -> PerformanceTestResult:
        """測試性能合規性"""
        start_time = time.time()
        
        # 準備測試數據
        test_data = {
            "test_type": "performance_compliance",
            "data": "test data for performance testing",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"開始性能合規性測試: {adapter_name}")
        
        # 1. 響應時間測試
        logger.info("測試響應時間...")
        response_time_metrics = self.measure_response_time(adapter_instance, test_data, iterations=50)
        
        # 2. 吞吐量測試
        logger.info("測試吞吐量...")
        throughput_metrics = self.measure_throughput(adapter_instance, test_data, duration_seconds=15)
        
        # 3. 併發性能測試
        logger.info("測試併發性能...")
        concurrent_metrics = self.measure_concurrent_performance(adapter_instance, test_data, concurrent_users=5, requests_per_user=5)
        
        # 4. 資源使用測試
        logger.info("測試資源使用...")
        resource_metrics = self.measure_resource_usage(adapter_instance, test_data, duration_seconds=30)
        
        # 彙總性能指標
        metrics = PerformanceMetrics(
            response_time_ms=response_time_metrics["avg_response_time"],
            throughput_rps=throughput_metrics["requests_per_second"],
            memory_usage_mb=resource_metrics["peak_memory_mb"],
            cpu_usage_percent=resource_metrics["avg_cpu_percent"],
            success_rate=min(throughput_metrics["success_rate"], concurrent_metrics["success_rate"]),
            error_count=throughput_metrics["total_errors"] + concurrent_metrics["total_errors"],
            concurrent_requests=concurrent_metrics["concurrent_users"],
            test_duration_seconds=time.time() - start_time
        )
        
        # 性能基準對比
        benchmark_comparison = self._compare_with_benchmarks(metrics)
        
        # 判斷是否通過
        passed = self._evaluate_performance_compliance(metrics, benchmark_comparison)
        
        # 詳細信息
        details = {
            "response_time_details": response_time_metrics,
            "throughput_details": throughput_metrics,
            "concurrent_details": concurrent_metrics,
            "resource_details": resource_metrics,
            "test_configuration": {
                "response_time_iterations": 50,
                "throughput_duration": 15,
                "concurrent_users": 5,
                "resource_monitoring_duration": 30
            }
        }
        
        execution_time = time.time() - start_time
        
        return PerformanceTestResult(
            test_name="Performance Compliance",
            adapter_name=adapter_name,
            passed=passed,
            metrics=metrics,
            benchmark_comparison=benchmark_comparison,
            details=details,
            execution_time=execution_time
        )
    
    def _compare_with_benchmarks(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """與基準進行比較"""
        standards = self.performance_standards
        
        def get_performance_level(value: float, thresholds: Dict[str, float], reverse: bool = False) -> str:
            """獲取性能等級"""
            if reverse:  # 對於錯誤率等指標，值越小越好
                if value <= thresholds["excellent"]:
                    return "excellent"
                elif value <= thresholds["good"]:
                    return "good"
                elif value <= thresholds["acceptable"]:
                    return "acceptable"
                else:
                    return "poor"
            else:  # 對於吞吐量等指標，值越大越好
                if value >= thresholds["excellent"]:
                    return "excellent"
                elif value >= thresholds["good"]:
                    return "good"
                elif value >= thresholds["acceptable"]:
                    return "acceptable"
                else:
                    return "poor"
        
        return {
            "response_time": {
                "value": metrics.response_time_ms,
                "level": get_performance_level(metrics.response_time_ms, standards["response_time"], reverse=True),
                "benchmark": standards["response_time"]
            },
            "throughput": {
                "value": metrics.throughput_rps,
                "level": get_performance_level(metrics.throughput_rps, standards["throughput"]),
                "benchmark": standards["throughput"]
            },
            "memory_usage": {
                "value": metrics.memory_usage_mb,
                "level": get_performance_level(metrics.memory_usage_mb, standards["memory_usage"], reverse=True),
                "benchmark": standards["memory_usage"]
            },
            "cpu_usage": {
                "value": metrics.cpu_usage_percent,
                "level": get_performance_level(metrics.cpu_usage_percent, standards["cpu_usage"], reverse=True),
                "benchmark": standards["cpu_usage"]
            },
            "success_rate": {
                "value": metrics.success_rate,
                "level": get_performance_level(metrics.success_rate, standards["success_rate"]),
                "benchmark": standards["success_rate"]
            }
        }
    
    def _evaluate_performance_compliance(self, metrics: PerformanceMetrics, benchmark_comparison: Dict[str, Any]) -> bool:
        """評估性能合規性"""
        # 檢查關鍵指標是否達到可接受水平
        critical_checks = [
            benchmark_comparison["response_time"]["level"] in ["excellent", "good", "acceptable"],
            benchmark_comparison["success_rate"]["level"] in ["excellent", "good", "acceptable"],
            benchmark_comparison["memory_usage"]["level"] in ["excellent", "good", "acceptable"]
        ]
        
        # 至少80%的關鍵檢查通過
        return sum(critical_checks) >= len(critical_checks) * 0.8
    
    def run_performance_tests(self, adapter_name: str = None) -> List[PerformanceTestResult]:
        """運行性能測試"""
        logger.info("開始MCP性能合規性測試...")
        
        # 發現適配器
        try:
            from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
            registry = SafeMCPRegistry()
            adapters = registry.list_adapters()
            
            # 轉換為字典格式
            adapter_dict = {}
            for adapter_name_reg, adapter_instance in adapters:
                adapter_dict[adapter_name_reg] = {
                    "name": adapter_name_reg,
                    "instance": adapter_instance
                }
                
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
            # 限制測試數量以避免過長時間
            test_adapters = dict(list(adapter_dict.items())[:5])
        
        results = []
        
        for name, adapter_info in test_adapters.items():
            adapter_instance = adapter_info.get("instance")
            if not adapter_instance:
                logger.warning(f"無法獲取適配器實例: {name}")
                continue
            
            try:
                result = self.test_performance_compliance(name, adapter_instance)
                results.append(result)
                
            except Exception as e:
                logger.error(f"性能測試失敗 {name}: {e}")
        
        self.test_results = results
        logger.info(f"性能合規性測試完成，測試了 {len(results)} 個適配器")
        
        return results
    
    def generate_performance_report(self) -> str:
        """生成性能測試報告"""
        if not self.test_results:
            return "# MCP性能合規性測試報告\n\n無測試結果可用。"
        
        # 計算統計信息
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        
        avg_response_time = statistics.mean([r.metrics.response_time_ms for r in self.test_results])
        avg_throughput = statistics.mean([r.metrics.throughput_rps for r in self.test_results])
        avg_memory = statistics.mean([r.metrics.memory_usage_mb for r in self.test_results])
        avg_cpu = statistics.mean([r.metrics.cpu_usage_percent for r in self.test_results])
        avg_success_rate = statistics.mean([r.metrics.success_rate for r in self.test_results])
        
        report = f"""
# MCP性能合規性測試報告

## 📊 總體統計
- **測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **測試適配器數**: {total_tests}
- **通過測試數**: {passed_tests}
- **通過率**: {(passed_tests/total_tests*100):.1f}%

## 📈 平均性能指標
- **平均響應時間**: {avg_response_time:.1f} ms
- **平均吞吐量**: {avg_throughput:.1f} RPS
- **平均記憶體使用**: {avg_memory:.1f} MB
- **平均CPU使用率**: {avg_cpu:.1f}%
- **平均成功率**: {avg_success_rate:.1f}%

## 🔍 詳細測試結果
"""
        
        for result in self.test_results:
            status = "✅" if result.passed else "❌"
            metrics = result.metrics
            
            report += f"""
### {status} {result.adapter_name}
- **響應時間**: {metrics.response_time_ms:.1f} ms ({result.benchmark_comparison['response_time']['level']})
- **吞吐量**: {metrics.throughput_rps:.1f} RPS ({result.benchmark_comparison['throughput']['level']})
- **記憶體使用**: {metrics.memory_usage_mb:.1f} MB ({result.benchmark_comparison['memory_usage']['level']})
- **CPU使用率**: {metrics.cpu_usage_percent:.1f}% ({result.benchmark_comparison['cpu_usage']['level']})
- **成功率**: {metrics.success_rate:.1f}% ({result.benchmark_comparison['success_rate']['level']})
- **測試時長**: {result.execution_time:.1f} 秒
"""
        
        report += f"""
## 🎯 性能基準

### 響應時間標準 (毫秒)
- **優秀**: ≤ {self.performance_standards['response_time']['excellent']}
- **良好**: ≤ {self.performance_standards['response_time']['good']}
- **可接受**: ≤ {self.performance_standards['response_time']['acceptable']}
- **較差**: > {self.performance_standards['response_time']['poor']}

### 吞吐量標準 (RPS)
- **優秀**: ≥ {self.performance_standards['throughput']['excellent']}
- **良好**: ≥ {self.performance_standards['throughput']['good']}
- **可接受**: ≥ {self.performance_standards['throughput']['acceptable']}
- **較差**: < {self.performance_standards['throughput']['poor']}

## 📋 改進建議

### 性能優化
1. 優化響應時間超過1秒的適配器
2. 提升吞吐量低於20 RPS的適配器
3. 減少記憶體使用超過200MB的適配器
4. 降低CPU使用率超過50%的適配器

### 合規性改進
1. 確保所有適配器成功率達到95%以上
2. 實施性能監控和告警機制
3. 建立性能回歸測試
4. 優化資源使用效率

## 🏆 合規性評估

{'✅ 系統達到性能合規要求' if (passed_tests/total_tests) >= 0.8 else '⚠️ 系統需要性能優化' if (passed_tests/total_tests) >= 0.6 else '❌ 系統未達到性能合規要求'}

**整體通過率**: {(passed_tests/total_tests*100):.1f}%
"""
        
        return report

if __name__ == "__main__":
    tester = MCPPerformanceComplianceTester()
    results = tester.run_performance_tests()
    
    # 生成報告
    report = tester.generate_performance_report()
    
    # 保存報告
    report_file = Path("mcp_performance_compliance_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ MCP性能合規性測試完成")
    print(f"📄 報告已保存到: {report_file}")
    if results:
        passed_count = sum(1 for r in results if r.passed)
        print(f"🎯 測試結果: {passed_count}/{len(results)} 個適配器通過性能測試")
    else:
        print("⚠️ 未找到可測試的適配器")

