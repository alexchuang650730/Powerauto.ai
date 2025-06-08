#!/usr/bin/env python3
"""
配置環境變量並運行GAIA測試
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """設置環境變量"""
    # 設置API密鑰
    os.environ["GEMINI_API_KEY"] = "AIzaSyBjQOKRMz0uTGnvDe9CDE5BmAwlY0_rCMw"
    os.environ["CLAUDE_API_KEY"] = "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"
    
    # 設置Python路徑
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print("✅ 環境配置完成")

def run_gaia_test():
    """運行GAIA測試"""
    setup_environment()
    
    print("\\n🚀 開始運行GAIA Level 1測試...")
    
    try:
        # 運行CLI命令
        cmd = [
            sys.executable, 
            "mcptool/cli/safe_unified_mcp_cli.py", 
            "gaia", 
            "--level", "1", 
            "--max-tasks", "10"
        ]
        
        result = subprocess.run(
            cmd,
            cwd="/home/ubuntu/Powerauto.ai",
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=600  # 10分鐘超時
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"\\n返回碼: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("❌ 測試超時（10分鐘）")
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")

if __name__ == "__main__":
    run_gaia_test()

