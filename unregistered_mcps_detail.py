#!/usr/bin/env python3
"""
未註冊MCP詳細列表生成器
從檢查報告中提取並分類顯示所有未註冊的MCP
"""

import json
import os
from typing import Dict, List, Any

def load_report():
    """加載檢查報告"""
    report_file = "/home/ubuntu/Powerauto.ai/mcp_registration_check_report.json"
    
    if not os.path.exists(report_file):
        print("❌ 檢查報告不存在，請先運行 mcp_registration_checker.py")
        return None
    
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def display_unregistered_mcps():
    """顯示所有未註冊的MCP"""
    report = load_report()
    if not report:
        return
    
    print("🔍 **完整未註冊MCP列表**")
    print("=" * 80)
    
    # 按類型分組顯示
    unregistered_by_type = report.get("unregistered_by_type", {})
    
    # 定義優先級順序
    priority_order = [
        ("工具引擎", "🔧"),
        ("AI模型適配器", "🤖"), 
        ("記憶/知識系統", "🧠"),
        ("強化學習", "🎯"),
        ("網頁/搜索", "🌐"),
        ("數據處理", "📊"),
        ("工作流自動化", "🔄"),
        ("用戶界面", "💻"),
        ("未知類型", "❓")
    ]
    
    total_count = 0
    
    for category, icon in priority_order:
        if category in unregistered_by_type:
            mcps = unregistered_by_type[category]
            print(f"\n{icon} **{category}** ({len(mcps)}個)")
            print("-" * 60)
            
            for i, mcp in enumerate(mcps, 1):
                # 檢查檔名問題
                naming_issues = []
                if not mcp["has_mcp_suffix"] and not mcp["has_adapter_suffix"]:
                    naming_issues.append("無MCP後綴")
                
                # 檢查文件大小
                size_kb = mcp["file_size"] / 1024
                size_info = f"({size_kb:.1f}KB)"
                
                # 重要性標記
                importance = ""
                if any(keyword in mcp["file_name"].lower() for keyword in ['smart_tool', 'kilocode', 'claude', 'gemini', 'memory', 'rl_srt']):
                    importance = " ⭐ [重要]"
                
                # 顯示信息
                naming_suffix = f" [{', '.join(naming_issues)}]" if naming_issues else ""
                print(f"  {i:2d}. {mcp['file_name']}{naming_suffix}{importance}")
                print(f"      路徑: {mcp['file_path']}")
                print(f"      大小: {size_info} | 匹配指標: {len(mcp['matched_indicators'])}")
                
                # 顯示匹配的MCP特徵
                if mcp['matched_indicators']:
                    indicators = ', '.join(mcp['matched_indicators'][:3])
                    if len(mcp['matched_indicators']) > 3:
                        indicators += f"... (+{len(mcp['matched_indicators'])-3})"
                    print(f"      特徵: {indicators}")
                print()
            
            total_count += len(mcps)
    
    print(f"\n📊 **統計摘要**")
    print(f"   總未註冊MCP: {total_count}")
    print(f"   重要MCP: {sum(1 for category, mcps in unregistered_by_type.items() for mcp in mcps if any(keyword in mcp['file_name'].lower() for keyword in ['smart_tool', 'kilocode', 'claude', 'gemini', 'memory', 'rl_srt']))}")
    print(f"   檔名問題: {sum(1 for category, mcps in unregistered_by_type.items() for mcp in mcps if not mcp['has_mcp_suffix'] and not mcp['has_adapter_suffix'])}")

