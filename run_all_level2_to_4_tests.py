#!/usr/bin/env python3
"""
PowerAutomation Level 2-4 統一測試運行器

批量運行Level 2-4所有測試，生成詳細報告
"""

import unittest
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class Level2to4TestRunner:
    """Level 2-4 統一測試運行器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        
    def run_level_tests(self, level: str) -> Dict[str, Tuple[int, int, int]]:
        """運行指定層級的測試"""
        level_dir = self.test_dir / level
        if not level_dir.exists():
            return {}
        
        level_results = {}
        
        for category_dir in level_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                category = category_dir.name
                
                suite = unittest.TestSuite()
                loader = unittest.TestLoader()
                
                # 加載該類別下的所有測試
                for test_file in category_dir.glob('test_*.py'):
                    module_name = f"test.{level}.{category}.{test_file.stem}"
                    try:
                        module = __import__(module_name, fromlist=[''])
                        suite.addTests(loader.loadTestsFromModule(module))
                    except ImportError as e:
                        print(f"⚠️ 無法加載測試模塊 {module_name}: {e}")
                
                # 運行測試
                runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
                result = runner.run(suite)
                
                level_results[category] = (result.testsRun, len(result.failures), len(result.errors))
        
        return level_results
    
    def run_all_tests(self) -> Dict[str, any]:
        """運行所有Level 2-4測試"""
        print("🚀 開始運行Level 2-4測試...")
        
        levels = ['level2', 'level3', 'level4']
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for level in levels:
            print(f"\n📋 運行 {level.upper()} 測試...")
            level_results = self.run_level_tests(level)
            self.results[level] = level_results
            
            level_tests = sum(r[0] for r in level_results.values())
            level_failures = sum(r[1] for r in level_results.values())
            level_errors = sum(r[2] for r in level_results.values())
            
            total_tests += level_tests
            total_failures += level_failures
            total_errors += level_errors
            
            if level_tests > 0:
                success_rate = ((level_tests - level_failures - level_errors) / level_tests) * 100
                print(f"  ✅ {level.upper()}: {level_tests}個測試, 成功率 {success_rate:.1f}%")
            else:
                print(f"  ⚠️ {level.upper()}: 無測試文件")
        
        return {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'levels': self.results
        }
    
    def generate_report(self, results: Dict) -> str:
        """生成測試報告"""
        report = []
        report.append("# PowerAutomation Level 2-4 測試報告")
        report.append("=" * 50)
        report.append("")
        
        # 總體統計
        total_tests = results['total_tests']
        total_failures = results['total_failures']
        total_errors = results['total_errors']
        success_count = total_tests - total_failures - total_errors
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        
        report.append(f"## 總體統計")
        report.append(f"- 總測試數: {total_tests}")
        report.append(f"- 成功測試: {success_count}")
        report.append(f"- 失敗測試: {total_failures}")
        report.append(f"- 錯誤測試: {total_errors}")
        report.append(f"- 成功率: {success_rate:.2f}%")
        report.append("")
        
        # 層級統計
        for level, level_results in results['levels'].items():
            level_tests = sum(r[0] for r in level_results.values())
            level_failures = sum(r[1] for r in level_results.values())
            level_errors = sum(r[2] for r in level_results.values())
            
            if level_tests > 0:
                level_success_rate = ((level_tests - level_failures - level_errors) / level_tests) * 100
                report.append(f"## {level.upper()} 統計")
                report.append(f"- 測試數: {level_tests}")
                report.append(f"- 成功率: {level_success_rate:.1f}%")
                
                for category, (tests, failures, errors) in level_results.items():
                    if tests > 0:
                        cat_success_rate = ((tests - failures - errors) / tests) * 100
                        report.append(f"  - {category}: {tests}個測試, 成功率 {cat_success_rate:.1f}%")
                
                report.append("")
        
        return "\n".join(report)

def main():
    """主函數"""
    runner = Level2to4TestRunner()
    results = runner.run_all_tests()
    
    # 生成報告
    report = runner.generate_report(results)
    
    # 保存報告
    report_path = Path(__file__).parent / "level2_to_4_test_report.md"
    report_path.write_text(report, encoding='utf-8')
    
    print("\n" + "="*50)
    print("🎉 Level 2-4 測試完成!")
    print("="*50)
    print(f"📊 總測試數: {results['total_tests']}")
    print(f"✅ 成功率: {((results['total_tests'] - results['total_failures'] - results['total_errors']) / results['total_tests'] * 100):.1f}%" if results['total_tests'] > 0 else "N/A")
    print(f"📄 詳細報告: {report_path}")
    print("="*50)

if __name__ == '__main__':
    main()
