#!/usr/bin/env python3
"""
PowerAutomation v0.53 統一架構整合測試

測試統一架構的整合效果，包括：
1. 功能完整性測試
2. 性能對比測試
3. 數據一致性測試
4. 組件協調測試
"""

import os
import json
import time
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import unittest
from unittest.mock import Mock, patch

# 導入統一架構
from unified_architecture import (
    UnifiedArchitectureCoordinator,
    InteractionSource,
    DeliverableType,
    DataLayer,
    initialize_unified_architecture
)

class UnifiedArchitectureIntegrationTest:
    """統一架構整合測試"""
    
    def __init__(self):
        self.test_results = {
            'functionality_tests': {},
            'performance_tests': {},
            'integration_tests': {},
            'data_consistency_tests': {},
            'overall_score': 0.0
        }
        self.logger = logging.getLogger(__name__)
        
        # 測試配置
        self.test_config = {
            'base_dir': '/home/ubuntu/Powerauto.ai/test_unified',
            'test_data_count': 10,
            'performance_iterations': 5,
            'timeout_seconds': 30
        }
        
        # 初始化測試環境
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """設置測試環境"""
        test_dir = Path(self.test_config['base_dir'])
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # 清理之前的測試數據
        for subdir in ['unified_data', 'test_results']:
            if (test_dir / subdir).exists():
                import shutil
                shutil.rmtree(test_dir / subdir)
        
        self.logger.info(f"✅ 測試環境已設置: {test_dir}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        print("🚀 開始統一架構整合測試")
        
        # 1. 功能完整性測試
        print("\n📋 1. 功能完整性測試")
        functionality_results = await self.test_functionality()
        self.test_results['functionality_tests'] = functionality_results
        
        # 2. 性能對比測試
        print("\n⚡ 2. 性能對比測試")
        performance_results = await self.test_performance()
        self.test_results['performance_tests'] = performance_results
        
        # 3. 整合效果測試
        print("\n🔄 3. 整合效果測試")
        integration_results = await self.test_integration()
        self.test_results['integration_tests'] = integration_results
        
        # 4. 數據一致性測試
        print("\n📊 4. 數據一致性測試")
        consistency_results = await self.test_data_consistency()
        self.test_results['data_consistency_tests'] = consistency_results
        
        # 5. 計算總體評分
        overall_score = self.calculate_overall_score()
        self.test_results['overall_score'] = overall_score
        
        # 6. 生成測試報告
        await self.generate_test_report()
        
        print(f"\n✅ 測試完成，總體評分: {overall_score:.2f}/100")
        return self.test_results
    
    async def test_functionality(self) -> Dict[str, Any]:
        """功能完整性測試"""
        results = {
            'data_collection': {'passed': False, 'score': 0, 'details': ''},
            'data_storage': {'passed': False, 'score': 0, 'details': ''},
            'learning_generation': {'passed': False, 'score': 0, 'details': ''},
            'template_generation': {'passed': False, 'score': 0, 'details': ''},
            'component_coordination': {'passed': False, 'score': 0, 'details': ''}
        }
        
        try:
            # 初始化協調器
            config = {
                'base_dir': self.test_config['base_dir'],
                'collector': {'batch_size': 5, 'log_level': 'INFO'},
                'data_manager': {'local_storage': True}
            }
            coordinator = UnifiedArchitectureCoordinator(config)
            await coordinator.start_processing()
            
            # 測試數據收集
            print("  📥 測試數據收集功能...")
            test_interaction = {
                'user_request': {'text': '測試功能', 'type': 'test'},
                'agent_response': {'text': '測試響應'},
                'deliverables': [{
                    'name': 'test.py',
                    'content': 'def test(): return "hello"',
                    'metadata': {'test': True}
                }],
                'context': {'test_mode': True}
            }
            
            result = await coordinator.process_interaction(
                InteractionSource.SYSTEM_INTERNAL, test_interaction
            )
            
            if result['success']:
                results['data_collection']['passed'] = True
                results['data_collection']['score'] = 20
                results['data_collection']['details'] = '數據收集功能正常'
                print("    ✅ 數據收集測試通過")
            else:
                results['data_collection']['details'] = f"數據收集失敗: {result.get('error', 'Unknown')}"
                print("    ❌ 數據收集測試失敗")
            
            # 測試數據存儲
            print("  💾 測試數據存儲功能...")
            if result['success']:
                storage_path = result['storage_path']
                if os.path.exists(storage_path):
                    results['data_storage']['passed'] = True
                    results['data_storage']['score'] = 20
                    results['data_storage']['details'] = '數據存儲功能正常'
                    print("    ✅ 數據存儲測試通過")
                else:
                    results['data_storage']['details'] = '存儲文件不存在'
                    print("    ❌ 數據存儲測試失敗")
            
            # 測試學習經驗生成
            print("  🧠 測試學習經驗生成...")
            if result['success'] and result['learning_experiences_generated'] > 0:
                results['learning_generation']['passed'] = True
                results['learning_generation']['score'] = 20
                results['learning_generation']['details'] = '學習經驗生成正常'
                print("    ✅ 學習經驗生成測試通過")
            else:
                results['learning_generation']['details'] = '未生成學習經驗'
                print("    ❌ 學習經驗生成測試失敗")
            
            # 測試模板生成（需要高質量交付件）
            print("  🔧 測試模板生成功能...")
            high_quality_interaction = {
                'user_request': {'text': '創建高質量代碼', 'type': 'code_generation'},
                'agent_response': {'text': '創建高質量Python類'},
                'deliverables': [{
                    'name': 'high_quality.py',
                    'content': '''
class HighQualityClass:
    """高質量的Python類示例"""
    
    def __init__(self, name: str):
        self.name = name
    
    def process(self, data: dict) -> dict:
        """處理數據的方法"""
        try:
            result = {"processed": True, "data": data}
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def __str__(self) -> str:
        return f"HighQualityClass({self.name})"
                    ''',
                    'metadata': {'lines': 20, 'functions': 3, 'classes': 1}
                }],
                'context': {'quality_focus': True}
            }
            
            template_result = await coordinator.process_interaction(
                InteractionSource.SYSTEM_INTERNAL, high_quality_interaction
            )
            
            if template_result['success'] and template_result['templates_generated'] > 0:
                results['template_generation']['passed'] = True
                results['template_generation']['score'] = 20
                results['template_generation']['details'] = '模板生成功能正常'
                print("    ✅ 模板生成測試通過")
            else:
                results['template_generation']['details'] = '未生成模板'
                print("    ❌ 模板生成測試失敗")
            
            # 測試組件協調
            print("  🔄 測試組件協調功能...")
            status = await coordinator.get_system_status()
            if (status['coordinator_status']['initialized'] and 
                status['coordinator_status']['processed_interactions'] > 0):
                results['component_coordination']['passed'] = True
                results['component_coordination']['score'] = 20
                results['component_coordination']['details'] = '組件協調功能正常'
                print("    ✅ 組件協調測試通過")
            else:
                results['component_coordination']['details'] = '組件協調異常'
                print("    ❌ 組件協調測試失敗")
            
            await coordinator.stop_processing()
            
        except Exception as e:
            error_msg = f"功能測試異常: {e}"
            print(f"    ❌ {error_msg}")
            for test_name in results:
                if not results[test_name]['passed']:
                    results[test_name]['details'] = error_msg
        
        return results
    
    async def test_performance(self) -> Dict[str, Any]:
        """性能對比測試"""
        results = {
            'processing_speed': {'score': 0, 'details': ''},
            'memory_usage': {'score': 0, 'details': ''},
            'concurrent_processing': {'score': 0, 'details': ''},
            'scalability': {'score': 0, 'details': ''}
        }
        
        try:
            # 初始化協調器
            config = {'base_dir': self.test_config['base_dir']}
            coordinator = UnifiedArchitectureCoordinator(config)
            await coordinator.start_processing()
            
            # 測試處理速度
            print("  ⚡ 測試處理速度...")
            start_time = time.time()
            
            for i in range(self.test_config['performance_iterations']):
                test_interaction = {
                    'user_request': {'text': f'性能測試 {i}', 'type': 'performance_test'},
                    'agent_response': {'text': f'響應 {i}'},
                    'deliverables': [{
                        'name': f'perf_test_{i}.py',
                        'content': f'# Performance test {i}\nprint("test {i}")',
                        'metadata': {'iteration': i}
                    }]
                }
                
                result = await coordinator.process_interaction(
                    InteractionSource.SYSTEM_INTERNAL, test_interaction
                )
                
                if not result['success']:
                    print(f"    ⚠️ 第{i+1}次處理失敗")
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / self.test_config['performance_iterations']
            
            # 評分：平均處理時間 < 1秒得滿分
            if avg_time < 1.0:
                speed_score = 25
            elif avg_time < 2.0:
                speed_score = 20
            elif avg_time < 5.0:
                speed_score = 15
            else:
                speed_score = 10
            
            results['processing_speed']['score'] = speed_score
            results['processing_speed']['details'] = f'平均處理時間: {avg_time:.3f}秒'
            print(f"    ✅ 平均處理時間: {avg_time:.3f}秒 (評分: {speed_score}/25)")
            
            # 測試內存使用（簡化版）
            print("  💾 測試內存使用...")
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            # 評分：內存使用 < 100MB得滿分
            if memory_mb < 100:
                memory_score = 25
            elif memory_mb < 200:
                memory_score = 20
            elif memory_mb < 500:
                memory_score = 15
            else:
                memory_score = 10
            
            results['memory_usage']['score'] = memory_score
            results['memory_usage']['details'] = f'內存使用: {memory_mb:.1f}MB'
            print(f"    ✅ 內存使用: {memory_mb:.1f}MB (評分: {memory_score}/25)")
            
            # 測試並發處理（簡化版）
            print("  🔄 測試並發處理...")
            concurrent_start = time.time()
            
            # 創建並發任務
            tasks = []
            for i in range(3):  # 3個並發任務
                task_interaction = {
                    'user_request': {'text': f'並發測試 {i}', 'type': 'concurrent_test'},
                    'agent_response': {'text': f'並發響應 {i}'},
                    'deliverables': [{
                        'name': f'concurrent_{i}.py',
                        'content': f'# Concurrent test {i}',
                        'metadata': {'concurrent': True}
                    }]
                }
                
                task = coordinator.process_interaction(
                    InteractionSource.SYSTEM_INTERNAL, task_interaction
                )
                tasks.append(task)
            
            # 等待所有任務完成
            concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
            concurrent_end = time.time()
            concurrent_time = concurrent_end - concurrent_start
            
            successful_tasks = sum(1 for r in concurrent_results 
                                 if isinstance(r, dict) and r.get('success', False))
            
            # 評分：成功率和時間
            if successful_tasks == 3 and concurrent_time < 3.0:
                concurrent_score = 25
            elif successful_tasks >= 2 and concurrent_time < 5.0:
                concurrent_score = 20
            elif successful_tasks >= 1:
                concurrent_score = 15
            else:
                concurrent_score = 10
            
            results['concurrent_processing']['score'] = concurrent_score
            results['concurrent_processing']['details'] = f'並發成功率: {successful_tasks}/3, 時間: {concurrent_time:.3f}秒'
            print(f"    ✅ 並發處理: {successful_tasks}/3成功, {concurrent_time:.3f}秒 (評分: {concurrent_score}/25)")
            
            # 測試可擴展性（數據量測試）
            print("  📈 測試可擴展性...")
            scalability_start = time.time()
            
            # 處理大量小任務
            for i in range(20):
                simple_interaction = {
                    'user_request': {'text': f'簡單任務 {i}'},
                    'agent_response': {'text': f'簡單響應 {i}'},
                    'context': {'batch_test': True}
                }
                
                await coordinator.process_interaction(
                    InteractionSource.SYSTEM_INTERNAL, simple_interaction
                )
            
            scalability_end = time.time()
            scalability_time = scalability_end - scalability_start
            
            # 評分：處理20個任務的時間
            if scalability_time < 10.0:
                scalability_score = 25
            elif scalability_time < 20.0:
                scalability_score = 20
            elif scalability_time < 30.0:
                scalability_score = 15
            else:
                scalability_score = 10
            
            results['scalability']['score'] = scalability_score
            results['scalability']['details'] = f'處理20個任務時間: {scalability_time:.3f}秒'
            print(f"    ✅ 可擴展性: 20個任務 {scalability_time:.3f}秒 (評分: {scalability_score}/25)")
            
            await coordinator.stop_processing()
            
        except Exception as e:
            error_msg = f"性能測試異常: {e}"
            print(f"    ❌ {error_msg}")
            for test_name in results:
                results[test_name]['details'] = error_msg
        
        return results
    
    async def test_integration(self) -> Dict[str, Any]:
        """整合效果測試"""
        results = {
            'component_communication': {'score': 0, 'details': ''},
            'data_flow_integrity': {'score': 0, 'details': ''},
            'error_handling': {'score': 0, 'details': ''},
            'configuration_management': {'score': 0, 'details': ''}
        }
        
        try:
            # 測試組件間通信
            print("  📡 測試組件間通信...")
            coordinator = UnifiedArchitectureCoordinator({'base_dir': self.test_config['base_dir']})
            await coordinator.start_processing()
            
            # 測試收集器和數據管理器的通信
            collector_stats = await coordinator.interaction_collector.get_statistics()
            data_manager_config = coordinator.data_manager.storage_config
            
            if collector_stats and data_manager_config:
                results['component_communication']['score'] = 25
                results['component_communication']['details'] = '組件間通信正常'
                print("    ✅ 組件間通信測試通過")
            else:
                results['component_communication']['details'] = '組件間通信異常'
                print("    ❌ 組件間通信測試失敗")
            
            # 測試數據流完整性
            print("  🔄 測試數據流完整性...")
            test_interaction = {
                'user_request': {'text': '數據流測試', 'type': 'data_flow_test'},
                'agent_response': {'text': '數據流響應'},
                'deliverables': [{
                    'name': 'data_flow_test.py',
                    'content': 'def data_flow_test(): pass',
                    'metadata': {'test_type': 'data_flow'}
                }]
            }
            
            result = await coordinator.process_interaction(
                InteractionSource.SYSTEM_INTERNAL, test_interaction
            )
            
            if result['success']:
                # 檢查數據是否正確存儲
                log_id = result['interaction_log_id']
                retrieved_data = await coordinator.data_manager.retrieve_data(
                    log_id, DataLayer.INTERACTION
                )
                
                if retrieved_data and retrieved_data['log_id'] == log_id:
                    results['data_flow_integrity']['score'] = 25
                    results['data_flow_integrity']['details'] = '數據流完整性正常'
                    print("    ✅ 數據流完整性測試通過")
                else:
                    results['data_flow_integrity']['details'] = '數據檢索失敗'
                    print("    ❌ 數據流完整性測試失敗")
            else:
                results['data_flow_integrity']['details'] = '數據處理失敗'
                print("    ❌ 數據流完整性測試失敗")
            
            # 測試錯誤處理
            print("  ⚠️ 測試錯誤處理...")
            try:
                # 故意觸發錯誤
                invalid_interaction = {
                    'user_request': None,  # 無效數據
                    'agent_response': {'text': '錯誤測試'},
                    'deliverables': 'invalid_format'  # 錯誤格式
                }
                
                error_result = await coordinator.process_interaction(
                    InteractionSource.SYSTEM_INTERNAL, invalid_interaction
                )
                
                # 檢查是否正確處理錯誤
                if not error_result['success'] and 'error' in error_result:
                    results['error_handling']['score'] = 25
                    results['error_handling']['details'] = '錯誤處理機制正常'
                    print("    ✅ 錯誤處理測試通過")
                else:
                    results['error_handling']['details'] = '錯誤處理機制異常'
                    print("    ❌ 錯誤處理測試失敗")
                    
            except Exception as e:
                # 如果拋出異常，檢查是否是預期的
                results['error_handling']['score'] = 20  # 部分分數
                results['error_handling']['details'] = f'錯誤處理: {str(e)[:100]}'
                print("    ⚠️ 錯誤處理測試部分通過")
            
            # 測試配置管理
            print("  ⚙️ 測試配置管理...")
            system_status = await coordinator.get_system_status()
            
            if (system_status and 
                'coordinator_status' in system_status and
                'collector_statistics' in system_status and
                'data_manager_config' in system_status):
                results['configuration_management']['score'] = 25
                results['configuration_management']['details'] = '配置管理正常'
                print("    ✅ 配置管理測試通過")
            else:
                results['configuration_management']['details'] = '配置管理異常'
                print("    ❌ 配置管理測試失敗")
            
            await coordinator.stop_processing()
            
        except Exception as e:
            error_msg = f"整合測試異常: {e}"
            print(f"    ❌ {error_msg}")
            for test_name in results:
                if results[test_name]['score'] == 0:
                    results[test_name]['details'] = error_msg
        
        return results
    
    async def test_data_consistency(self) -> Dict[str, Any]:
        """數據一致性測試"""
        results = {
            'data_format_consistency': {'score': 0, 'details': ''},
            'storage_integrity': {'score': 0, 'details': ''},
            'retrieval_accuracy': {'score': 0, 'details': ''},
            'cross_component_consistency': {'score': 0, 'details': ''}
        }
        
        try:
            coordinator = UnifiedArchitectureCoordinator({'base_dir': self.test_config['base_dir']})
            await coordinator.start_processing()
            
            # 測試數據格式一致性
            print("  📋 測試數據格式一致性...")
            test_interactions = []
            
            for i in range(3):
                interaction = {
                    'user_request': {'text': f'一致性測試 {i}', 'type': 'consistency_test'},
                    'agent_response': {'text': f'一致性響應 {i}'},
                    'deliverables': [{
                        'name': f'consistency_{i}.py',
                        'content': f'# Consistency test {i}',
                        'metadata': {'test_id': i}
                    }]
                }
                
                result = await coordinator.process_interaction(
                    InteractionSource.SYSTEM_INTERNAL, interaction
                )
                
                if result['success']:
                    test_interactions.append(result['interaction_log_id'])
            
            if len(test_interactions) == 3:
                results['data_format_consistency']['score'] = 25
                results['data_format_consistency']['details'] = '數據格式一致性正常'
                print("    ✅ 數據格式一致性測試通過")
            else:
                results['data_format_consistency']['details'] = f'只有{len(test_interactions)}/3個交互成功'
                print("    ❌ 數據格式一致性測試失敗")
            
            # 測試存儲完整性
            print("  💾 測試存儲完整性...")
            stored_count = 0
            for log_id in test_interactions:
                retrieved_data = await coordinator.data_manager.retrieve_data(
                    log_id, DataLayer.INTERACTION
                )
                if retrieved_data:
                    stored_count += 1
            
            if stored_count == len(test_interactions):
                results['storage_integrity']['score'] = 25
                results['storage_integrity']['details'] = '存儲完整性正常'
                print("    ✅ 存儲完整性測試通過")
            else:
                results['storage_integrity']['details'] = f'只有{stored_count}/{len(test_interactions)}個數據可檢索'
                print("    ❌ 存儲完整性測試失敗")
            
            # 測試檢索準確性
            print("  🔍 測試檢索準確性...")
            if test_interactions:
                query_result = await coordinator.data_manager.query_data(
                    {'interaction_source': 'system_internal'}, DataLayer.INTERACTION
                )
                
                if len(query_result) >= len(test_interactions):
                    results['retrieval_accuracy']['score'] = 25
                    results['retrieval_accuracy']['details'] = '檢索準確性正常'
                    print("    ✅ 檢索準確性測試通過")
                else:
                    results['retrieval_accuracy']['details'] = f'查詢結果不完整: {len(query_result)}/{len(test_interactions)}'
                    print("    ❌ 檢索準確性測試失敗")
            
            # 測試跨組件一致性
            print("  🔄 測試跨組件一致性...")
            collector_stats = await coordinator.interaction_collector.get_statistics()
            system_status = await coordinator.get_system_status()
            
            collector_count = collector_stats.get('total_collected', 0)
            coordinator_count = system_status['coordinator_status'].get('processed_interactions', 0)
            
            if collector_count > 0 and coordinator_count > 0:
                results['cross_component_consistency']['score'] = 25
                results['cross_component_consistency']['details'] = '跨組件一致性正常'
                print("    ✅ 跨組件一致性測試通過")
            else:
                results['cross_component_consistency']['details'] = f'統計不一致: 收集器{collector_count}, 協調器{coordinator_count}'
                print("    ❌ 跨組件一致性測試失敗")
            
            await coordinator.stop_processing()
            
        except Exception as e:
            error_msg = f"數據一致性測試異常: {e}"
            print(f"    ❌ {error_msg}")
            for test_name in results:
                if results[test_name]['score'] == 0:
                    results[test_name]['details'] = error_msg
        
        return results
    
    def calculate_overall_score(self) -> float:
        """計算總體評分"""
        total_score = 0
        max_score = 0
        
        # 功能測試 (40%)
        functionality_scores = [test['score'] for test in self.test_results['functionality_tests'].values()]
        functionality_total = sum(functionality_scores)
        functionality_max = len(functionality_scores) * 20
        functionality_weight = 0.4
        
        # 性能測試 (25%)
        performance_scores = [test['score'] for test in self.test_results['performance_tests'].values()]
        performance_total = sum(performance_scores)
        performance_max = len(performance_scores) * 25
        performance_weight = 0.25
        
        # 整合測試 (20%)
        integration_scores = [test['score'] for test in self.test_results['integration_tests'].values()]
        integration_total = sum(integration_scores)
        integration_max = len(integration_scores) * 25
        integration_weight = 0.20
        
        # 數據一致性測試 (15%)
        consistency_scores = [test['score'] for test in self.test_results['data_consistency_tests'].values()]
        consistency_total = sum(consistency_scores)
        consistency_max = len(consistency_scores) * 25
        consistency_weight = 0.15
        
        # 計算加權總分
        if functionality_max > 0:
            total_score += (functionality_total / functionality_max) * 100 * functionality_weight
        if performance_max > 0:
            total_score += (performance_total / performance_max) * 100 * performance_weight
        if integration_max > 0:
            total_score += (integration_total / integration_max) * 100 * integration_weight
        if consistency_max > 0:
            total_score += (consistency_total / consistency_max) * 100 * consistency_weight
        
        return round(total_score, 2)
    
    async def generate_test_report(self):
        """生成測試報告"""
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'overall_score': self.test_results['overall_score'],
                'test_environment': self.test_config,
                'status': 'PASSED' if self.test_results['overall_score'] >= 70 else 'FAILED'
            },
            'detailed_results': self.test_results,
            'recommendations': self.generate_recommendations()
        }
        
        # 保存報告
        report_path = Path(self.test_config['base_dir']) / 'unified_architecture_test_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 測試報告已生成: {report_path}")
        return report
    
    def generate_recommendations(self) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        # 基於測試結果生成建議
        if self.test_results['overall_score'] < 70:
            recommendations.append("整體評分偏低，需要全面優化系統")
        
        # 功能測試建議
        functionality_tests = self.test_results['functionality_tests']
        for test_name, test_result in functionality_tests.items():
            if not test_result['passed']:
                recommendations.append(f"需要修復{test_name}功能: {test_result['details']}")
        
        # 性能測試建議
        performance_tests = self.test_results['performance_tests']
        for test_name, test_result in performance_tests.items():
            if test_result['score'] < 20:
                recommendations.append(f"需要優化{test_name}性能: {test_result['details']}")
        
        if not recommendations:
            recommendations.append("系統運行良好，建議繼續監控和維護")
        
        return recommendations

