#!/usr/bin/env python3
"""
標準化測試方法接口
為所有測試模組提供統一的接口標準和基礎類

主要功能：
- 統一的測試接口定義
- 標準化的測試結果格式
- 通用的測試基礎類
- 測試方法命名規範
"""

import sys
import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Union, Protocol, TypeVar, Generic
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """測試狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"

class TestSeverity(Enum):
    """測試嚴重性枚舉"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TestResult:
    """標準化測試結果"""
    test_name: str
    adapter_name: str
    status: TestStatus
    score: float
    execution_time: float
    message: str
    details: Dict[str, Any]
    severity: TestSeverity
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class BaseTestFramework(ABC):
    """測試框架基礎類"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.test_results: List[TestResult] = []
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # 配置日誌
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def run_tests(self, adapter_name: Optional[str] = None) -> List[TestResult]:
        """運行測試的抽象方法"""
        pass
    
    def get_adapters(self) -> List[tuple]:
        """獲取適配器列表"""
        try:
            # 導入統一適配器註冊表
            from mcptool.adapters.core.unified_adapter_registry import UnifiedAdapterRegistry
            
            registry = UnifiedAdapterRegistry()
            adapters = registry.get_all_adapters()
            
            self.logger.info(f"從統一註冊表獲取到 {len(adapters)} 個適配器")
            return adapters
            
        except Exception as e:
            self.logger.warning(f"無法從統一註冊表獲取適配器: {e}")
            
            # 回退到安全註冊表
            try:
                from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
                
                registry = SafeMCPRegistry()
                registered_mcps = registry.list_registered_mcps()
                
                adapters = []
                for mcp_info in registered_mcps:
                    try:
                        adapter_instance = registry.get_mcp_instance(mcp_info["name"])
                        if adapter_instance:
                            adapters.append((mcp_info["name"], adapter_instance))
                    except Exception as adapter_error:
                        self.logger.debug(f"無法獲取適配器實例 {mcp_info['name']}: {adapter_error}")
                
                self.logger.info(f"從安全註冊表獲取到 {len(adapters)} 個適配器")
                return adapters
                
            except Exception as e2:
                self.logger.error(f"無法從安全註冊表獲取適配器: {e2}")
                return []
    
    def create_test_result(
        self,
        test_name: str,
        adapter_name: str,
        passed: bool,
        score: float,
        execution_time: float,
        message: str,
        details: Dict[str, Any] = None,
        severity: TestSeverity = TestSeverity.MEDIUM
    ) -> TestResult:
        """創建標準化測試結果"""
        
        status = TestStatus.PASSED if passed else TestStatus.FAILED
        
        return TestResult(
            test_name=test_name,
            adapter_name=adapter_name,
            status=status,
            score=score,
            execution_time=execution_time,
            message=message,
            details=details or {},
            severity=severity
        )
    
    def add_test_result(self, result: TestResult):
        """添加測試結果"""
        self.test_results.append(result)
        
        status_icon = "✅" if result.status == TestStatus.PASSED else "❌"
        self.logger.info(f"測試 {result.test_name} 完成: {result.status.value}")
    
    def get_test_summary(self) -> Dict[str, Any]:
        """獲取測試摘要"""
        if not self.test_results:
            return {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "pass_rate": 0.0,
                "overall_score": 0.0,
                "total_time": 0.0
            }
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == TestStatus.PASSED)
        failed_tests = total_tests - passed_tests
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0
        
        # 計算總體分數（加權平均）
        total_score = sum(r.score for r in self.test_results)
        overall_score = total_score / total_tests if total_tests > 0 else 0.0
        
        # 計算總執行時間
        total_time = sum(r.execution_time for r in self.test_results)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
            "overall_score": overall_score,
            "total_time": total_time
        }
    
    def generate_report(self) -> str:
        """生成測試報告"""
        summary = self.get_test_summary()
        
        report = f"""# {self.name} 測試報告

## 測試摘要
- **測試框架**: {self.name}
- **描述**: {self.description}
- **測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 統計信息
- **總測試數**: {summary['total_tests']}
- **通過測試**: {summary['passed_tests']}
- **失敗測試**: {summary['failed_tests']}
- **通過率**: {summary['pass_rate']:.1%}
- **總體分數**: {summary['overall_score']:.1f}
- **總執行時間**: {summary['total_time']:.2f}秒

## 詳細結果

