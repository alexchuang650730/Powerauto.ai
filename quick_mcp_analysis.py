#!/usr/bin/env python3
"""
簡化的MCP分析工具
快速掃描MCP文件並識別問題
"""

import os
import json
from pathlib import Path

def quick_analyze_mcp():
    """快速分析MCP文件"""
    root_dir = "/home/ubuntu/Powerauto.ai"
    
    # 找到所有MCP文件
    mcp_files = []
    for root, dirs, files in os.walk(root_dir):
        if "__pycache__" in root:
            continue
        for file in files:
            if file.endswith("_mcp.py") or ("mcp" in file.lower() and file.endswith(".py")):
                mcp_files.append(os.path.join(root, file))
    
    print(f"找到 {len(mcp_files)} 個MCP文件")
    
    # 分析每個文件
    results = {
        "working": [],
        "missing": [],
        "has_issues": [],
        "abstract_class": []
    }
    
    for file_path in sorted(mcp_files):
        file_name = os.path.basename(file_path)
        
        if not os.path.exists(file_path):
            results["missing"].append(file_name)
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否有抽象方法
            if "@abstractmethod" in content or "abstractmethod" in content:
                results["abstract_class"].append(file_name)
            # 檢查是否有基本的類定義和process方法
            elif "class " in content and "def process" in content:
                results["working"].append(file_name)
            else:
                results["has_issues"].append(file_name)
                
        except Exception as e:
            results["has_issues"].append(f"{file_name} (錯誤: {e})")
    
    # 顯示結果
    print(f"\\n=== MCP分析結果 ===")
    print(f"正常工作: {len(results['working'])} 個")
    print(f"抽象類: {len(results['abstract_class'])} 個")
    print(f"有問題: {len(results['has_issues'])} 個")
    print(f"文件缺失: {len(results['missing'])} 個")
    
    print(f"\\n=== 抽象類（需要修復）===")
    for file in results["abstract_class"]:
        print(f"  - {file}")
    
    print(f"\\n=== 有問題的文件 ===")
    for file in results["has_issues"]:
        print(f"  - {file}")
    
    print(f"\\n=== 缺失的文件 ===")
    for file in results["missing"]:
        print(f"  - {file}")
    
    return results

if __name__ == "__main__":
    quick_analyze_mcp()