def display_critical_missing():
    """顯示關鍵缺失的MCP"""
    report = load_report()
    if not report:
        return
    
    print("\n🚨 **關鍵缺失MCP (必須立即註冊)**")
    print("=" * 80)
    
    critical_keywords = [
        'smart_tool_engine',
        'kilocode', 
        'claude_mcp',
        'gemini_mcp',
        'qwen',
        'unified_memory',
        'supermemory',
        'rl_srt',
        'webagent'
    ]
    
    unregistered_mcps = report.get("unregistered_mcps", [])
    critical_mcps = []
    
    for mcp in unregistered_mcps:
        file_name_lower = mcp["file_name"].lower()
        for keyword in critical_keywords:
            if keyword in file_name_lower:
                critical_mcps.append({
                    **mcp,
                    "keyword": keyword,
                    "priority": "HIGH" if keyword in ['smart_tool_engine', 'kilocode', 'claude_mcp', 'gemini_mcp'] else "MEDIUM"
                })
                break
    
    # 按優先級排序
    critical_mcps.sort(key=lambda x: (x["priority"] == "MEDIUM", x["file_name"]))
    
    for i, mcp in enumerate(critical_mcps, 1):
        priority_icon = "🔴" if mcp["priority"] == "HIGH" else "🟡"
        print(f"{i:2d}. {priority_icon} {mcp['file_name']}")
        print(f"    路徑: {mcp['file_path']}")
        print(f"    關鍵詞: {mcp['keyword']}")
        print(f"    類型: {mcp['estimated_type']}")
        print(f"    優先級: {mcp['priority']}")
        print()
    
    print(f"📊 關鍵MCP總數: {len(critical_mcps)}")
    high_priority = sum(1 for mcp in critical_mcps if mcp["priority"] == "HIGH")
    print(f"   高優先級: {high_priority}")
    print(f"   中優先級: {len(critical_mcps) - high_priority}")

def display_registration_commands():
    """顯示註冊命令建議"""
    report = load_report()
    if not report:
        return
    
    print("\n💻 **註冊命令建議**")
    print("=" * 80)
    
    # 關鍵MCP的註冊建議
    registration_map = {
        "smart_tool_engine_mcp.py": ("smart_tool_engine", "SmartToolEngineMCP"),
        "unified_smart_tool_engine_mcp.py": ("unified_smart_tool", "UnifiedSmartToolEngineMCP"),
        "kilocode_mcp.py": ("kilocode", "KiloCodeMCP"),
        "claude_mcp.py": ("claude", "ClaudeMCP"),
        "gemini_mcp.py": ("gemini", "GeminiMCP"),
        "qwen3_8b_local_mcp.py": ("qwen", "Qwen3_8BLocalMCP"),
        "unified_memory_mcp.py": ("unified_memory", "UnifiedMemoryMCP"),
        "supermemory_mcp.py": ("supermemory", "SuperMemoryMCP"),
        "rl_srt_mcp.py": ("rl_srt", "RLSRTMCP"),
        "rl_srt_dataflow_mcp.py": ("rl_srt_dataflow", "RLSRTDataflowMCP"),
        "webagent_adapter.py": ("webagent", "WebAgentAdapter"),
        "simple_smart_tool_engine.py": ("simple_smart_tool", "SimpleSmartToolEngine"),
        "simple_kilocode_adapter.py": ("simple_kilocode", "SimpleKiloCodeAdapter"),
        "simple_gemini_adapter.py": ("simple_gemini", "SimpleGeminiAdapter"),
        "simple_claude_adapter.py": ("simple_claude", "SimpleClaudeAdapter"),
        "simple_webagent.py": ("simple_webagent", "SimpleWebAgent"),
        "simple_sequential_thinking.py": ("simple_sequential", "SimpleSequentialThinking")
    }
    
    unregistered_mcps = report.get("unregistered_mcps", [])
    
    print("在 safe_mcp_registry.py 中添加以下導入:")
    print("```python")
    
    imports = []
    registrations = []
    
    for mcp in unregistered_mcps:
        file_name = mcp["file_name"]
        if file_name in registration_map:
            adapter_id, class_name = registration_map[file_name]
            
            # 生成導入語句
            module_path = mcp["file_path"].replace("/", ".").replace(".py", "")
            import_stmt = f"from {module_path} import {class_name}"
            imports.append(import_stmt)
            
            # 生成註冊語句
            reg_stmt = f'            "{adapter_id}": {class_name},'
            registrations.append(reg_stmt)
    
    # 顯示導入
    for imp in sorted(set(imports)):
        print(imp)
    
    print("\n# 在 core_adapters 字典中添加:")
    for reg in sorted(set(registrations)):
        print(reg)
    
    print("```")
    
    print(f"\n📊 建議註冊的MCP: {len(set(registrations))}")

def main():
    """主函數"""
    display_unregistered_mcps()
    display_critical_missing()
    display_registration_commands()

if __name__ == "__main__":
    main()

