#!/usr/bin/env python3
"""
十層測試架構CLI驅動程序 v2.0
統一的命令行接口，用於運行各層級測試

支持功能：
- 運行單個層級測試
- 運行多個層級測試
- 運行所有層級測試
- 生成綜合報告
- 測試結果管理
- 實時進度顯示
- 詳細錯誤報告
"""

import sys
import os
import argparse
import time
import json
import logging
import traceback
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TenLayerTestCLI:
    """十層測試架構CLI v2.0"""
    
    def __init__(self):
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
        
        # 已實現的測試框架映射
        self.implemented_frameworks = {
            1: {
                "module": "test.level1.enhanced_unit_test_framework",
                "class": "Level1UnitTestFramework",
                "status": "✅ 已實現"
            },
            2: {
                "module": "test.level2.enhanced_integration_test_framework",
                "class": "Level2IntegrationTestFramework", 
                "status": "✅ 已實現"
            },
            3: {
                "module": "test.level3.enhanced_mcp_compliance_framework",
                "class": "Level3MCPComplianceFramework",
                "status": "✅ 已實現"
            },
            4: {
                "module": "test.level4.end_to_end_test_framework",
                "class": "EndToEndTestFramework",
                "status": "✅ 已實現"
            },
            5: {
                "module": None,
                "class": None,
                "status": "⏳ 待實現"
            },
            6: {
                "module": "test.level6.enterprise_security_framework",
                "class": "EnterpriseSecurityFramework",
                "status": "✅ 已實現"
            },
            7: {
                "module": "test.level7.compatibility_test_framework",
                "class": "CompatibilityTestFramework",
                "status": "✅ 已實現"
            },
            8: {
                "module": "test.level8.stress_test_framework",
                "class": "StressTestFramework",
                "status": "✅ 已實現"
            },
            9: {
                "module": "test.level9.gaia",
                "class": "GAIATestFramework",
                "status": "✅ 已實現"
            },
            10: {
                "module": "test.level10.ai_capability_evaluator",
                "class": "AICapabilityEvaluator",
                "status": "✅ 已實現"
            }
        }
    
    def list_available_levels(self):
        """列出所有可用的測試層級"""
        print("🏗️  PowerAutomation 十層測試架構")
        print("=" * 60)
        
        for level in self.available_levels:
            status = self.implemented_frameworks[level]["status"]
            description = self.level_descriptions[level]
            print(f"Level {level:2d}: {status} {description}")
        
        print("=" * 60)
        implemented_count = sum(1 for info in self.implemented_frameworks.values() if info["status"] == "✅ 已實現")
        print(f"📊 總進度: {implemented_count}/10 層級已實現 ({implemented_count/10*100:.0f}%)")
    
    def run_level_test(self, level: int, adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """運行指定層級的測試"""
        if level not in self.available_levels:
            raise ValueError(f"無效的測試層級: {level}")
        
        framework_info = self.implemented_frameworks[level]
        
        print(f"🚀 開始運行Level {level}測試...")
        print(f"📋 {self.level_descriptions[level]}")
        print(f"📊 狀態: {framework_info['status']}")
        
        if framework_info["module"] is None:
            print(f"⚠️  Level {level}測試框架尚未實現")
            return {
                "level": level,
                "status": "not_implemented",
                "message": f"Level {level}測試框架尚未實現",
                "score": 0.0,
                "execution_time": 0.0
            }
        
        try:
            start_time = time.time()
            
            # 動態導入和實例化測試框架
            framework = self._import_framework(level, framework_info)
            
            if framework is None:
                return {
                    "level": level,
                    "status": "import_failed",
                    "message": f"Level {level}測試框架導入失敗",
                    "score": 0.0,
                    "execution_time": 0.0
                }
            
            # 運行測試
            print(f"⚡ 執行測試中...")
            results = framework.run_tests(adapter_name=adapter_name)
            
            execution_time = time.time() - start_time
            
            if results and len(results) > 0:
                result = results[0]
                print(f"✅ Level {level}測試完成!")
                print(f"📊 狀態: {result.status.value}")
                print(f"🎯 分數: {result.score:.1f}/100")
                print(f"⏱️  執行時間: {execution_time:.2f}秒")
                
                return {
                    "level": level,
                    "status": result.status.value,
                    "score": result.score,
                    "execution_time": execution_time,
                    "message": result.message,
                    "details": result.details
                }
            else:
                return {
                    "level": level,
                    "status": "no_results",
                    "message": "測試未返回結果",
                    "score": 0.0,
                    "execution_time": execution_time
                }
                
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0.0
            error_msg = f"Level {level}測試執行失敗: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            print(f"❌ {error_msg}")
            
            return {
                "level": level,
                "status": "error",
                "message": error_msg,
                "score": 0.0,
                "execution_time": execution_time,
                "error": str(e)
            }
    
    def _import_framework(self, level: int, framework_info: Dict[str, Any]):
        """動態導入測試框架"""
        try:
            module_name = framework_info["module"]
            class_name = framework_info["class"]
            
            # 動態導入模組
            module = __import__(module_name, fromlist=[class_name])
            framework_class = getattr(module, class_name)
            
            # 實例化框架
            framework = framework_class()
            
            return framework
            
        except ImportError as e:
            logger.error(f"導入Level {level}測試框架失敗: {e}")
            return None
        except AttributeError as e:
            logger.error(f"Level {level}測試框架類不存在: {e}")
            return None
        except Exception as e:
            logger.error(f"Level {level}測試框架實例化失敗: {e}")
            return None
    
    def run_multiple_levels(self, levels: List[int], adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """運行多個層級的測試"""
        print(f"🎯 開始運行多層級測試: {levels}")
        print("=" * 60)
        
        all_results = {}
        total_score = 0.0
        total_time = 0.0
        success_count = 0
        
        for i, level in enumerate(levels, 1):
            print(f"\n📍 進度: {i}/{len(levels)} - Level {level}")
            print("-" * 40)
            
            result = self.run_level_test(level, adapter_name)
            all_results[f"level_{level}"] = result
            
            if result["status"] in ["passed", "failed"]:
                total_score += result["score"]
                success_count += 1
            
            total_time += result["execution_time"]
            
            print("-" * 40)
        
        # 計算總體統計
        avg_score = total_score / success_count if success_count > 0 else 0.0
        
        summary = {
            "total_levels": len(levels),
            "successful_levels": success_count,
            "failed_levels": len(levels) - success_count,
            "average_score": avg_score,
            "total_execution_time": total_time,
            "results": all_results
        }
        
        print("\n" + "=" * 60)
        print("📊 多層級測試總結")
        print("=" * 60)
        print(f"🎯 測試層級: {len(levels)}個")
        print(f"✅ 成功執行: {success_count}個")
        print(f"❌ 執行失敗: {len(levels) - success_count}個")
        print(f"📊 平均分數: {avg_score:.1f}/100")
        print(f"⏱️  總執行時間: {total_time:.2f}秒")
        
        return summary
    
    def run_all_implemented(self, adapter_name: Optional[str] = None) -> Dict[str, Any]:
        """運行所有已實現的測試層級"""
        implemented_levels = [
            level for level, info in self.implemented_frameworks.items()
            if info["status"] == "✅ 已實現"
        ]
        
        print(f"🚀 運行所有已實現的測試層級: {implemented_levels}")
        return self.run_multiple_levels(implemented_levels, adapter_name)
    
    def generate_comprehensive_report(self, results: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """生成綜合測試報告"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"comprehensive_test_report_{timestamp}.md"
        
        report_content = f"""# PowerAutomation 十層測試架構綜合報告

## 📊 測試概覽
- **測試時間**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **測試層級數**: {results.get('total_levels', 0)}
- **成功執行**: {results.get('successful_levels', 0)}
- **執行失敗**: {results.get('failed_levels', 0)}
- **平均分數**: {results.get('average_score', 0):.1f}/100
- **總執行時間**: {results.get('total_execution_time', 0):.2f}秒

## 🎯 各層級詳細結果

"""
        
        if "results" in results:
            for level_key, level_result in results["results"].items():
                level_num = level_key.split("_")[1]
                description = self.level_descriptions.get(int(level_num), "未知層級")
                
                status_emoji = {
                    "passed": "✅",
                    "failed": "❌", 
                    "error": "💥",
                    "not_implemented": "⏳",
                    "import_failed": "🚫"
                }.get(level_result["status"], "❓")
                
                report_content += f"""### Level {level_num}: {description}
- **狀態**: {status_emoji} {level_result["status"]}
- **分數**: {level_result["score"]:.1f}/100
- **執行時間**: {level_result["execution_time"]:.2f}秒
- **消息**: {level_result.get("message", "無")}

"""
        
        report_content += f"""## 📈 測試架構完成度

| 層級 | 描述 | 狀態 | 分數 |
|------|------|------|------|
"""
        
        for level in self.available_levels:
            description = self.level_descriptions[level]
            status = self.implemented_frameworks[level]["status"]
            
            if "results" in results and f"level_{level}" in results["results"]:
                score = results["results"][f"level_{level}"]["score"]
                score_str = f"{score:.1f}/100"
            else:
                score_str = "未測試"
            
            report_content += f"| {level} | {description} | {status} | {score_str} |\n"
        
        report_content += f"""
## 🎯 總結

PowerAutomation十層測試架構展現了{"優秀" if results.get("average_score", 0) >= 85 else "良好" if results.get("average_score", 0) >= 75 else "可接受" if results.get("average_score", 0) >= 65 else "需要改進"}的整體表現。

### 🏆 優勢
- 完整的測試覆蓋範圍
- 標準化的測試接口
- 自動化的測試執行
- 詳細的測試報告

### 💡 改進建議
- 繼續完善未實現的測試層級
- 優化測試執行效率
- 增強錯誤處理機制
- 提升測試覆蓋率

---
*報告生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        # 寫入報告文件
        report_path = Path(output_file)
        report_path.write_text(report_content, encoding='utf-8')
        
        print(f"📄 綜合報告已生成: {report_path.absolute()}")
        return str(report_path.absolute())

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation 十層測試架構CLI v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --list                    # 列出所有測試層級
  %(prog)s --level 3                 # 運行Level 3測試
  %(prog)s --level 1 2 3             # 運行Level 1,2,3測試
  %(prog)s --all                     # 運行所有已實現的測試
  %(prog)s --level 3 --adapter claude # 測試特定適配器
  %(prog)s --all --report report.md  # 生成綜合報告
        """
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有可用的測試層級"
    )
    
    parser.add_argument(
        "--level",
        type=int,
        nargs="+",
        help="指定要運行的測試層級 (1-10)"
    )
    
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="運行所有已實現的測試層級"
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
        help="顯示詳細輸出"
    )
    
    args = parser.parse_args()
    
    # 配置日誌級別
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    cli = TenLayerTestCLI()
    
    try:
        if args.list:
            cli.list_available_levels()
            return
        
        results = None
        
        if args.all:
            results = cli.run_all_implemented(args.adapter)
        elif args.level:
            if len(args.level) == 1:
                result = cli.run_level_test(args.level[0], args.adapter)
                results = {
                    "total_levels": 1,
                    "successful_levels": 1 if result["status"] in ["passed", "failed"] else 0,
                    "failed_levels": 0 if result["status"] in ["passed", "failed"] else 1,
                    "average_score": result["score"],
                    "total_execution_time": result["execution_time"],
                    "results": {f"level_{args.level[0]}": result}
                }
            else:
                results = cli.run_multiple_levels(args.level, args.adapter)
        else:
            parser.print_help()
            return
        
        # 生成報告
        if results and args.report:
            cli.generate_comprehensive_report(results, args.report)
        elif results:
            # 默認生成報告
            cli.generate_comprehensive_report(results)
            
    except KeyboardInterrupt:
        print("\n⚠️  測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"❌ CLI執行失敗: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