async def main():
    """主測試程序"""
    print("🧪 PowerAutomation v0.53 統一架構整合測試")
    print("=" * 60)
    
    # 設置日誌
    logging.basicConfig(level=logging.WARNING)  # 減少日誌輸出
    
    # 創建測試實例
    test_suite = UnifiedArchitectureIntegrationTest()
    
    # 運行所有測試
    results = await test_suite.run_all_tests()
    
    # 輸出總結
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    overall_score = results['overall_score']
    status = "✅ 通過" if overall_score >= 70 else "❌ 失敗"
    
    print(f"總體評分: {overall_score:.2f}/100 {status}")
    
    # 分類評分
    categories = [
        ('功能完整性', results['functionality_tests']),
        ('性能表現', results['performance_tests']),
        ('整合效果', results['integration_tests']),
        ('數據一致性', results['data_consistency_tests'])
    ]
    
    for category_name, category_results in categories:
        scores = [test['score'] for test in category_results.values()]
        if scores:
            avg_score = sum(scores) / len(scores)
            max_possible = 25 if category_name != '功能完整性' else 20
            percentage = (avg_score / max_possible) * 100
            print(f"{category_name}: {percentage:.1f}% ({avg_score:.1f}/{max_possible})")
    
    print("\n🎯 統一架構整合測試完成！")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())

