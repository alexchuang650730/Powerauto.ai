#!/usr/bin/env python3
"""
PowerAutomation v0.5.2 部署腳本
一鍵啟動端雲模擬環境
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_requirements():
    """檢查運行要求"""
    print("🔍 檢查運行環境...")
    
    # 檢查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 檢查必要文件
    required_files = [
        "dynamic_network_manager.py",
        "edge_cloud_simulator.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少必要文件: {file}")
            return False
    
    print("✅ 所有必要文件存在")
    return True


def install_dependencies():
    """安裝依賴"""
    print("📦 檢查依賴包...")
    
    # 這裡使用標準庫，不需要額外安裝
    print("✅ 使用Python標準庫，無需額外依賴")


def start_services():
    """啟動服務"""
    print("🚀 啟動PowerAutomation v0.5.2 端雲模擬環境...")
    
    try:
        # 啟動端雲模擬器
        subprocess.run([sys.executable, "edge_cloud_simulator.py"], check=True)
    except KeyboardInterrupt:
        print("\n✅ 服務已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")


def main():
    """主函數"""
    print("🎉 PowerAutomation v0.5.2 部署腳本")
    print("=" * 50)
    
    if not check_requirements():
        print("❌ 環境檢查失敗")
        return
    
    install_dependencies()
    start_services()


if __name__ == "__main__":
    main()

