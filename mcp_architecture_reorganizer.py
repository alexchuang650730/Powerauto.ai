#!/usr/bin/env python3
"""
MCP架構重組器 - 快速執行
將核心組件移到adapters/core，區分基礎設施和可調用工具
"""

import os
import shutil
from pathlib import Path
import json

class MCPArchitectureReorganizer:
    """MCP架構重組器"""
    
    def __init__(self):
        self.project_root = Path("/home/ubuntu/Powerauto.ai")
        self.core_dir = self.project_root / "mcptool/adapters/core"
        self.adapters_dir = self.project_root / "mcptool/adapters"
        
        # 應該移到core的組件（基礎設施）
        self.core_components = [
            # 基礎架構
            "base_mcp.py",
            "adapter_interface.py", 
            "ai_module_interface.py",
            "adapter_interfaces.py",
            
            # 註冊和管理
            "unified_adapter_registry.py",
            "mcp_registry_integration_manager.py",
            "fixed_unified_adapter_registry.py",
            
            # 核心引擎（不直接調用）
            "webagent_core.py",
            "automatic_tool_creation_engine.py",
            "mcp_core_loader.py",
            
            # 錯誤處理和工具
            "error_handler.py",
            "serializable_mcp_types.py",
            "fixed_event_loop_manager.py",
            
            # 記憶核心
            "memory_query_engine.py",
            
            # 數據處理核心
            "intelligent_intent_processor.py"
        ]
        
        # 應該保持為可調用工具的組件
        self.tool_components = [
            # AI模型適配器
            "claude_mcp.py",
            "gemini_mcp.py", 
            "qwen3_8b_local_mcp.py",
            "simple_claude_adapter.py",
            "simple_gemini_adapter.py",
            
            # 工具引擎（可調用）
            "smart_tool_engine_mcp.py",
            "unified_smart_tool_engine_mcp.py",
            "kilocode_mcp.py",
            "simple_kilocode_adapter.py",
            "simple_smart_tool_engine.py",
            
            # 功能適配器
            "simple_webagent.py",
            "webagent_adapter.py",
            "simple_sequential_thinking.py",
            
            # 記憶系統（可調用）
            "unified_memory_mcp.py",
            "supermemory_mcp.py",
            
            # RL系統
            "rl_srt_mcp.py",
            "rl_srt_dataflow_mcp.py"
        ]
    
    def reorganize_architecture(self):
        """重組MCP架構"""
        print("🔧 開始MCP架構重組...")
        
        # 1. 確保core目錄存在
        self.core_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. 移動核心組件到core
        moved_to_core = self._move_to_core()
        
        # 3. 更新註冊表
        self._update_registry()
        
        # 4. 生成報告
        report = {
            "moved_to_core": moved_to_core,
            "core_components_count": len(moved_to_core),
            "tool_components_count": len(self.tool_components),
            "reorganization_complete": True
        }
        
        return report
    
    def _move_to_core(self):
        """移動組件到core目錄"""
        moved_files = []
        
        for component in self.core_components:
            # 搜索文件位置
            found_files = list(self.project_root.glob(f"**/{component}"))
            
            for file_path in found_files:
                if "core" not in str(file_path) and "__pycache__" not in str(file_path):
                    target_path = self.core_dir / component
                    
                    try:
                        # 如果目標已存在，備份
                        if target_path.exists():
                            backup_path = self.core_dir / f"{component}.backup"
                            shutil.move(str(target_path), str(backup_path))
                        
                        # 移動文件
                        shutil.move(str(file_path), str(target_path))
                        moved_files.append({
                            "file": component,
                            "from": str(file_path),
                            "to": str(target_path)
                        })
                        print(f"✅ 移動到core: {component}")
                        
                    except Exception as e:
                        print(f"❌ 移動失敗 {component}: {e}")
        
        return moved_files
    
    def _update_registry(self):
        """更新註冊表，區分core和tools"""
        registry_path = self.core_dir / "safe_mcp_registry.py"
        
        if not registry_path.exists():
            print("❌ 註冊表不存在")
            return
        
        # 讀取現有註冊表
        with open(registry_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加註釋區分core和tools
        updated_content = content.replace(
            "# 核心可用適配器列表（經過驗證的）",
            """# 核心可用適配器列表（經過驗證的）
        # 
        # 架構說明:
        # - adapters/core/: 基礎設施組件，不直接調用
        # - adapters/: 可調用的工具適配器
        #"""
        )
        
        # 保存更新的註冊表
        with open(registry_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ 更新註冊表完成")

def main():
    """主函數"""
    print("🚀 MCP架構重組 - 快速執行")
    print("=" * 50)
    
    reorganizer = MCPArchitectureReorganizer()
    report = reorganizer.reorganize_architecture()
    
    print(f"\n📊 重組完成:")
    print(f"   移動到core: {report['core_components_count']} 個組件")
    print(f"   保持為工具: {report['tool_components_count']} 個組件")
    
    # 顯示移動的文件
    if report['moved_to_core']:
        print(f"\n📁 移動到core的文件:")
        for item in report['moved_to_core']:
            print(f"   • {item['file']}")
    
    # 保存報告
    report_path = "/home/ubuntu/Powerauto.ai/mcp_architecture_reorganization.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 詳細報告: {report_path}")
    print("✅ MCP架構重組完成！")

if __name__ == "__main__":
    main()

