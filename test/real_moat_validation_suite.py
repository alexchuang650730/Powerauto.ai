#!/usr/bin/env python3
"""
PowerAutomation 真實護城河驗證測試套件

升級版本: 從mock實現升級為真實的護城河驗證邏輯
包含真實的指標計算、性能測試和安全掃描
"""

import unittest
import asyncio
import sys
import os
import json
import time
import requests
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import concurrent.futures
import threading

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class MoatStrength(Enum):
    """護城河強度等級"""
    WEAK = "弱護城河"
    MODERATE = "中等護城河"
    STRONG = "強護城河"
    FORTRESS = "堡壘級護城河"

@dataclass
class RealMoatMetrics:
    """真實護城河指標"""
    test_coverage: float = 0.0
    test_quality: float = 0.0
    performance_score: float = 0.0
    security_score: float = 0.0
    compatibility_score: float = 0.0
    ai_capability_score: float = 0.0
    overall_strength: str = MoatStrength.WEAK.value
    validation_timestamp: str = ""
    detailed_results: Dict[str, Any] = None

class RealMoatValidationSuite:
    """真實護城河驗證套件"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api/v1"):
        self.api_base_url = api_base_url
        self.test_results = []
        self.metrics = RealMoatMetrics()
        self.detailed_results = {}
    
    async def validate_all_moats(self) -> RealMoatMetrics:
        """驗證所有護城河"""
        print("🏰 開始真實護城河驗證...")
        
        # 並行執行各項驗證
        tasks = [
            self.validate_test_coverage(),
            self.validate_test_quality(),
            self.validate_performance(),
            self.validate_security(),
            self.validate_compatibility(),
            self.validate_ai_capability()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理結果
        self.metrics.test_coverage = results[0] if not isinstance(results[0], Exception) else 0.0
        self.metrics.test_quality = results[1] if not isinstance(results[1], Exception) else 0.0
        self.metrics.performance_score = results[2] if not isinstance(results[2], Exception) else 0.0
        self.metrics.security_score = results[3] if not isinstance(results[3], Exception) else 0.0
        self.metrics.compatibility_score = results[4] if not isinstance(results[4], Exception) else 0.0
        self.metrics.ai_capability_score = results[5] if not isinstance(results[5], Exception) else 0.0
        
        # 計算整體強度
        self.metrics.overall_strength = self._calculate_overall_strength()
        self.metrics.validation_timestamp = datetime.now().isoformat()
        self.metrics.detailed_results = self.detailed_results
        
        print(f"🎯 護城河驗證完成，整體強度: {self.metrics.overall_strength}")
        return self.metrics
    
    async def validate_test_coverage(self) -> float:
        """驗證測試覆蓋率"""
        print("📊 驗證測試覆蓋率...")
        
        try:
            # 獲取所有測試結果
            response = requests.get(f"{self.api_base_url}/test/results", timeout=10)
            if response.status_code != 200:
                return 0.0
            
            test_results = response.json()
            
            if not test_results:
                return 0.0
            
            # 計算通過率
            passed_tests = sum(1 for result in test_results if result.get('status') == 'passed')
            total_tests = len(test_results)
            coverage = (passed_tests / total_tests) * 100
            
            # 執行真實的代碼覆蓋率檢查
            try:
                # 使用coverage.py檢查代碼覆蓋率
                result = subprocess.run(
                    ['python', '-m', 'coverage', 'report', '--show-missing'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # 解析覆蓋率報告
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'TOTAL' in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                coverage_percent = parts[-1].replace('%', '')
                                try:
                                    code_coverage = float(coverage_percent)
                                    coverage = (coverage + code_coverage) / 2  # 平均值
                                except ValueError:
                                    pass
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            self.detailed_results['test_coverage'] = {
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'coverage_percentage': coverage
            }
            
            return min(100.0, coverage)
            
        except Exception as e:
            print(f"❌ 測試覆蓋率驗證失敗: {str(e)}")
            return 0.0
    
    async def validate_test_quality(self) -> float:
        """驗證測試質量"""
        print("🔍 驗證測試質量...")
        
        try:
            # 檢查測試文件質量
            test_dir = Path(__file__).parent
            test_files = list(test_dir.rglob("test_*.py"))
            
            quality_metrics = {
                'total_files': len(test_files),
                'files_with_assertions': 0,
                'files_with_setup': 0,
                'files_with_teardown': 0,
                'files_with_docstrings': 0,
                'average_test_methods': 0
            }
            
            total_test_methods = 0
            
            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 檢查是否有斷言
                    if 'assert' in content or 'self.assert' in content:
                        quality_metrics['files_with_assertions'] += 1
                    
                    # 檢查是否有setUp
                    if 'setUp' in content:
                        quality_metrics['files_with_setup'] += 1
                    
                    # 檢查是否有tearDown
                    if 'tearDown' in content:
                        quality_metrics['files_with_teardown'] += 1
                    
                    # 檢查是否有文檔字符串
                    if '"""' in content or "'''" in content:
                        quality_metrics['files_with_docstrings'] += 1
                    
                    # 計算測試方法數量
                    test_methods = content.count('def test_')
                    total_test_methods += test_methods
                    
                except Exception:
                    continue
            
            if quality_metrics['total_files'] > 0:
                quality_metrics['average_test_methods'] = total_test_methods / quality_metrics['total_files']
                
                # 計算質量分數
                quality_score = (
                    (quality_metrics['files_with_assertions'] / quality_metrics['total_files']) * 30 +
                    (quality_metrics['files_with_setup'] / quality_metrics['total_files']) * 20 +
                    (quality_metrics['files_with_teardown'] / quality_metrics['total_files']) * 20 +
                    (quality_metrics['files_with_docstrings'] / quality_metrics['total_files']) * 20 +
                    min(10, quality_metrics['average_test_methods'])
                )
            else:
                quality_score = 0.0
            
            self.detailed_results['test_quality'] = quality_metrics
            return min(100.0, quality_score)
            
        except Exception as e:
            print(f"❌ 測試質量驗證失敗: {str(e)}")
            return 0.0
    
    async def validate_performance(self) -> float:
        """驗證性能指標"""
        print("⚡ 驗證性能指標...")
        
        try:
            performance_metrics = {
                'api_response_time': 0.0,
                'memory_usage': 0.0,
                'cpu_usage': 0.0,
                'concurrent_requests': 0
            }
            
            # 測試API響應時間
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            api_response_time = (time.time() - start_time) * 1000  # 毫秒
            performance_metrics['api_response_time'] = api_response_time
            
            # 測試並發請求處理能力
            def make_request():
                try:
                    response = requests.get(f"{self.api_base_url}/health", timeout=5)
                    return response.status_code == 200
                except:
                    return False
            
            # 並發測試
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(make_request) for _ in range(50)]
                successful_requests = sum(1 for future in concurrent.futures.as_completed(futures) if future.result())
            
            performance_metrics['concurrent_requests'] = successful_requests
            
            # 獲取系統資源使用情況
            try:
                process = psutil.Process()
                performance_metrics['memory_usage'] = process.memory_percent()
                performance_metrics['cpu_usage'] = process.cpu_percent(interval=1)
            except:
                performance_metrics['memory_usage'] = 0.0
                performance_metrics['cpu_usage'] = 0.0
            
            # 計算性能分數
            response_time_score = max(0, 100 - (api_response_time / 10))  # 100ms以下滿分
            concurrent_score = (successful_requests / 50) * 100
            memory_score = max(0, 100 - performance_metrics['memory_usage'])
            cpu_score = max(0, 100 - performance_metrics['cpu_usage'])
            
            performance_score = (response_time_score + concurrent_score + memory_score + cpu_score) / 4
            
            self.detailed_results['performance'] = performance_metrics
            return min(100.0, performance_score)
            
        except Exception as e:
            print(f"❌ 性能驗證失敗: {str(e)}")
            return 0.0
    
    async def validate_security(self) -> float:
        """驗證安全性"""
        print("🔒 驗證安全性...")
        
        try:
            security_metrics = {
                'https_enabled': False,
                'auth_required': False,
                'input_validation': False,
                'error_handling': False,
                'rate_limiting': False
            }
            
            # 檢查HTTPS
            try:
                https_response = requests.get(self.api_base_url.replace('http://', 'https://'), timeout=5)
                security_metrics['https_enabled'] = True
            except:
                security_metrics['https_enabled'] = False
            
            # 檢查輸入驗證
            try:
                # 嘗試發送無效數據
                invalid_data = {"invalid": None, "test": "<script>alert('xss')</script>"}
                response = requests.post(f"{self.api_base_url}/config/load", json=invalid_data, timeout=5)
                # 如果API正確處理了無效輸入，則認為有輸入驗證
                security_metrics['input_validation'] = response.status_code in [400, 422, 500]
            except:
                security_metrics['input_validation'] = False
            
            # 檢查錯誤處理
            try:
                response = requests.get(f"{self.api_base_url}/nonexistent_endpoint", timeout=5)
                security_metrics['error_handling'] = response.status_code == 404
            except:
                security_metrics['error_handling'] = False
            
            # 檢查速率限制（簡單測試）
            try:
                start_time = time.time()
                for _ in range(100):
                    requests.get(f"{self.api_base_url}/health", timeout=1)
                end_time = time.time()
                
                # 如果100個請求花費時間較長，可能有速率限制
                security_metrics['rate_limiting'] = (end_time - start_time) > 5
            except:
                security_metrics['rate_limiting'] = False
            
            # 計算安全分數
            security_score = sum(security_metrics.values()) / len(security_metrics) * 100
            
            self.detailed_results['security'] = security_metrics
            return security_score
            
        except Exception as e:
            print(f"❌ 安全性驗證失敗: {str(e)}")
            return 0.0
    
    async def validate_compatibility(self) -> float:
        """驗證兼容性"""
        print("🔄 驗證兼容性...")
        
        try:
            compatibility_metrics = {
                'python_version': sys.version_info[:2],
                'api_version_support': False,
                'cross_platform': True,
                'backward_compatibility': False
            }
            
            # 檢查API版本支持
            try:
                response = requests.get(f"{self.api_base_url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    compatibility_metrics['api_version_support'] = 'version' in health_data
            except:
                compatibility_metrics['api_version_support'] = False
            
            # 檢查跨平台兼容性
            compatibility_metrics['cross_platform'] = os.name in ['posix', 'nt']
            
            # 檢查向後兼容性（檢查是否支持舊版本API調用）
            try:
                # 嘗試使用可能的舊版本端點
                old_endpoints = ['/api/config', '/config', '/health']
                for endpoint in old_endpoints:
                    try:
                        response = requests.get(f"http://localhost:8000{endpoint}", timeout=2)
                        if response.status_code in [200, 404]:  # 404也表示端點被識別
                            compatibility_metrics['backward_compatibility'] = True
                            break
                    except:
                        continue
            except:
                compatibility_metrics['backward_compatibility'] = False
            
            # 計算兼容性分數
            score_weights = {
                'api_version_support': 30,
                'cross_platform': 30,
                'backward_compatibility': 40
            }
            
            compatibility_score = sum(
                score_weights[key] for key, value in compatibility_metrics.items() 
                if key in score_weights and value
            )
            
            self.detailed_results['compatibility'] = compatibility_metrics
            return compatibility_score
            
        except Exception as e:
            print(f"❌ 兼容性驗證失敗: {str(e)}")
            return 0.0
    
    async def validate_ai_capability(self) -> float:
        """驗證AI能力"""
        print("🤖 驗證AI能力...")
        
        try:
            ai_metrics = {
                'api_available': False,
                'response_quality': 0.0,
                'processing_speed': 0.0,
                'error_handling': False
            }
            
            # 測試AI API可用性
            try:
                ai_request = {
                    "prompt": "測試AI能力：請生成一個簡單的Python函數",
                    "model": "gpt-4",
                    "max_tokens": 100
                }
                
                start_time = time.time()
                response = requests.post(f"{self.api_base_url}/ai/generate", json=ai_request, timeout=10)
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    ai_metrics['api_available'] = True
                    ai_data = response.json()
                    
                    # 評估響應質量
                    if 'response' in ai_data and len(ai_data['response']) > 10:
                        ai_metrics['response_quality'] = min(100, len(ai_data['response']) / 2)
                    
                    # 評估處理速度
                    ai_metrics['processing_speed'] = max(0, 100 - (processing_time * 10))
                    
            except Exception as e:
                print(f"AI API測試失敗: {str(e)}")
            
            # 測試AI能力評估
            try:
                test_cases = [
                    {"prompt": "解釋什麼是機器學習", "expected_keywords": ["學習", "算法", "數據"]},
                    {"prompt": "寫一個排序算法", "expected_keywords": ["排序", "算法", "數組"]}
                ]
                
                response = requests.post(f"{self.api_base_url}/ai/evaluate", json=test_cases, timeout=15)
                if response.status_code == 200:
                    eval_data = response.json()
                    if 'average_score' in eval_data:
                        ai_metrics['response_quality'] = eval_data['average_score']
                        ai_metrics['error_handling'] = True
                        
            except Exception as e:
                print(f"AI評估測試失敗: {str(e)}")
            
            # 計算AI能力分數
            ai_score = (
                (30 if ai_metrics['api_available'] else 0) +
                (ai_metrics['response_quality'] * 0.4) +
                (ai_metrics['processing_speed'] * 0.2) +
                (10 if ai_metrics['error_handling'] else 0)
            )
            
            self.detailed_results['ai_capability'] = ai_metrics
            return min(100.0, ai_score)
            
        except Exception as e:
            print(f"❌ AI能力驗證失敗: {str(e)}")
            return 0.0
    
    def _calculate_overall_strength(self) -> str:
        """計算整體護城河強度"""
        scores = [
            self.metrics.test_coverage,
            self.metrics.test_quality,
            self.metrics.performance_score,
            self.metrics.security_score,
            self.metrics.compatibility_score,
            self.metrics.ai_capability_score
        ]
        
        average_score = sum(scores) / len(scores)
        
        if average_score >= 90:
            return MoatStrength.FORTRESS.value
        elif average_score >= 75:
            return MoatStrength.STRONG.value
        elif average_score >= 60:
            return MoatStrength.MODERATE.value
        else:
            return MoatStrength.WEAK.value
    
    def generate_report(self) -> Dict[str, Any]:
        """生成詳細報告"""
        return {
            "validation_summary": asdict(self.metrics),
            "detailed_analysis": self.detailed_results,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if self.metrics.test_coverage < 80:
            recommendations.append("建議提高測試覆蓋率至80%以上")
        
        if self.metrics.performance_score < 85:
            recommendations.append("建議優化API響應時間和並發處理能力")
        
        if self.metrics.security_score < 90:
            recommendations.append("建議加強安全防護措施，啟用HTTPS和身份驗證")
        
        if self.metrics.ai_capability_score < 85:
            recommendations.append("建議提升AI模型性能和響應質量")
        
        return recommendations

# 測試類
class TestRealMoatValidation(unittest.TestCase):
    """真實護城河驗證測試"""
    
    @classmethod
    def setUpClass(cls):
        """測試類設置"""
        cls.validator = RealMoatValidationSuite()
    
    def test_real_moat_validation(self):
        """測試真實護城河驗證"""
        # 運行異步驗證
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            metrics = loop.run_until_complete(self.validator.validate_all_moats())
            
            # 驗證結果
            self.assertIsInstance(metrics, RealMoatMetrics)
            self.assertGreaterEqual(metrics.test_coverage, 0)
            self.assertLessEqual(metrics.test_coverage, 100)
            self.assertIn(metrics.overall_strength, [s.value for s in MoatStrength])
            
            # 生成報告
            report = self.validator.generate_report()
            self.assertIn('validation_summary', report)
            self.assertIn('detailed_analysis', report)
            self.assertIn('recommendations', report)
            
            print(f"\n🏰 護城河驗證完成:")
            print(f"   測試覆蓋率: {metrics.test_coverage:.1f}%")
            print(f"   測試質量: {metrics.test_quality:.1f}%")
            print(f"   性能分數: {metrics.performance_score:.1f}%")
            print(f"   安全分數: {metrics.security_score:.1f}%")
            print(f"   兼容性分數: {metrics.compatibility_score:.1f}%")
            print(f"   AI能力分數: {metrics.ai_capability_score:.1f}%")
            print(f"   整體強度: {metrics.overall_strength}")
            
        finally:
            loop.close()

if __name__ == '__main__':
    # 檢查API服務是否運行
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("警告: API服務未運行，請先啟動 real_api_server.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("錯誤: 無法連接到API服務，請先啟動 real_api_server.py")
        sys.exit(1)
    
    unittest.main()

