#!/usr/bin/env python3
"""
完整MCP統計器 - 統計所有可註冊的MCP
"""

import os
import sys
from pathlib import Path
import importlib.util
import json

def count_all_mcps():
    """統計所有可註冊的MCP"""
    print("📊 統計所有可註冊的MCP適配器")
    print("=" * 50)
    
    project_root = Path("/home/ubuntu/Powerauto.ai")
    
    # 搜索所有可能的MCP文件
    mcp_patterns = [
        "*mcp*.py",
        "*adapter*.py", 
        "*engine*.py",
        "*tool*.py",
        "*memory*.py",
        "*agent*.py"
    ]
    
    all_files = set()
    
    for pattern in mcp_patterns:
        files = list(project_root.glob(f"**/{pattern}"))
        for file in files:
            if "__pycache__" not in str(file) and file.is_file():
                all_files.add(file)
    
    print(f"🔍 找到 {len(all_files)} 個潛在MCP文件")
    
    # 分類文件
    categories = {
        "mcp_files": [],
        "adapter_files": [],
        "engine_files": [],
        "tool_files": [],
        "memory_files": [],
        "agent_files": [],
        "other_files": []
    }
    
    for file in all_files:
        file_name = file.name.lower()
        relative_path = str(file.relative_to(project_root))
        
        if "mcp" in file_name:
            categories["mcp_files"].append(relative_path)
        elif "adapter" in file_name:
            categories["adapter_files"].append(relative_path)
        elif "engine" in file_name:
            categories["engine_files"].append(relative_path)
        elif "tool" in file_name:
            categories["tool_files"].append(relative_path)
        elif "memory" in file_name:
            categories["memory_files"].append(relative_path)
        elif "agent" in file_name:
            categories["agent_files"].append(relative_path)
        else:
            categories["other_files"].append(relative_path)
    
    # 顯示統計
    total_count = 0
    for category, files in categories.items():
        if files:
            count = len(files)
            total_count += count
            print(f"\n📁 {category.replace('_', ' ').title()}: {count}個")
            for file in sorted(files)[:5]:  # 只顯示前5個
                print(f"   • {file}")
            if len(files) > 5:
                print(f"   ... 還有 {len(files) - 5} 個文件")
    
    print(f"\n📊 總計: {total_count} 個潛在MCP文件")
    
    # 檢查哪些可以作為MCP註冊
    registrable_mcps = []
    
    # 重點檢查的MCP文件
    priority_files = [
        f for f in all_files 
        if any(keyword in f.name.lower() for keyword in [
            "mcp", "adapter", "engine"
        ]) and "test" not in f.name.lower() and "backup" not in f.name.lower()
    ]
    
    print(f"\n🎯 優先級文件: {len(priority_files)} 個")
    
    for file in priority_files:
        try:
            # 嘗試檢查文件是否包含類定義
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 簡單檢查是否包含類定義
            if "class " in content and ("MCP" in content or "Adapter" in content or "Engine" in content):
                registrable_mcps.append(str(file.relative_to(project_root)))
                
        except Exception as e:
            continue
    
    print(f"\n✅ 可註冊的MCP: {len(registrable_mcps)} 個")
    
    # 保存結果
    result = {
        "total_files": total_count,
        "categories": {k: len(v) for k, v in categories.items()},
        "priority_files": len(priority_files),
        "registrable_mcps": len(registrable_mcps),
        "registrable_list": registrable_mcps,
        "category_details": categories
    }
    
    with open("complete_mcp_count.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 詳細統計保存到: complete_mcp_count.json")
    
    return result

if __name__ == "__main__":
    result = count_all_mcps()
    print(f"\n🎯 結論:")
    print(f"   當前註冊: 9個")
    print(f"   可註冊總數: {result['registrable_mcps']}個") 
    print(f"   註冊率: {9/max(result['registrable_mcps'], 1)*100:.1f}%")
    print(f"   目標: 100% ({result['registrable_mcps']}個)")

