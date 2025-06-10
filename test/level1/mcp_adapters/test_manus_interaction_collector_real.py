"""
PowerAutomation Level 1 真實單元測試 - interaction_log_manager (Manus功能)

測試類別: mcp_adapters
測試目標: 驗證InteractionLogManager中整合的Manus交互收集功能的真實環境測試
"""

import unittest
import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from interaction_log_manager import InteractionLogManager

class TestRealInteractionLogManagerManus(unittest.TestCase):
    """
    InteractionLogManager Manus功能真實環境測試類
    
    測試覆蓋範圍:
    - 真實Manus服務連接測試
    - 實際數據處理測試
    - 性能基準測試
    - 錯誤恢復測試
    """
    
    def setUp(self):
        """測試前設置"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = InteractionLogManager(base_dir=self.temp_dir)
        
    def tearDown(self):
        """測試後清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_real_manus_connection(self):
        """測試真實Manus連接"""
        # 注意：這個測試需要真實的Manus服務
        # 在沒有網絡連接或Manus服務不可用時會失敗
        try:
            result = self.manager.connect_to_manus()
            # 如果連接成功，驗證結果
            if result:
                self.assertTrue(result)
                print("✅ 成功連接到Manus服務")
            else:
                print("⚠️ 無法連接到Manus服務（可能是網絡問題或服務不可用）")
                self.skipTest("Manus服務不可用")
        except Exception as e:
            print(f"⚠️ Manus連接測試異常: {e}")
            self.skipTest(f"Manus連接異常: {e}")
    
    def test_real_data_processing(self):
        """測試真實數據處理"""
        # 使用真實的響應格式進行測試
        real_response = """
        我來分析這個問題。
        
        <thought>
        用戶想要測試Manus交互收集功能，我需要提供一個包含思考過程和行動的響應。
        這個測試將驗證提取功能是否正常工作。
        </thought>
        
        <action>
        創建測試響應，包含思考過程和具體行動步驟。
        </action>
        
        基於分析，我建議以下解決方案...
        """
        
        # 記錄交互
        interaction = self.manager.record_manus_interaction(
            "real_test",
            "測試Manus交互收集功能",
            real_response
        )
        
        # 驗證提取結果
        self.assertIsNotNone(interaction)
        self.assertEqual(len(interaction['thought_process']), 1)
        self.assertEqual(len(interaction['actions']), 1)
        self.assertIn("用戶想要測試", interaction['thought_process'][0])
        self.assertIn("創建測試響應", interaction['actions'][0])
    
    def test_performance_benchmark(self):
        """測試性能基準"""
        import time
        
        # 測試大量數據處理性能
        start_time = time.time()
        
        for i in range(100):
            response = f"Response {i} <thought>Thought {i}</thought> <action>Action {i}</action>"
            self.manager.record_manus_interaction(f"perf_test_{i}", f"Input {i}", response)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 驗證性能指標
        self.assertLess(processing_time, 5.0, "處理100個交互應該在5秒內完成")
        
        # 驗證數據完整性
        stats = self.manager.get_manus_statistics()
        self.assertEqual(stats['total'], 100)
        
        print(f"✅ 性能測試完成: 處理100個交互用時 {processing_time:.2f} 秒")
    
    def test_error_recovery(self):
        """測試錯誤恢復"""
        # 測試無效響應處理
        invalid_responses = [
            None,
            "",
            123,
            {"invalid": "json"},
            "<thought>Incomplete thought",
            "<action>Incomplete action"
        ]
        
        for i, invalid_response in enumerate(invalid_responses):
            try:
                interaction = self.manager.record_manus_interaction(
                    f"error_test_{i}",
                    f"Error input {i}",
                    invalid_response
                )
                # 即使響應無效，也應該能記錄交互
                self.assertIsNotNone(interaction)
            except Exception as e:
                self.fail(f"處理無效響應時不應該拋出異常: {e}")
    
    def test_large_data_handling(self):
        """測試大數據處理"""
        # 創建大型響應
        large_thought = "這是一個很長的思考過程。" * 1000
        large_action = "這是一個很長的行動描述。" * 1000
        large_response = f"<thought>{large_thought}</thought> <action>{large_action}</action>"
        
        # 記錄大型交互
        interaction = self.manager.record_manus_interaction(
            "large_data_test",
            "大數據測試輸入",
            large_response
        )
        
        # 驗證處理結果
        self.assertIsNotNone(interaction)
        self.assertEqual(len(interaction['thought_process']), 1)
        self.assertEqual(len(interaction['actions']), 1)
        self.assertGreater(len(interaction['thought_process'][0]), 10000)
        self.assertGreater(len(interaction['actions'][0]), 10000)
    
    def test_concurrent_real_processing(self):
        """測試並發真實處理"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def process_interactions(thread_id):
            try:
                for i in range(20):
                    response = f"Thread {thread_id} Response {i} <thought>Concurrent thought {thread_id}-{i}</thought>"
                    interaction = self.manager.record_manus_interaction(
                        f"concurrent_{thread_id}_{i}",
                        f"Concurrent input {thread_id}-{i}",
                        response
                    )
                    results_queue.put(("success", thread_id, i))
            except Exception as e:
                results_queue.put(("error", thread_id, str(e)))
        
        # 創建多個線程
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=process_interactions, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join()
        
        # 收集結果
        success_count = 0
        error_count = 0
        
        while not results_queue.empty():
            result_type, thread_id, data = results_queue.get()
            if result_type == "success":
                success_count += 1
            else:
                error_count += 1
                print(f"線程 {thread_id} 錯誤: {data}")
        
        # 驗證結果
        self.assertEqual(success_count, 100)  # 5 threads * 20 interactions
        self.assertEqual(error_count, 0)
        
        # 驗證最終統計
        stats = self.manager.get_manus_statistics()
        self.assertGreaterEqual(stats['total'], 100)
        
        print(f"✅ 並發測試完成: 成功處理 {success_count} 個交互，錯誤 {error_count} 個")

if __name__ == '__main__':
    unittest.main()