"""
        
        # 按適配器分組顯示結果
        adapter_results = {}
        for result in self.test_results:
            if result.adapter_name not in adapter_results:
                adapter_results[result.adapter_name] = []
            adapter_results[result.adapter_name].append(result)
        
        for adapter_name, results in adapter_results.items():
            adapter_passed = sum(1 for r in results if r.status == TestStatus.PASSED)
            adapter_total = len(results)
            adapter_pass_rate = adapter_passed / adapter_total if adapter_total > 0 else 0.0
            
            status_icon = "✅" if adapter_pass_rate >= 0.8 else "⚠️" if adapter_pass_rate >= 0.6 else "❌"
            
            report += f"### {status_icon} {adapter_name}\n"
            report += f"- **通過率**: {adapter_pass_rate:.1%} ({adapter_passed}/{adapter_total})\n"
            
            for result in results:
                result_icon = "✅" if result.status == TestStatus.PASSED else "❌"
                report += f"  - {result_icon} {result.test_name}: {result.message} (分數: {result.score:.1f})\n"
                
                if result.status != TestStatus.PASSED and result.details.get("error"):
                    report += f"    - 錯誤: {result.details['error']}\n"
            
            report += "\n"
        
        return report
    
    def save_results(self, output_dir: str):
        """保存測試結果到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON結果
        json_file = output_path / f"{self.name}_results_{timestamp}.json"
        
        # 轉換結果為可序列化格式
        serializable_results = []
        for result in self.test_results:
            result_dict = asdict(result)
            # 轉換枚舉為字符串
            result_dict['status'] = result.status.value
            result_dict['severity'] = result.severity.value
            serializable_results.append(result_dict)
        
        results_data = {
            "framework": self.name,
            "description": self.description,
            "timestamp": timestamp,
            "summary": self.get_test_summary(),
            "results": serializable_results
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        # 保存Markdown報告
        md_file = output_path / f"{self.name}_report_{timestamp}.md"
        report = self.generate_report()
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"測試結果已保存到: {json_file} 和 {md_file}")

class StandardizedTestRunner:
    """標準化測試運行器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.StandardizedTestRunner")
    
    def run_framework(self, framework: BaseTestFramework, adapter_name: Optional[str] = None) -> List[TestResult]:
        """運行指定的測試框架"""
        self.logger.info(f"開始運行測試框架: {framework.name}")
        
        start_time = time.time()
        results = framework.run_tests(adapter_name)
        execution_time = time.time() - start_time
        
        summary = framework.get_test_summary()
        
        self.logger.info(f"測試框架 {framework.name} 完成")
        self.logger.info(f"結果: {summary['passed_tests']}/{summary['total_tests']} 通過 ({summary['pass_rate']:.1%})")
        self.logger.info(f"執行時間: {execution_time:.2f}秒")
        
        return results

# 測試接口協議
class TestableAdapter(Protocol):
    """可測試適配器的協議定義"""
    
    def get_name(self) -> str:
        """獲取適配器名稱"""
        ...
    
    def get_capabilities(self) -> List[str]:
        """獲取適配器能力"""
        ...
    
    def process(self, data: Any) -> Any:
        """處理數據（可選方法）"""
        ...

# 工具函數
def create_test_framework(name: str, description: str) -> type:
    """動態創建測試框架類"""
    
    class DynamicTestFramework(BaseTestFramework):
        def __init__(self):
            super().__init__(name, description)
        
        def run_tests(self, adapter_name: Optional[str] = None) -> List[TestResult]:
            # 默認實現
            self.logger.info("運行默認測試...")
            return []
    
    return DynamicTestFramework

def validate_test_result(result: TestResult) -> bool:
    """驗證測試結果的有效性"""
    try:
        # 檢查必需字段
        if not result.test_name or not result.adapter_name:
            return False
        
        # 檢查分數範圍
        if not (0 <= result.score <= 100):
            return False
        
        # 檢查執行時間
        if result.execution_time < 0:
            return False
        
        # 檢查狀態和嚴重性
        if not isinstance(result.status, TestStatus):
            return False
        
        if not isinstance(result.severity, TestSeverity):
            return False
        
        return True
        
    except Exception:
        return False

# 導出的主要類和函數
__all__ = [
    'TestStatus',
    'TestSeverity', 
    'TestResult',
    'BaseTestFramework',
    'StandardizedTestRunner',
    'TestableAdapter',
    'create_test_framework',
    'validate_test_result'
]

