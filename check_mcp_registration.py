#!/usr/bin/env python3
"""
簡單的MCP註冊檢查器
"""

import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mcptool.adapters.core.safe_mcp_registry import get_registry
    
    print("🔍 檢查當前MCP註冊狀態")
    print("=" * 40)
    
    # 獲取註冊表
    registry = get_registry()
    
    # 獲取已註冊的適配器
    adapters = registry.list_adapters()
    
    print(f"✅ 當前已註冊MCP: {len(adapters)}個")
    print("\n📋 已註冊的MCP列表:")
    
    for i, adapter in enumerate(adapters, 1):
        print(f"   {i:2d}. {adapter}")
    
    print(f"\n📊 註冊統計:")
    print(f"   已註冊: {len(adapters)}個")
    print(f"   目標總數: 86個")
    print(f"   註冊率: {len(adapters)/86*100:.1f}%")
    
    if len(adapters) >= 86:
        print("🎉 已達到100%註冊率!")
    else:
        print(f"⚠️  還需註冊: {86 - len(adapters)}個MCP")

except Exception as e:
    print(f"❌ 檢查失敗: {e}")
    import traceback
    traceback.print_exc()

