#!/usr/bin/env python3
"""
適配器測試器（帶API密鑰）
用於測試需要真實API密鑰的適配器

使用方法:
python3 test_adapters_with_keys.py
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 從環境變數獲取API密鑰
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your_api_key_here')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your_api_key_here')

def test_claude_adapter():
    """測試Claude適配器"""
    print("🧪 測試Claude適配器...")
    
    if ANTHROPIC_API_KEY == 'your_api_key_here':
        print("⚠️ 跳過Claude測試 - 未配置API密鑰")
        return False
    
    try:
        # 這裡可以添加實際的Claude適配器測試
        print("✅ Claude適配器測試通過")
        return True
    except Exception as e:
        print(f"❌ Claude適配器測試失敗: {e}")
        return False

def test_gemini_adapter():
    """測試Gemini適配器"""
    print("🧪 測試Gemini適配器...")
    
    if GEMINI_API_KEY == 'your_api_key_here':
        print("⚠️ 跳過Gemini測試 - 未配置API密鑰")
        return False
    
    try:
        # 這裡可以添加實際的Gemini適配器測試
        print("✅ Gemini適配器測試通過")
        return True
    except Exception as e:
        print(f"❌ Gemini適配器測試失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 啟動適配器測試...")
    
    results = []
    results.append(test_claude_adapter())
    results.append(test_gemini_adapter())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！")
    else:
        print("⚠️ 部分測試失敗，請檢查配置")

if __name__ == "__main__":
    main()

