#!/usr/bin/env python3
"""
十層測試架構CLI驅動程序
統一的命令行接口，用於運行各層級測試

支持功能：
- 運行單個層級測試
- 運行多個層級測試
- 運行所有層級測試
- 生成綜合報告
- 測試結果管理
"""

import sys
import os
import argparse
import time
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 導入測試框架
from test.standardized_test_interface import StandardizedTestRunner
from test.optimized_module_importer import import_test_framework

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TenLayerTestCLI:
    """十層測試架構CLI"""
    
    def __init__(self):
        self.test_runner = StandardizedTestRunner()
        self.available_levels = list(range(1, 11))
        self.level_descriptions = {
            1: "單元測試 + 代碼質量 (基礎層)",
            2: "集成測試 + 智能體協作 (業務層)",
            3: "MCP合規測試 + 標準化驗證 (業務層)",
            4: "端到端測試 + 用戶場景 (業務層)",
            5: "性能測試 + 四層兜底性能 (戰術層)",
            6: "安全測試 + 企業級安全 (戰術層)",
            7: "兼容性測試 + 編輯器集成 (戰術層)",
            8: "壓力測試 + 護城河驗證 (戰略層)",
            9: "GAIA基準測試 + 競對比較 (戰略層)",
            10: "AI能力評估 + 標準基準測試 (戰略層)"
        }
        
        # 已實現的測試框架
        self.implemented_frameworks = {
            1: "test.level1.enhanced_unit_test_framework",
            2: "test.level2.enhanced_integration_test_framework", 
            3: "test.level3.enhanced_mcp_compliance_framework"
        }
    
    def run_level_test(self, level: int, adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """運行指定層級的測試"""
        if level not in self.available_levels:
            raise ValueError(f"無效的測試層級: {level}")
        
        print(f"🚀 開始運行Level {level}測試...")
        print(f"📋 {self.level_descriptions[level]}")
        
        if level not in self.implemented_frameworks:
            print(f"⚠️  Level {level}測試框架尚未實現")
            return {
                "level": level,
                "status": "not_implemented",
                "message": f"Level {level}測試框架尚未實現"
            }
        
        try:
            # 動態導入測試框架
            framework_module = self.implemented_frameworks[level]
            
            if level == 1:
                from test.level1.enhanced_unit_test_framework import Level1UnitTestFramework
                framework = Level1UnitTestFramework()
            elif level == 2:
                from test.level2.enhanced_integration_test_framework import Level2IntegrationTestFramework
                framework = Level2IntegrationTestFramework()
            elif level == 3:
                from test.level3.enhanced_mcp_compliance_framework import Level3MCPComplianceFramework
                framework = Level3MCPComplianceFramework()
            else:
                raise ImportError(f"未找到Level {level}的測試框架")
            
            # 運行測試
            start_time = time.time()
            results = framework.run_tests(adapter_name)
            execution_time = time.time() - start_time
            
            # 獲取測試摘要
            summary = framework.get_test_summary()
            
            # 保存結果
            framework.save_results(f"test/level{level}")
            
            print(f"✅ Level {level}測試完成")
            print(f"📊 測試摘要: {summary['passed_tests']}/{summary['total_tests']} 通過 ({summary['pass_rate']:.1%})")
            print(f"⏱️  執行時間: {execution_time:.2f}秒")
            
            return {
                "level": level,
                "status": "completed",
                "summary": summary,
                "execution_time": execution_time,
                "results_count": len(results)
            }
            
        except Exception as e:
            error_msg = f"Level {level}測試執行失敗: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(error_msg, exc_info=True)
            
            return {
                "level": level,
                "status": "error",
                "error": error_msg
            }
    
    def run_multiple_levels(self, levels: List[int], adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """運行多個層級的測試"""
        print(f"🎯 開始運行多層級測試: Level {', '.join(map(str, levels))}")
        
        results = {}
        total_start_time = time.time()
        
        for level in levels:
            print(f"\n{'='*60}")
            result = self.run_level_test(level, adapter_name)
            results[f"level_{level}"] = result
        
        total_execution_time = time.time() - total_start_time
        
        # 計算總體統計
        completed_levels = [r for r in results.values() if r["status"] == "completed"]
        total_tests = sum(r["summary"]["total_tests"] for r in completed_levels)
        total_passed = sum(r["summary"]["passed_tests"] for r in completed_levels)
        overall_pass_rate = total_passed / total_tests if total_tests > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"🏆 多層級測試完成")
        print(f"📊 總體統計:")
        print(f"   完成層級: {len(completed_levels)}/{len(levels)}")
        print(f"   總測試數: {total_tests}")
        print(f"   總通過數: {total_passed}")
        print(f"   總體通過率: {overall_pass_rate:.1%}")
        print(f"   總執行時間: {total_execution_time:.2f}秒")
        
        return {
            "levels": levels,
            "results": results,
            "summary": {
                "completed_levels": len(completed_levels),
                "total_levels": len(levels),
                "total_tests": total_tests,
                "total_passed": total_passed,
                "overall_pass_rate": overall_pass_rate,
                "total_execution_time": total_execution_time
            }
        }
    
    def run_all_implemented_tests(self, adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """運行所有已實現的測試"""
        implemented_levels = list(self.implemented_frameworks.keys())
        return self.run_multiple_levels(implemented_levels, adapter_name)
    
    def list_available_levels(self):
        """列出可用的測試層級"""
        print("📋 可用的測試層級:")
        print()
        
        for level in self.available_levels:
            status = "✅ 已實現" if level in self.implemented_frameworks else "⏳ 待實現"
            print(f"Level {level:2d}: {self.level_descriptions[level]}")
            print(f"          {status}")
            print()
    
    def generate_comprehensive_report(self, results: Dict[str, Any], output_file: Optional[str] = None):
        """生成綜合測試報告"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"comprehensive_test_report_{timestamp}.md"
        
        report = f"""# PowerAutomation 十層測試架構綜合報告

## 📊 測試執行摘要
- **測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **測試層級**: {', '.join(f"Level {level}" for level in results.get('levels', []))}

"""
        
        if "summary" in results:
            summary = results["summary"]
            report += f"""## 🎯 總體統計
- **完成層級**: {summary['completed_levels']}/{summary['total_levels']}
- **總測試數**: {summary['total_tests']}
- **總通過數**: {summary['total_passed']}
- **總體通過率**: {summary['overall_pass_rate']:.1%}
- **總執行時間**: {summary['total_execution_time']:.2f}秒

"""
        
        # 各層級詳細結果
        report += "## 📋 各層級測試結果\n\n"
        
        for level_key, level_result in results.get("results", {}).items():
            level_num = level_key.split("_")[1]
            level_desc = self.level_descriptions.get(int(level_num), "未知層級")
            
            if level_result["status"] == "completed":
                summary = level_result["summary"]
                status_icon = "✅" if summary["pass_rate"] >= 0.8 else "⚠️" if summary["pass_rate"] >= 0.6 else "❌"
                
                report += f"""### {status_icon} Level {level_num}: {level_desc}
- **通過率**: {summary['pass_rate']:.1%} ({summary['passed_tests']}/{summary['total_tests']})
- **總體分數**: {summary['overall_score']:.1f}
- **執行時間**: {level_result['execution_time']:.2f}秒

"""
            elif level_result["status"] == "not_implemented":
                report += f"""### ⏳ Level {level_num}: {level_desc}
- **狀態**: 尚未實現

"""
            else:
                report += f"""### ❌ Level {level_num}: {level_desc}
- **狀態**: 執行失敗
- **錯誤**: {level_result.get('error', '未知錯誤')}

"""
        
        # 保存報告
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 綜合測試報告已保存到: {output_path}")
        return output_path

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation 十層測試架構CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --list                    # 列出所有可用層級
  %(prog)s --level 1                 # 運行Level 1測試
  %(prog)s --level 1 2 3             # 運行Level 1-3測試
  %(prog)s --all                     # 運行所有已實現的測試
  %(prog)s --level 1 --adapter simple_gemini  # 測試特定適配器
        """
    )
    
    parser.add_argument(
        "--level", "-l",
        type=int,
        nargs="+",
        help="要運行的測試層級 (1-10)"
    )
    
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="運行所有已實現的測試"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有可用的測試層級"
    )
    
    parser.add_argument(
        "--adapter",
        type=str,
        help="指定要測試的適配器名稱"
    )
    
    parser.add_argument(
        "--report", "-r",
        type=str,
        help="生成綜合報告的文件名"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細輸出"
    )
    
    args = parser.parse_args()
    
    # 配置日誌級別
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 創建CLI實例
    cli = TenLayerTestCLI()
    
    try:
        if args.list:
            cli.list_available_levels()
            
        elif args.all:
            results = cli.run_all_implemented_tests(args.adapter)
            if args.report:
                cli.generate_comprehensive_report(results, args.report)
                
        elif args.level:
            if len(args.level) == 1:
                result = cli.run_level_test(args.level[0], args.adapter)
            else:
                results = cli.run_multiple_levels(args.level, args.adapter)
                if args.report:
                    cli.generate_comprehensive_report(results, args.report)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

