#!/usr/bin/env python3
"""
適配器測試器 - 清理版本
測試各種適配器的基本功能，不包含敏感信息
"""

import os
import sys
import json
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent))

def load_test_config():
    """載入測試配置"""
    return {
        'claude_api_key': os.getenv('CLAUDE_API_KEY', 'test_key_placeholder'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY', 'test_key_placeholder'),
        'test_mode': os.getenv('TEST_MODE', 'mock')  # mock或real
    }

def test_adapters():
    """測試適配器功能"""
    try:
        from mcptool.core.adapter_test_framework import AdapterTestFramework
        
        # 載入配置
        config = load_test_config()
        
        # 創建測試框架
        framework = AdapterTestFramework()
        
        # 運行測試
        print("🧪 開始適配器測試...")
        results = framework.run_comprehensive_tests()
        
        # 顯示結果
        print("📊 測試結果:")
        for adapter_name, result in results.items():
            status = "✅" if result.get('success', False) else "❌"
            print(f"  {status} {adapter_name}: {result.get('message', 'Unknown')}")
        
        return results
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return {}

if __name__ == "__main__":
    test_adapters()

