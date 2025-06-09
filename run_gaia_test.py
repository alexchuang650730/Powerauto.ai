#!/usr/bin/env python3
"""
GAIA測試運行器
用於執行GAIA基準測試的主要腳本

使用方法:
python3 run_gaia_test.py
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

def main():
    """主函數"""
    print("🚀 啟動GAIA測試...")
    
    # 檢查API密鑰配置
    if ANTHROPIC_API_KEY == 'your_api_key_here':
        print("⚠️ 請配置ANTHROPIC_API_KEY環境變數")
        return
    
    if GEMINI_API_KEY == 'your_api_key_here':
        print("⚠️ 請配置GEMINI_API_KEY環境變數")
        return
    
    try:
        # 導入GAIA測試模組
        from test.level9.gaia import GAIATester
        
        # 創建測試器實例
        tester = GAIATester()
        
        # 運行測試
        results = tester.run_tests()
        
        print(f"✅ GAIA測試完成，結果: {results}")
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {e}")
    except Exception as e:
        print(f"❌ 測試執行錯誤: {e}")

if __name__ == "__main__":
    main()

