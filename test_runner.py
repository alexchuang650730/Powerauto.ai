#!/usr/bin/env python3
"""
PowerAutomation 測試運行器和報告生成器

運行所有真實測試並生成詳細報告
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TestResult:
    """測試結果"""
    test_file: str
    test_class: str
    test_method: str
    status: str  # "PASS", "FAIL", "ERROR", "SKIP"
    duration: float
    error_message: str = ""
    
@dataclass
class TestSuiteReport:
    """測試套件報告"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    skipped_tests: int = 0
    total_duration: float = 0.0
    success_rate: float = 0.0
    test_results: List[TestResult] = None
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []

class PowerAutomationTestRunner:
    """PowerAutomation測試運行器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_dir = self.project_root / "test"
        self.api_base_url = "http://localhost:8000"
        self.report = TestSuiteReport()
        
    def check_api_server(self) -> bool:
        """檢查API服務器是否運行"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def find_real_tests(self) -> List[Path]:
        """查找所有真實測試文件"""
        return list(self.test_dir.rglob("*_real.py"))
    
    def run_single_test(self, test_file: Path) -> List[TestResult]:
        """運行單個測試文件"""
        print(f"🧪 運行測試: {test_file.relative_to(self.project_root)}")
        
        start_time = time.time()
        try:
            # 運行測試
            result = subprocess.run(
                [sys.executable, str(test_file), "-v"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            # 解析測試結果
            test_results = self.parse_test_output(test_file, result, duration)
            
            if result.returncode == 0:
                print(f"✅ 測試通過: {test_file.name} ({duration:.2f}s)")
            else:
                print(f"❌ 測試失敗: {test_file.name} ({duration:.2f}s)")
                if result.stderr:
                    print(f"   錯誤: {result.stderr[:200]}...")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏰ 測試超時: {test_file.name} ({duration:.2f}s)")
            return [TestResult(
                test_file=str(test_file.relative_to(self.project_root)),
                test_class="Unknown",
                test_method="timeout",
                status="ERROR",
                duration=duration,
                error_message="測試執行超時"
            )]
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 測試異常: {test_file.name} - {str(e)}")
            return [TestResult(
                test_file=str(test_file.relative_to(self.project_root)),
                test_class="Unknown",
                test_method="exception",
                status="ERROR",
                duration=duration,
                error_message=str(e)
            )]
    
    def parse_test_output(self, test_file: Path, result: subprocess.CompletedProcess, duration: float) -> List[TestResult]:
        """解析測試輸出"""
        test_results = []
        
        if result.returncode == 0:
            # 測試通過
            lines = result.stderr.split('\n') if result.stderr else []
            test_count = 0
            
            for line in lines:
                if "Ran" in line and "test" in line:
                    try:
                        test_count = int(line.split()[1])
                    except:
                        test_count = 1
                    break
            
            if test_count == 0:
                test_count = 1
            
            # 創建通過的測試結果
            for i in range(test_count):
                test_results.append(TestResult(
                    test_file=str(test_file.relative_to(self.project_root)),
                    test_class=test_file.stem.replace("test_", "").replace("_real", ""),
                    test_method=f"test_{i+1}",
                    status="PASS",
                    duration=duration / test_count
                ))
        else:
            # 測試失敗或錯誤
            error_message = result.stderr if result.stderr else result.stdout
            test_results.append(TestResult(
                test_file=str(test_file.relative_to(self.project_root)),
                test_class=test_file.stem.replace("test_", "").replace("_real", ""),
                test_method="failed_test",
                status="FAIL" if "FAILED" in error_message else "ERROR",
                duration=duration,
                error_message=error_message[:500] if error_message else "未知錯誤"
            ))
        
        return test_results
    
    def run_all_tests(self) -> TestSuiteReport:
        """運行所有真實測試"""
        print("🚀 PowerAutomation 真實測試套件運行器")
        print("=" * 60)
        
        # 檢查API服務器
        if not self.check_api_server():
            print("❌ API服務器未運行，請先啟動 real_api_server.py")
            return self.report
        
        print("✅ API服務器運行正常")
        
        # 查找測試文件
        test_files = self.find_real_tests()
        print(f"📋 發現 {len(test_files)} 個真實測試文件")
        
        # 運行測試
        start_time = time.time()
        all_results = []
        
        for i, test_file in enumerate(test_files, 1):
            print(f"\n[{i}/{len(test_files)}] ", end="")
            test_results = self.run_single_test(test_file)
            all_results.extend(test_results)
        
        total_duration = time.time() - start_time
        
        # 統計結果
        self.report.test_results = all_results
        self.report.total_tests = len(all_results)
        self.report.total_duration = total_duration
        
        for result in all_results:
            if result.status == "PASS":
                self.report.passed_tests += 1
            elif result.status == "FAIL":
                self.report.failed_tests += 1
            elif result.status == "ERROR":
                self.report.error_tests += 1
            elif result.status == "SKIP":
                self.report.skipped_tests += 1
        
        if self.report.total_tests > 0:
            self.report.success_rate = self.report.passed_tests / self.report.total_tests
        
        return self.report
    
    def generate_report(self) -> str:
        """生成測試報告"""
        report = f"""
# PowerAutomation v0.53 真實測試套件報告

## 📊 測試摘要

- **執行時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **總測試數**: {self.report.total_tests}
- **通過測試**: {self.report.passed_tests} ✅
- **失敗測試**: {self.report.failed_tests} ❌
- **錯誤測試**: {self.report.error_tests} 💥
- **跳過測試**: {self.report.skipped_tests} ⏭️
- **成功率**: {self.report.success_rate:.1%}
- **總耗時**: {self.report.total_duration:.2f} 秒

## 🎯 測試結果分析

### 成功率評級
"""
        
        if self.report.success_rate >= 0.9:
            report += "🏆 **優秀** (≥90%) - 測試質量極佳\n"
        elif self.report.success_rate >= 0.8:
            report += "🥈 **良好** (≥80%) - 測試質量良好\n"
        elif self.report.success_rate >= 0.7:
            report += "🥉 **及格** (≥70%) - 測試質量一般\n"
        else:
            report += "⚠️ **需改進** (<70%) - 測試質量需要提升\n"
        
        # 詳細測試結果
        report += "\n## 📋 詳細測試結果\n\n"
        report += "| 測試文件 | 測試類 | 狀態 | 耗時 | 錯誤信息 |\n"
        report += "|---------|-------|------|------|----------|\n"
        
        for result in self.report.test_results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌", 
                "ERROR": "💥",
                "SKIP": "⏭️"
            }.get(result.status, "❓")
            
            error_msg = result.error_message[:50] + "..." if len(result.error_message) > 50 else result.error_message
            error_msg = error_msg.replace("|", "\\|").replace("\n", " ")
            
            report += f"| {result.test_file} | {result.test_class} | {status_icon} {result.status} | {result.duration:.2f}s | {error_msg} |\n"
        
        # 護城河指標
        report += "\n## 🏰 護城河強度評估\n\n"
        
        if self.report.success_rate >= 0.9:
            moat_strength = "堡壘級護城河 🏰"
        elif self.report.success_rate >= 0.8:
            moat_strength = "強護城河 🛡️"
        elif self.report.success_rate >= 0.7:
            moat_strength = "中等護城河 🚧"
        else:
            moat_strength = "弱護城河 ⚠️"
        
        report += f"**當前護城河強度**: {moat_strength}\n\n"
        
        # 改進建議
        report += "## 🔧 改進建議\n\n"
        
        if self.report.failed_tests > 0:
            report += f"1. **修復失敗測試**: {self.report.failed_tests} 個測試失敗，需要檢查業務邏輯\n"
        
        if self.report.error_tests > 0:
            report += f"2. **修復錯誤測試**: {self.report.error_tests} 個測試出現錯誤，需要檢查代碼實現\n"
        
        if self.report.success_rate < 0.9:
            report += "3. **提升測試覆蓋率**: 增加更多邊界條件和異常情況的測試\n"
            report += "4. **優化測試性能**: 減少測試執行時間，提高測試效率\n"
        
        report += "\n## 🚀 下一步行動\n\n"
        report += "1. 修復所有失敗和錯誤的測試\n"
        report += "2. 增加更多真實場景的測試用例\n"
        report += "3. 集成到CI/CD流程中\n"
        report += "4. 定期運行測試套件，監控質量變化\n"
        
        return report
    
    def save_json_report(self, filename: str):
        """保存JSON格式的測試報告"""
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.report.total_tests,
                "passed_tests": self.report.passed_tests,
                "failed_tests": self.report.failed_tests,
                "error_tests": self.report.error_tests,
                "skipped_tests": self.report.skipped_tests,
                "success_rate": self.report.success_rate,
                "total_duration": self.report.total_duration
            },
            "test_results": [asdict(result) for result in self.report.test_results]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

def main():
    """主函數"""
    project_root = "/home/ubuntu/Powerauto.ai"
    
    runner = PowerAutomationTestRunner(project_root)
    
    # 運行所有測試
    report = runner.run_all_tests()
    
    # 生成報告
    markdown_report = runner.generate_report()
    
    # 保存報告
    report_file = Path(project_root) / "test_execution_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    # 保存JSON報告
    json_report_file = Path(project_root) / "test_execution_results.json"
    runner.save_json_report(json_report_file)
    
    # 輸出摘要
    print("\n" + "=" * 60)
    print("📊 測試執行完成！")
    print(f"📋 總測試數: {report.total_tests}")
    print(f"✅ 通過: {report.passed_tests}")
    print(f"❌ 失敗: {report.failed_tests}")
    print(f"💥 錯誤: {report.error_tests}")
    print(f"📈 成功率: {report.success_rate:.1%}")
    print(f"⏱️ 總耗時: {report.total_duration:.2f} 秒")
    print(f"📄 詳細報告: {report_file}")
    print(f"📊 JSON數據: {json_report_file}")
    
    return report

if __name__ == "__main__":
    main()

