#!/usr/bin/env python3
"""
GAIA測試運行器 - 清理版本
不包含任何敏感信息
"""

import os
import sys
import json
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent))

def load_api_keys():
    """從環境變數載入API密鑰"""
    return {
        'claude_api_key': os.getenv('CLAUDE_API_KEY', 'your_claude_api_key_here'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY', 'your_gemini_api_key_here'),
        'github_token': os.getenv('GITHUB_TOKEN', 'your_github_token_here')
    }

def run_gaia_test():
    """運行GAIA測試"""
    try:
        from mcptool.core.robust_gaia_tester import RobustGAIATester
        
        # 載入API配置
        api_config = load_api_keys()
        
        # 創建測試器
        tester = RobustGAIATester(
            claude_api_key=api_config['claude_api_key'],
            gemini_api_key=api_config['gemini_api_key']
        )
        
        # 運行測試
        print("🚀 開始GAIA Level 1測試...")
        results = tester.run_complete_test()
        
        # 保存結果
        output_file = f"gaia_test_results_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 測試完成，結果保存到: {output_file}")
        print(f"📊 準確率: {results.get('accuracy', 0):.1%}")
        
        return results
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return None

if __name__ == "__main__":
    import time
    run_gaia_test()

