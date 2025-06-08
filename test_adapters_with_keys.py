#!/usr/bin/env python3
"""
配置API密鑰並測試適配器
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def configure_api_keys():
    """配置API密鑰"""
    # 設置環境變量
    os.environ["GEMINI_API_KEY"] = "AIzaSyBjQOKRMz0uTGnvDe9CDE5BmAwlY0_rCMw"
    os.environ["CLAUDE_API_KEY"] = "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"
    
    print("✅ API密鑰配置完成")

def test_adapters():
    """測試適配器"""
    from mcptool.adapters.simple_gemini_adapter import SimpleGeminiAdapter
    from mcptool.adapters.simple_claude_adapter import SimpleClaudeAdapter
    
    print("\\n=== 測試Gemini適配器 ===")
    gemini = SimpleGeminiAdapter()
    if gemini.test_connection():
        print("✅ Gemini適配器測試成功")
    else:
        print("❌ Gemini適配器測試失敗")
    
    print("\\n=== 測試Claude適配器 ===")
    claude = SimpleClaudeAdapter()
    if claude.test_connection():
        print("✅ Claude適配器測試成功")
    else:
        print("❌ Claude適配器測試失敗")

if __name__ == "__main__":
    configure_api_keys()
    test_adapters()

