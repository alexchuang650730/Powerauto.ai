#!/usr/bin/env python3
"""
MCP註冊狀態檢查器
檢查所有潛在的MCP文件，找出未註冊和檔名異常的組件
"""

import os
import sys
import json
import logging
import re
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPRegistrationChecker:
    """MCP註冊狀態檢查器"""
    
    def __init__(self, project_root: str = "/home/ubuntu/Powerauto.ai"):
        """初始化檢查器"""
        self.project_root = Path(project_root)
        self.registered_mcps = set()
        self.potential_mcps = []
        self.unregistered_mcps = []
        self.naming_issues = []
        
        logger.info("MCP註冊狀態檢查器初始化完成")
    
    def check_all_mcps(self) -> Dict[str, Any]:
        """檢查所有MCP狀態"""
        try:
            # 1. 獲取已註冊的MCP
            self._get_registered_mcps()
            
            # 2. 掃描所有潛在的MCP文件
            self._scan_potential_mcps()
            
            # 3. 分析未註冊的MCP
            self._analyze_unregistered_mcps()
            
            # 4. 檢查檔名問題
            self._check_naming_issues()
            
            # 5. 生成報告
            return self._generate_report()
            
        except Exception as e:
            logger.error(f"MCP檢查失敗: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_registered_mcps(self):
        """獲取已註冊的MCP列表"""
        try:
            # 檢查安全註冊表
            registry_file = self.project_root / "mcptool/adapters/core/safe_mcp_registry.py"
            
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取已註冊的適配器
                import_pattern = r'from\s+[\w.]+\s+import\s+(\w+)'
                imports = re.findall(import_pattern, content)
                
                # 提取適配器映射
                mapping_pattern = r'"(\w+)":\s*(\w+)'
                mappings = re.findall(mapping_pattern, content)
                
                for adapter_id, class_name in mappings:
                    self.registered_mcps.add(adapter_id)
                
                logger.info(f"找到 {len(self.registered_mcps)} 個已註冊的MCP")
            
        except Exception as e:
            logger.error(f"獲取已註冊MCP失敗: {e}")
    
    def _scan_potential_mcps(self):
        """掃描所有潛在的MCP文件"""
        try:
            # 搜索模式
            search_patterns = [
                "**/*mcp*.py",      # 包含mcp的文件
                "**/adapters/**/*.py",  # adapters目錄下的文件
                "**/*adapter*.py",  # 包含adapter的文件
                "**/*engine*.py",   # 包含engine的文件
                "**/*tool*.py",     # 包含tool的文件
            ]
            
            found_files = set()
            
            for pattern in search_patterns:
                for file_path in self.project_root.glob(pattern):
                    if file_path.is_file() and not any(skip in str(file_path) for skip in ['__pycache__', '.git', 'test']):
                        found_files.add(file_path)
            
            # 分析每個文件
            for file_path in found_files:
                self._analyze_file(file_path)
            
            logger.info(f"掃描到 {len(self.potential_mcps)} 個潛在MCP文件")
            
        except Exception as e:
            logger.error(f"掃描潛在MCP失敗: {e}")
    
    def _analyze_file(self, file_path: Path):
        """分析單個文件是否為MCP"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查是否為MCP的特徵
            mcp_indicators = [
                'class.*MCP',
                'BaseMCP',
                'def process',
                'def get_capabilities',
                'mcp.*adapter',
                'adapter.*mcp'
            ]
            
            is_mcp = False
            matched_indicators = []
            
            for indicator in mcp_indicators:
                if re.search(indicator, content, re.IGNORECASE):
                    is_mcp = True
                    matched_indicators.append(indicator)
            
            if is_mcp:
                relative_path = file_path.relative_to(self.project_root)
                
                mcp_info = {
                    "file_path": str(relative_path),
                    "full_path": str(file_path),
                    "file_name": file_path.name,
                    "has_mcp_suffix": "mcp" in file_path.name.lower(),
                    "has_adapter_suffix": "adapter" in file_path.name.lower(),
                    "matched_indicators": matched_indicators,
                    "estimated_type": self._estimate_mcp_type(file_path.name, content),
                    "file_size": file_path.stat().st_size,
                    "is_registered": self._check_if_registered(file_path.name)
                }
                
                self.potential_mcps.append(mcp_info)
            
        except Exception as e:
            logger.warning(f"分析文件失敗 {file_path}: {e}")
    
    def _estimate_mcp_type(self, file_name: str, content: str) -> str:
        """估計MCP類型"""
        name_lower = file_name.lower()
        content_lower = content.lower()
        
        if any(keyword in name_lower for keyword in ['gemini', 'claude', 'qwen', 'ai', 'llm']):
            return "AI模型適配器"
        elif any(keyword in name_lower for keyword in ['memory', 'rag', 'knowledge']):
            return "記憶/知識系統"
        elif any(keyword in name_lower for keyword in ['tool', 'engine', 'kilocode']):
            return "工具引擎"
        elif any(keyword in name_lower for keyword in ['web', 'search', 'browser']):
            return "網頁/搜索"
        elif any(keyword in name_lower for keyword in ['data', 'process', 'analyze']):
            return "數據處理"
        elif any(keyword in name_lower for keyword in ['workflow', 'automation']):
            return "工作流自動化"
        elif any(keyword in name_lower for keyword in ['rl', 'reinforcement', 'learning']):
            return "強化學習"
        elif any(keyword in name_lower for keyword in ['cli', 'interface', 'ui']):
            return "用戶界面"
        else:
            return "未知類型"
    
    def _check_if_registered(self, file_name: str) -> bool:
        """檢查文件是否已註冊"""
        # 簡化的檢查邏輯
        base_name = file_name.replace('.py', '').replace('_mcp', '').replace('_adapter', '')
        
        for registered in self.registered_mcps:
            if base_name.lower() in registered.lower() or registered.lower() in base_name.lower():
                return True
        
        return False
    
    def _analyze_unregistered_mcps(self):
        """分析未註冊的MCP"""
        for mcp in self.potential_mcps:
            if not mcp["is_registered"]:
                self.unregistered_mcps.append(mcp)
        
        logger.info(f"找到 {len(self.unregistered_mcps)} 個未註冊的MCP")
    
    def _check_naming_issues(self):
        """檢查檔名問題"""
        for mcp in self.potential_mcps:
            issues = []
            
            # 檢查是否缺少mcp後綴
            if not mcp["has_mcp_suffix"] and not mcp["has_adapter_suffix"]:
                issues.append("缺少mcp或adapter後綴")
            
            # 檢查檔名是否過於簡單
            if len(mcp["file_name"]) < 10:
                issues.append("檔名過短，可能不夠描述性")
            
            # 檢查是否有特殊字符
            if re.search(r'[^a-zA-Z0-9_.]', mcp["file_name"]):
                issues.append("檔名包含特殊字符")
            
            if issues:
                self.naming_issues.append({
                    **mcp,
                    "naming_issues": issues
                })
        
        logger.info(f"找到 {len(self.naming_issues)} 個檔名問題")
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成檢查報告"""
        # 按類型分組未註冊的MCP
        unregistered_by_type = {}
        for mcp in self.unregistered_mcps:
            mcp_type = mcp["estimated_type"]
            if mcp_type not in unregistered_by_type:
                unregistered_by_type[mcp_type] = []
            unregistered_by_type[mcp_type].append(mcp)
        
        # 按問題類型分組檔名問題
        naming_issues_by_type = {}
        for mcp in self.naming_issues:
            for issue in mcp["naming_issues"]:
                if issue not in naming_issues_by_type:
                    naming_issues_by_type[issue] = []
                naming_issues_by_type[issue].append(mcp)
        
        report = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_potential_mcps": len(self.potential_mcps),
                "registered_mcps": len(self.registered_mcps),
                "unregistered_mcps": len(self.unregistered_mcps),
                "naming_issues": len(self.naming_issues),
                "registration_rate": len(self.registered_mcps) / max(len(self.potential_mcps), 1) * 100
            },
            "registered_mcps": list(self.registered_mcps),
            "unregistered_mcps": self.unregistered_mcps,
            "unregistered_by_type": unregistered_by_type,
            "naming_issues": self.naming_issues,
            "naming_issues_by_type": naming_issues_by_type,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """生成修復建議"""
        recommendations = []
        
        # 未註冊MCP的建議
        if self.unregistered_mcps:
            recommendations.append({
                "type": "registration",
                "priority": "high",
                "title": "註冊未註冊的MCP",
                "description": f"有 {len(self.unregistered_mcps)} 個MCP未註冊到系統中",
                "action": "將這些MCP添加到safe_mcp_registry.py中"
            })
        
        # 檔名問題的建議
        if self.naming_issues:
            recommendations.append({
                "type": "naming",
                "priority": "medium",
                "title": "修復檔名問題",
                "description": f"有 {len(self.naming_issues)} 個文件存在檔名問題",
                "action": "重命名文件以符合MCP命名規範"
            })
        
        # 類型特定建議
        unregistered_by_type = {}
        for mcp in self.unregistered_mcps:
            mcp_type = mcp["estimated_type"]
            unregistered_by_type[mcp_type] = unregistered_by_type.get(mcp_type, 0) + 1
        
        for mcp_type, count in unregistered_by_type.items():
            if count >= 2:
                recommendations.append({
                    "type": "category",
                    "priority": "medium",
                    "title": f"批量處理{mcp_type}",
                    "description": f"有 {count} 個{mcp_type}未註冊",
                    "action": f"統一處理{mcp_type}的註冊和集成"
                })
        
        return recommendations


