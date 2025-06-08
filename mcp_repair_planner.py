#!/usr/bin/env python3
"""
MCP修復計劃生成器
分析所有MCP文件並生成修復優先級
"""

import os
import json
from pathlib import Path

def categorize_mcps():
    """分類所有MCP文件"""
    root_dir = "/home/ubuntu/Powerauto.ai"
    
    # 找到所有MCP文件
    mcp_files = []
    for root, dirs, files in os.walk(root_dir):
        if "__pycache__" in root:
            continue
        for file in files:
            if file.endswith("_mcp.py") or ("mcp" in file.lower() and file.endswith(".py")):
                mcp_files.append(os.path.join(root, file))
    
    # 分類MCP
    categories = {
        "core_functionality": [],      # 核心功能
        "ai_models": [],              # AI模型
        "tools_engines": [],          # 工具引擎
        "memory_systems": [],         # 記憶系統
        "workflow_automation": [],    # 工作流自動化
        "data_processing": [],        # 數據處理
        "integration": [],            # 集成適配器
        "development_tools": [],      # 開發工具
        "optimization": [],           # 優化相關
        "testing": [],               # 測試相關
        "cli_interfaces": [],        # CLI接口
        "abstract_base": [],         # 抽象基類
        "unknown": []                # 未分類
    }
    
    for file_path in sorted(mcp_files):
        file_name = os.path.basename(file_path).lower()
        relative_path = os.path.relpath(file_path, root_dir)
        
        # 根據文件名和路徑分類
        if any(keyword in file_name for keyword in ["base_mcp", "abstract", "interface"]):
            categories["abstract_base"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["gemini", "claude", "qwen", "ai_", "model"]):
            categories["ai_models"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["memory", "supermemory"]):
            categories["memory_systems"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["tool", "engine", "smart", "kilo"]):
            categories["tools_engines"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["workflow", "automation", "sequential"]):
            categories["workflow_automation"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["data", "cloud", "edge", "rl_srt"]):
            categories["data_processing"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["zapier", "integration", "registry"]):
            categories["integration"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["dev", "release", "problem_solver"]):
            categories["development_tools"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["optimization", "enhance", "brainstorm", "planner"]):
            categories["optimization"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["test", "confidence", "integrity"]):
            categories["testing"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["cli", "coordinator", "server", "manager"]):
            categories["cli_interfaces"].append((file_path, relative_path))
        elif any(keyword in file_name for keyword in ["core", "central", "unified", "safe"]):
            categories["core_functionality"].append((file_path, relative_path))
        else:
            categories["unknown"].append((file_path, relative_path))
    
    return categories

def generate_repair_plan(categories):
    """生成修復計劃"""
    
    # 優先級定義（1=最高優先級，5=最低優先級）
    priority_map = {
        "abstract_base": 1,           # 基礎類最重要
        "core_functionality": 1,     # 核心功能最重要
        "ai_models": 2,              # AI模型次重要
        "memory_systems": 2,         # 記憶系統次重要
        "tools_engines": 2,          # 工具引擎次重要
        "workflow_automation": 3,    # 工作流中等重要
        "data_processing": 3,        # 數據處理中等重要
        "integration": 3,            # 集成適配器中等重要
        "development_tools": 4,      # 開發工具較低優先級
        "optimization": 4,           # 優化功能較低優先級
        "testing": 5,               # 測試工具最低優先級
        "cli_interfaces": 4,        # CLI接口較低優先級
        "unknown": 3                # 未分類中等優先級
    }
    
    repair_plan = []
    
    for category, files in categories.items():
        if not files:
            continue
            
        priority = priority_map.get(category, 3)
        
        for file_path, relative_path in files:
            repair_plan.append({
                "file_path": file_path,
                "relative_path": relative_path,
                "file_name": os.path.basename(file_path),
                "category": category,
                "priority": priority,
                "status": "pending"
            })
    
    # 按優先級排序
    repair_plan.sort(key=lambda x: (x["priority"], x["file_name"]))
    
    return repair_plan

def main():
    """主函數"""
    print("🔍 分析所有MCP文件...")
    
    # 分類MCP文件
    categories = categorize_mcps()
    
    # 顯示分類結果
    print(f"\\n📊 MCP分類結果:")
    total_files = 0
    for category, files in categories.items():
        if files:
            print(f"  {category}: {len(files)} 個文件")
            total_files += len(files)
    
    print(f"\\n總計: {total_files} 個MCP文件")
    
    # 生成修復計劃
    repair_plan = generate_repair_plan(categories)
    
    # 按優先級分組顯示
    print(f"\\n🎯 修復優先級計劃:")
    for priority in range(1, 6):
        priority_files = [item for item in repair_plan if item["priority"] == priority]
        if priority_files:
            priority_names = {1: "最高", 2: "高", 3: "中等", 4: "較低", 5: "最低"}
            print(f"\\n優先級 {priority} ({priority_names[priority]}): {len(priority_files)} 個文件")
            for item in priority_files[:5]:  # 只顯示前5個
                print(f"  - {item['file_name']} ({item['category']})")
            if len(priority_files) > 5:
                print(f"  ... 還有 {len(priority_files) - 5} 個文件")
    
    # 保存修復計劃
    repair_data = {
        "categories": {k: [{"file_path": fp, "relative_path": rp} for fp, rp in v] 
                      for k, v in categories.items()},
        "repair_plan": repair_plan,
        "summary": {
            "total_files": total_files,
            "categories_count": len([k for k, v in categories.items() if v]),
            "priority_distribution": {
                str(p): len([item for item in repair_plan if item["priority"] == p])
                for p in range(1, 6)
            }
        }
    }
    
    with open("/home/ubuntu/Powerauto.ai/mcp_repair_plan.json", "w", encoding="utf-8") as f:
        json.dump(repair_data, f, ensure_ascii=False, indent=2)
    
    print(f"\\n💾 修復計劃已保存到: mcp_repair_plan.json")
    
    return repair_plan

if __name__ == "__main__":
    main()

