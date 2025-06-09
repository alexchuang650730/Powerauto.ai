#!/usr/bin/env python3
"""
第3層MCP合規測試集成驗證器
整合所有MCP合規測試模組，提供統一的測試和驗證接口

包括：
- 協議驗證測試
- 標準化測試框架
- 性能合規性測試
- 錯誤處理測試
- 能力聲明標準化
"""

import sys
import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 導入各個測試模組
try:
    from enhanced_protocol_validation import MCPProtocolValidator
    from standardized_test_framework import MCPStandardizedTestFramework
    from performance_compliance_tester import MCPPerformanceComplianceTester
    from error_handling_tester import MCPErrorHandlingTester
    from capability_standardizer import MCPCapabilityStandardizer
except ImportError as e:
    print(f"警告: 無法導入測試模組: {e}")

logger = logging.getLogger(__name__)

@dataclass
class Level3TestSummary:
    """第3層測試總結"""
    test_time: str
    total_adapters: int
    tested_adapters: int
    passed_adapters: int
    overall_compliance: float
    test_results: Dict[str, Any]
    recommendations: List[str]

class Level3MCPComplianceValidator:
    """第3層MCP合規測試集成驗證器"""
    
    def __init__(self):
        self.test_modules = {}
        self.test_results = {}
        self.summary = None
        
        # 初始化測試模組
        self._initialize_test_modules()
        
    def _initialize_test_modules(self):
        """初始化所有測試模組"""
        try:
            self.test_modules['protocol'] = MCPProtocolValidator()
            logger.info("✅ 協議驗證模組初始化成功")
        except Exception as e:
            logger.error(f"❌ 協議驗證模組初始化失敗: {e}")
        
        try:
            self.test_modules['standardization'] = MCPStandardizedTestFramework()
            logger.info("✅ 標準化測試模組初始化成功")
        except Exception as e:
            logger.error(f"❌ 標準化測試模組初始化失敗: {e}")
        
        try:
            self.test_modules['performance'] = MCPPerformanceComplianceTester()
            logger.info("✅ 性能測試模組初始化成功")
        except Exception as e:
            logger.error(f"❌ 性能測試模組初始化失敗: {e}")
        
        try:
            self.test_modules['error_handling'] = MCPErrorHandlingTester()
            logger.info("✅ 錯誤處理測試模組初始化成功")
        except Exception as e:
            logger.error(f"❌ 錯誤處理測試模組初始化失敗: {e}")
        
        try:
            self.test_modules['capability'] = MCPCapabilityStandardizer()
            logger.info("✅ 能力標準化模組初始化成功")
        except Exception as e:
            logger.error(f"❌ 能力標準化模組初始化失敗: {e}")
    
    def run_protocol_validation(self) -> Dict[str, Any]:
        """運行協議驗證測試"""
        logger.info("🔍 開始協議驗證測試...")
        
        if 'protocol' not in self.test_modules:
            return {"error": "協議驗證模組未初始化"}
        
        try:
            validator = self.test_modules['protocol']
            results = validator.run_validation_tests()
            
            # 生成報告
            report = validator.generate_validation_report()
            
            # 保存報告
            report_file = Path("protocol_validation_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return {
                "status": "completed",
                "results_count": len(results),
                "compliance_score": validator.calculate_overall_compliance(),
                "report_file": str(report_file)
            }
            
        except Exception as e:
            logger.error(f"協議驗證測試失敗: {e}")
            return {"error": str(e)}
    
    def run_standardization_tests(self) -> Dict[str, Any]:
        """運行標準化測試"""
        logger.info("📋 開始標準化測試...")
        
        if 'standardization' not in self.test_modules:
            return {"error": "標準化測試模組未初始化"}
        
        try:
            framework = self.test_modules['standardization']
            results = framework.run_standardization_tests()
            
            # 生成報告
            report = framework.generate_standardization_report()
            
            # 保存報告
            report_file = Path("standardization_test_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return {
                "status": "completed",
                "results_count": len(results),
                "compliance_score": framework.stats.get('overall_compliance', 0),
                "report_file": str(report_file)
            }
            
        except Exception as e:
            logger.error(f"標準化測試失敗: {e}")
            return {"error": str(e)}
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """運行性能測試"""
        logger.info("⚡ 開始性能合規性測試...")
        
        if 'performance' not in self.test_modules:
            return {"error": "性能測試模組未初始化"}
        
        try:
            tester = self.test_modules['performance']
            results = tester.run_performance_tests()
            
            # 生成報告
            report = tester.generate_performance_report()
            
            # 保存報告
            report_file = Path("performance_compliance_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            passed_count = sum(1 for r in results if r.passed) if results else 0
            
            return {
                "status": "completed",
                "results_count": len(results),
                "passed_count": passed_count,
                "pass_rate": passed_count / len(results) if results else 0,
                "report_file": str(report_file)
            }
            
        except Exception as e:
            logger.error(f"性能測試失敗: {e}")
            return {"error": str(e)}
    
    def run_error_handling_tests(self) -> Dict[str, Any]:
        """運行錯誤處理測試"""
        logger.info("🛡️ 開始錯誤處理測試...")
        
        if 'error_handling' not in self.test_modules:
            return {"error": "錯誤處理測試模組未初始化"}
        
        try:
            tester = self.test_modules['error_handling']
            results = tester.run_error_handling_tests()
            
            # 生成報告
            report = tester.generate_error_handling_report()
            
            # 保存報告
            report_file = Path("error_handling_test_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            passed_count = sum(1 for r in results if r.passed) if results else 0
            handled_count = sum(1 for r in results if r.error_handled) if results else 0
            
            return {
                "status": "completed",
                "results_count": len(results),
                "passed_count": passed_count,
                "handled_count": handled_count,
                "pass_rate": passed_count / len(results) if results else 0,
                "handle_rate": handled_count / len(results) if results else 0,
                "report_file": str(report_file)
            }
            
        except Exception as e:
            logger.error(f"錯誤處理測試失敗: {e}")
            return {"error": str(e)}
    
    def run_capability_standardization(self) -> Dict[str, Any]:
        """運行能力標準化"""
        logger.info("🎯 開始能力聲明標準化...")
        
        if 'capability' not in self.test_modules:
            return {"error": "能力標準化模組未初始化"}
        
        try:
            standardizer = self.test_modules['capability']
            results = standardizer.run_capability_standardization()
            
            # 生成報告
            report = standardizer.generate_standardization_report()
            
            # 保存報告
            report_file = Path("capability_standardization_report.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            valid_count = sum(1 for r in results if r.is_valid) if results else 0
            avg_compliance = sum(r.compliance_score for r in results) / len(results) if results else 0
            
            return {
                "status": "completed",
                "results_count": len(results),
                "valid_count": valid_count,
                "validity_rate": valid_count / len(results) if results else 0,
                "avg_compliance": avg_compliance,
                "report_file": str(report_file)
            }
            
        except Exception as e:
            logger.error(f"能力標準化失敗: {e}")
            return {"error": str(e)}
    
    def run_comprehensive_tests(self) -> Level3TestSummary:
        """運行完整的第3層測試"""
        logger.info("🚀 開始第3層MCP合規測試完整驗證...")
        
        start_time = time.time()
        test_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 運行所有測試
        self.test_results['protocol'] = self.run_protocol_validation()
        self.test_results['standardization'] = self.run_standardization_tests()
        self.test_results['performance'] = self.run_performance_tests()
        self.test_results['error_handling'] = self.run_error_handling_tests()
        self.test_results['capability'] = self.run_capability_standardization()
        
        # 計算總體統計
        total_adapters = 0
        tested_adapters = 0
        passed_tests = 0
        total_tests = 0
        
        for test_type, result in self.test_results.items():
            if 'error' not in result:
                results_count = result.get('results_count', 0)
                tested_adapters = max(tested_adapters, results_count)
                
                if test_type == 'protocol':
                    compliance_score = result.get('compliance_score', 0)
                    if compliance_score >= 0.8:
                        passed_tests += 1
                    total_tests += 1
                elif test_type in ['performance', 'error_handling']:
                    pass_rate = result.get('pass_rate', 0)
                    if pass_rate >= 0.8:
                        passed_tests += 1
                    total_tests += 1
                elif test_type == 'capability':
                    validity_rate = result.get('validity_rate', 0)
                    if validity_rate >= 0.8:
                        passed_tests += 1
                    total_tests += 1
        
        # 計算整體合規性
        overall_compliance = passed_tests / total_tests if total_tests > 0 else 0
        
        # 生成建議
        recommendations = self._generate_recommendations()
        
        # 創建總結
        self.summary = Level3TestSummary(
            test_time=test_start_time,
            total_adapters=tested_adapters,
            tested_adapters=tested_adapters,
            passed_adapters=passed_tests,
            overall_compliance=overall_compliance,
            test_results=self.test_results,
            recommendations=recommendations
        )
        
        execution_time = time.time() - start_time
        logger.info(f"✅ 第3層測試完成，耗時 {execution_time:.1f} 秒")
        
        return self.summary
    
    def _generate_recommendations(self) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 分析測試結果並生成建議
        for test_type, result in self.test_results.items():
            if 'error' in result:
                recommendations.append(f"修復 {test_type} 測試模組的問題: {result['error']}")
                continue
            
            if test_type == 'protocol':
                compliance = result.get('compliance_score', 0)
                if compliance < 0.8:
                    recommendations.append("改進MCP協議合規性，確保所有適配器符合協議標準")
            
            elif test_type == 'standardization':
                compliance = result.get('compliance_score', 0)
                if compliance < 0.8:
                    recommendations.append("統一適配器接口標準，實施標準化測試框架")
            
            elif test_type == 'performance':
                pass_rate = result.get('pass_rate', 0)
                if pass_rate < 0.8:
                    recommendations.append("優化適配器性能，確保響應時間和吞吐量達到標準")
            
            elif test_type == 'error_handling':
                pass_rate = result.get('pass_rate', 0)
                handle_rate = result.get('handle_rate', 0)
                if pass_rate < 0.8:
                    recommendations.append("完善錯誤處理機制，提高錯誤處理的正確性")
                if handle_rate < 0.9:
                    recommendations.append("增強錯誤檢測和處理能力，確保系統穩定性")
            
            elif test_type == 'capability':
                validity_rate = result.get('validity_rate', 0)
                if validity_rate < 0.8:
                    recommendations.append("標準化能力聲明格式，完善能力文檔和驗證")
        
        # 添加通用建議
        if self.summary and self.summary.overall_compliance < 0.8:
            recommendations.extend([
                "建立持續集成測試流程，確保代碼質量",
                "實施自動化測試和監控機制",
                "定期進行合規性審查和改進",
                "建立測試覆蓋率監控和報告機制"
            ])
        
        return recommendations
    
    def generate_comprehensive_report(self) -> str:
        """生成完整的第3層測試報告"""
        if not self.summary:
            return "# 第3層MCP合規測試報告\n\n測試尚未運行。"
        
        summary = self.summary
        
        report = f"""
# 第3層MCP合規測試完整報告

## 📊 執行總結
- **測試時間**: {summary.test_time}
- **測試適配器數**: {summary.tested_adapters}
- **通過測試模組數**: {summary.passed_adapters}/5
- **整體合規性**: {summary.overall_compliance:.1%}

## 🎯 合規性評估

{'✅ 第3層測試全面通過' if summary.overall_compliance >= 0.8 else '⚠️ 第3層測試需要改進' if summary.overall_compliance >= 0.6 else '❌ 第3層測試未達標準'}

## 📋 詳細測試結果

### 1. 協議驗證測試
"""
        
        protocol_result = summary.test_results.get('protocol', {})
        if 'error' in protocol_result:
            report += f"❌ **失敗**: {protocol_result['error']}\n"
        else:
            compliance = protocol_result.get('compliance_score', 0)
            status = "✅" if compliance >= 0.8 else "⚠️" if compliance >= 0.6 else "❌"
            report += f"{status} **合規分數**: {compliance:.1%}\n"
            report += f"- 測試結果數: {protocol_result.get('results_count', 0)}\n"
            report += f"- 報告文件: {protocol_result.get('report_file', 'N/A')}\n"
        
        report += f"""
### 2. 標準化測試
"""
        
        std_result = summary.test_results.get('standardization', {})
        if 'error' in std_result:
            report += f"❌ **失敗**: {std_result['error']}\n"
        else:
            compliance = std_result.get('compliance_score', 0)
            status = "✅" if compliance >= 0.8 else "⚠️" if compliance >= 0.6 else "❌"
            report += f"{status} **合規分數**: {compliance:.1%}\n"
            report += f"- 測試結果數: {std_result.get('results_count', 0)}\n"
            report += f"- 報告文件: {std_result.get('report_file', 'N/A')}\n"
        
        report += f"""
### 3. 性能合規性測試
"""
        
        perf_result = summary.test_results.get('performance', {})
        if 'error' in perf_result:
            report += f"❌ **失敗**: {perf_result['error']}\n"
        else:
            pass_rate = perf_result.get('pass_rate', 0)
            status = "✅" if pass_rate >= 0.8 else "⚠️" if pass_rate >= 0.6 else "❌"
            report += f"{status} **通過率**: {pass_rate:.1%}\n"
            report += f"- 測試結果數: {perf_result.get('results_count', 0)}\n"
            report += f"- 通過數: {perf_result.get('passed_count', 0)}\n"
            report += f"- 報告文件: {perf_result.get('report_file', 'N/A')}\n"
        
        report += f"""
### 4. 錯誤處理測試
"""
        
        error_result = summary.test_results.get('error_handling', {})
        if 'error' in error_result:
            report += f"❌ **失敗**: {error_result['error']}\n"
        else:
            pass_rate = error_result.get('pass_rate', 0)
            handle_rate = error_result.get('handle_rate', 0)
            status = "✅" if pass_rate >= 0.8 and handle_rate >= 0.9 else "⚠️" if pass_rate >= 0.6 else "❌"
            report += f"{status} **通過率**: {pass_rate:.1%}, **處理率**: {handle_rate:.1%}\n"
            report += f"- 測試結果數: {error_result.get('results_count', 0)}\n"
            report += f"- 通過數: {error_result.get('passed_count', 0)}\n"
            report += f"- 處理數: {error_result.get('handled_count', 0)}\n"
            report += f"- 報告文件: {error_result.get('report_file', 'N/A')}\n"
        
        report += f"""
### 5. 能力聲明標準化
"""
        
        cap_result = summary.test_results.get('capability', {})
        if 'error' in cap_result:
            report += f"❌ **失敗**: {cap_result['error']}\n"
        else:
            validity_rate = cap_result.get('validity_rate', 0)
            avg_compliance = cap_result.get('avg_compliance', 0)
            status = "✅" if validity_rate >= 0.8 else "⚠️" if validity_rate >= 0.6 else "❌"
            report += f"{status} **有效率**: {validity_rate:.1%}, **平均合規**: {avg_compliance:.1%}\n"
            report += f"- 測試結果數: {cap_result.get('results_count', 0)}\n"
            report += f"- 有效數: {cap_result.get('valid_count', 0)}\n"
            report += f"- 報告文件: {cap_result.get('report_file', 'N/A')}\n"
        
        report += f"""
## 💡 改進建議

"""
        
        for i, recommendation in enumerate(summary.recommendations, 1):
            report += f"{i}. {recommendation}\n"
        
        report += f"""
## 📈 下一步行動

### 立即行動
1. 修復所有失敗的測試模組
2. 提升合規性低於80%的測試項目
3. 實施自動化測試流程

### 中期目標
1. 建立持續集成測試管道
2. 實施性能監控和告警
3. 完善文檔和標準化流程

### 長期規劃
1. 建立企業級質量保證體系
2. 實施全面的合規性管理
3. 持續優化和改進測試框架

## 🏆 結論

第3層MCP合規測試{'已達到企業級標準' if summary.overall_compliance >= 0.8 else '需要進一步改進以達到企業級標準'}。

**整體合規性評分**: {summary.overall_compliance:.1%}
"""
        
        return report

if __name__ == "__main__":
    # 配置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    validator = Level3MCPComplianceValidator()
    
    # 運行完整測試
    summary = validator.run_comprehensive_tests()
    
    # 生成完整報告
    report = validator.generate_comprehensive_report()
    
    # 保存報告
    report_file = Path("level3_mcp_compliance_comprehensive_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存測試結果JSON
    results_file = Path("level3_test_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(summary), f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n🎉 第3層MCP合規測試完成！")
    print(f"📄 完整報告: {report_file}")
    print(f"📊 測試結果: {results_file}")
    print(f"🎯 整體合規性: {summary.overall_compliance:.1%}")
    print(f"📋 改進建議數: {len(summary.recommendations)}")
    
    if summary.overall_compliance >= 0.8:
        print("✅ 恭喜！第3層測試達到企業級標準")
    elif summary.overall_compliance >= 0.6:
        print("⚠️ 第3層測試需要改進以達到標準")
    else:
        print("❌ 第3層測試未達到基本要求，需要重點改進")

