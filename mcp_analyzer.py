#!/usr/bin/env python3
"""
MCP適配器分析工具
掃描所有MCP文件並分析問題
"""

import os
import sys
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MCPAnalyzer:
    """MCP適配器分析器"""
    
    def __init__(self):
        self.mcp_files = []
        self.analysis_results = {}
        self.issues = []
        
    def scan_mcp_files(self, root_dir: str) -> List[str]:
        """掃描所有MCP文件"""
        mcp_files = []
        
        for root, dirs, files in os.walk(root_dir):
            # 跳過__pycache__目錄
            if "__pycache__" in root:
                continue
                
            for file in files:
                if file.endswith("_mcp.py") or "mcp" in file.lower():
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        mcp_files.append(full_path)
        
        self.mcp_files = sorted(mcp_files)
        return self.mcp_files
    
    def analyze_mcp_file(self, file_path: str) -> Dict[str, Any]:
        """分析單個MCP文件"""
        result = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "exists": False,
            "readable": False,
            "has_class": False,
            "class_names": [],
            "has_process_method": False,
            "has_abstract_methods": False,
            "import_errors": [],
            "syntax_errors": [],
            "issues": []
        }
        
        try:
            # 檢查文件是否存在
            if not os.path.exists(file_path):
                result["issues"].append("文件不存在")
                return result
            
            result["exists"] = True
            
            # 讀取文件內容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                result["readable"] = True
            except Exception as e:
                result["issues"].append(f"無法讀取文件: {e}")
                return result
            
            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                result["syntax_errors"].append(str(e))
                result["issues"].append(f"語法錯誤: {e}")
                return result
            
            # 分析類定義
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    result["has_class"] = True
                    result["class_names"].append(node.name)
                    
                    # 檢查是否有process方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "process":
                            result["has_process_method"] = True
                        
                        # 檢查抽象方法
                        if isinstance(item, ast.FunctionDef):
                            for decorator in item.decorator_list:
                                if (isinstance(decorator, ast.Name) and decorator.id == "abstractmethod") or \
                                   (isinstance(decorator, ast.Attribute) and decorator.attr == "abstractmethod"):
                                    result["has_abstract_methods"] = True
            
            # 檢查導入
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            __import__(alias.name)
                        except ImportError as e:
                            result["import_errors"].append(f"導入錯誤: {alias.name} - {e}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            __import__(node.module)
                        except ImportError as e:
                            result["import_errors"].append(f"導入錯誤: {node.module} - {e}")
            
            # 檢查常見問題
            if not result["has_class"]:
                result["issues"].append("沒有找到類定義")
            
            if result["has_class"] and not result["has_process_method"]:
                result["issues"].append("沒有process方法")
            
            if result["has_abstract_methods"]:
                result["issues"].append("包含抽象方法，無法實例化")
            
            if result["import_errors"]:
                result["issues"].extend(result["import_errors"])
        
        except Exception as e:
            result["issues"].append(f"分析失敗: {e}")
        
        return result
    
    def analyze_all(self, root_dir: str) -> Dict[str, Any]:
        """分析所有MCP文件"""
        print(f"掃描目錄: {root_dir}")
        
        # 掃描文件
        mcp_files = self.scan_mcp_files(root_dir)
        print(f"找到 {len(mcp_files)} 個MCP文件")
        
        # 分析每個文件
        results = {}
        for file_path in mcp_files:
            print(f"分析: {os.path.basename(file_path)}")
            result = self.analyze_mcp_file(file_path)
            results[file_path] = result
        
        self.analysis_results = results
        
        # 生成總結
        summary = self.generate_summary()
        
        return {
            "summary": summary,
            "detailed_results": results
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成分析總結"""
        total_files = len(self.analysis_results)
        working_files = 0
        files_with_issues = 0
        common_issues = {}
        
        for file_path, result in self.analysis_results.items():
            if not result["issues"]:
                working_files += 1
            else:
                files_with_issues += 1
                
                for issue in result["issues"]:
                    if issue not in common_issues:
                        common_issues[issue] = 0
                    common_issues[issue] += 1
        
        return {
            "total_files": total_files,
            "working_files": working_files,
            "files_with_issues": files_with_issues,
            "success_rate": working_files / total_files if total_files > 0 else 0,
            "common_issues": common_issues
        }
    
    def save_report(self, output_file: str):
        """保存分析報告"""
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "analysis_results": self.analysis_results,
            "summary": self.generate_summary()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"分析報告已保存到: {output_file}")

def main():
    """主函數"""
    analyzer = MCPAnalyzer()
    
    # 分析PowerAutomation目錄
    root_dir = "/home/ubuntu/Powerauto.ai"
    results = analyzer.analyze_all(root_dir)
    
    # 顯示總結
    summary = results["summary"]
    print(f"\\n=== MCP分析總結 ===")
    print(f"總文件數: {summary['total_files']}")
    print(f"正常文件: {summary['working_files']}")
    print(f"有問題文件: {summary['files_with_issues']}")
    print(f"成功率: {summary['success_rate']:.1%}")
    
    print(f"\\n=== 常見問題 ===")
    for issue, count in summary['common_issues'].items():
        print(f"{issue}: {count}個文件")
    
    # 保存報告
    analyzer.save_report("/home/ubuntu/Powerauto.ai/mcp_analysis_report.json")

if __name__ == "__main__":
    main()