def main():
    """主函數"""
    print("🔍 MCP註冊狀態檢查器")
    print("=" * 50)
    
    checker = MCPRegistrationChecker()
    report = checker.check_all_mcps()
    
    if report["status"] != "success":
        print(f"❌ 檢查失敗: {report['error']}")
        return
    
    # 顯示摘要
    summary = report["summary"]
    print(f"\\n📊 檢查摘要:")
    print(f"   潛在MCP總數: {summary['total_potential_mcps']}")
    print(f"   已註冊MCP: {summary['registered_mcps']}")
    print(f"   未註冊MCP: {summary['unregistered_mcps']}")
    print(f"   檔名問題: {summary['naming_issues']}")
    print(f"   註冊率: {summary['registration_rate']:.1f}%")
    
    # 顯示未註冊的MCP
    if report["unregistered_mcps"]:
        print(f"\\n❌ 未註冊的MCP ({len(report['unregistered_mcps'])}個):")
        
        for mcp_type, mcps in report["unregistered_by_type"].items():
            print(f"\\n  📁 {mcp_type} ({len(mcps)}個):")
            for mcp in mcps:
                suffix_info = ""
                if not mcp["has_mcp_suffix"] and not mcp["has_adapter_suffix"]:
                    suffix_info = " [無MCP後綴]"
                print(f"    • {mcp['file_name']}{suffix_info}")
                print(f"      路徑: {mcp['file_path']}")
    
    # 顯示檔名問題
    if report["naming_issues"]:
        print(f"\\n⚠️ 檔名問題 ({len(report['naming_issues'])}個):")
        
        for issue_type, mcps in report["naming_issues_by_type"].items():
            print(f"\\n  🔸 {issue_type} ({len(mcps)}個):")
            for mcp in mcps:
                print(f"    • {mcp['file_name']}")
                print(f"      路徑: {mcp['file_path']}")
    
    # 顯示建議
    if report["recommendations"]:
        print(f"\\n💡 修復建議:")
        for i, rec in enumerate(report["recommendations"], 1):
            priority_icon = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
            print(f"\\n  {i}. {priority_icon} {rec['title']}")
            print(f"     {rec['description']}")
            print(f"     建議: {rec['action']}")
    
    # 保存詳細報告
    report_file = "/home/ubuntu/Powerauto.ai/mcp_registration_check_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\\n📄 詳細報告已保存到: {report_file}")
    print("\\n✅ MCP註冊狀態檢查完成！")


if __name__ == "__main__":
    main()

