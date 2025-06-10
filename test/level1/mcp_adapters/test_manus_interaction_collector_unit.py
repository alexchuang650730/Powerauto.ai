"""
PowerAutomation Level 1 單元測試 - interaction_log_manager (Manus功能)

測試類別: mcp_adapters
測試目標: 驗證InteractionLogManager中整合的Manus交互收集功能
"""

import unittest
import asyncio
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from interaction_log_manager import InteractionLogManager

class TestInteractionLogManagerManus(unittest.TestCase):
    """
    InteractionLogManager Manus功能單元測試類
    
    測試覆蓋範圍:
    - Manus連接功能測試
    - 思考過程提取測試
    - 行動提取測試
    - 交互記錄測試
    - 批量處理測試
    - 統計分析測試
    """
    
    def setUp(self):
        """測試前設置"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = InteractionLogManager(base_dir=self.temp_dir)
        
    def tearDown(self):
        """測試後清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manus_config_loading(self):
        """測試Manus配置加載"""
        # 測試默認配置
        self.assertIsNotNone(self.manager.manus_config)
        self.assertEqual(self.manager.manus_config['batch_size'], 10)
        self.assertEqual(self.manager.manus_config['timeout'], 30)
        self.assertEqual(self.manager.manus_config['max_retries'], 3)
    
    def test_thought_process_extraction(self):
        """測試思考過程提取"""
        # 測試單個思考過程
        response = "Some text <thought>This is a thought</thought> more text"
        thoughts = self.manager._extract_thought_process(response)
        self.assertEqual(len(thoughts), 1)
        self.assertEqual(thoughts[0], "This is a thought")
        
        # 測試多個思考過程
        response = "<thought>First thought</thought> text <thought>Second thought</thought>"
        thoughts = self.manager._extract_thought_process(response)
        self.assertEqual(len(thoughts), 2)
        self.assertEqual(thoughts[0], "First thought")
        self.assertEqual(thoughts[1], "Second thought")
        
        # 測試無思考過程
        response = "No thoughts here"
        thoughts = self.manager._extract_thought_process(response)
        self.assertEqual(len(thoughts), 0)
    
    def test_actions_extraction(self):
        """測試行動提取"""
        # 測試單個行動
        response = "Some text <action>This is an action</action> more text"
        actions = self.manager._extract_actions(response)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0], "This is an action")
        
        # 測試多個行動
        response = "<action>First action</action> text <action>Second action</action>"
        actions = self.manager._extract_actions(response)
        self.assertEqual(len(actions), 2)
        
        # 測試無行動
        response = "No actions here"
        actions = self.manager._extract_actions(response)
        self.assertEqual(len(actions), 0)
    
    def test_manus_interaction_recording(self):
        """測試Manus交互記錄"""
        interaction = self.manager.record_manus_interaction(
            "test", 
            "test input", 
            "test response <thought>test thought</thought> <action>test action</action>"
        )
        
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction['type'], 'test')
        self.assertEqual(interaction['user_input'], 'test input')
        self.assertEqual(len(interaction['thought_process']), 1)
        self.assertEqual(len(interaction['actions']), 1)
        self.assertIn('timestamp', interaction)
        self.assertIn('datetime', interaction)
    
    def test_manus_statistics(self):
        """測試Manus統計功能"""
        # 添加一些測試數據
        self.manager.record_manus_interaction("type1", "input1", "response1")
        self.manager.record_manus_interaction("type2", "input2", "response2")
        self.manager.record_manus_interaction("type1", "input3", "response3")
        
        stats = self.manager.get_manus_statistics()
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['by_type']['type1'], 2)
        self.assertEqual(stats['by_type']['type2'], 1)
        self.assertIn('avg_response_length', stats)
        self.assertIn('avg_thought_count', stats)
        self.assertIn('avg_action_count', stats)
    
    def test_batch_processing(self):
        """測試批量處理"""
        # 設置小的批量大小進行測試
        original_batch_size = self.manager.manus_config['batch_size']
        self.manager.manus_config['batch_size'] = 2
        
        # 添加數據觸發批量保存
        self.manager.record_manus_interaction("test1", "input1", "response1")
        self.assertEqual(len(self.manager.interaction_data), 1)
        
        self.manager.record_manus_interaction("test2", "input2", "response2")
        # 檢查數據是否被清空（表示已保存）
        self.assertEqual(len(self.manager.interaction_data), 0)
        
        # 恢復原始配置
        self.manager.manus_config['batch_size'] = original_batch_size
    
    @patch('requests.Session.get')
    def test_manus_connection(self, mock_get):
        """測試Manus連接"""
        # 測試成功連接
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.manager.connect_to_manus()
        self.assertTrue(result)
        
        # 測試連接失敗
        mock_response.status_code = 404
        result = self.manager.connect_to_manus()
        self.assertFalse(result)
    
    @patch('requests.Session.post')
    def test_send_command_to_manus(self, mock_post):
        """測試發送指令到Manus"""
        # 測試成功發送
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response
        
        result = self.manager.send_command_to_manus("test command")
        self.assertIsNotNone(result)
        self.assertEqual(result["result"], "success")
        
        # 測試發送失敗
        mock_response.status_code = 500
        result = self.manager.send_command_to_manus("test command")
        self.assertIsNone(result)
    
    def test_data_export_import(self):
        """測試數據導入導出"""
        # 添加測試數據
        self.manager.record_manus_interaction("test", "input", "response")
        
        # 測試導出
        export_file = os.path.join(self.temp_dir, "test_export.json")
        result = self.manager.export_manus_data(export_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_file))
        
        # 清空數據
        self.manager.interaction_data = []
        
        # 測試導入
        result = self.manager.import_manus_data(export_file)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.interaction_data), 1)

class TestInteractionLogManagerManusAsync(unittest.TestCase):
    """
    InteractionLogManager Manus功能異步單元測試類
    """
    
    def setUp(self):
        """測試前設置"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = InteractionLogManager(base_dir=self.temp_dir)
    
    def tearDown(self):
        """測試後清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_concurrent_interaction_recording(self):
        """測試並發交互記錄"""
        import threading
        
        def record_interactions():
            for i in range(10):
                self.manager.record_manus_interaction(f"type{i}", f"input{i}", f"response{i}")
        
        # 創建多個線程同時記錄
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=record_interactions)
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join()
        
        # 檢查數據完整性
        stats = self.manager.get_manus_statistics()
        self.assertEqual(stats['total'], 30)  # 3 threads * 10 interactions

if __name__ == '__main__':
    unittest.main()

