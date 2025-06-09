#!/usr/bin/env python3
"""
KiloCodeRAG MCP 功能列表管理器
提供完整的功能列表和能力展示
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class KiloCodeRAGCapabilityManager:
    """KiloCodeRAG MCP 功能管理器"""
    
    def __init__(self):
        """初始化功能管理器"""
        self.capabilities = self._define_capabilities()
        self.usage_stats = {}
        
        logger.info("KiloCodeRAG功能管理器初始化完成")
    
    def _define_capabilities(self) -> Dict[str, Any]:
        """定義所有功能能力"""
        return {
            "kilocode_functions": {
                "name": "KiloCode動態工具創建",
                "description": "動態創建和執行各種專用工具",
                "functions": [
                    {
                        "id": "create_calculator",
                        "name": "創建計算器工具",
                        "description": "動態創建數學計算工具",
                        "category": "math",
                        "usage": "處理數學計算、公式求解、數值運算",
                        "example": "計算 2+2*3 的結果",
                        "parameters": ["數學表達式", "計算類型"],
                        "output": "計算結果和過程"
                    },
                    {
                        "id": "create_data_processor",
                        "name": "創建數據處理工具",
                        "description": "動態創建數據分析和處理工具",
                        "category": "data",
                        "usage": "處理CSV數據、統計分析、數據清洗",
                        "example": "分析銷售數據的趨勢",
                        "parameters": ["數據源", "分析類型"],
                        "output": "分析結果和可視化"
                    },
                    {
                        "id": "create_text_processor",
                        "name": "創建文本處理工具",
                        "description": "動態創建文本分析和處理工具",
                        "category": "text",
                        "usage": "文本分析、情感分析、關鍵詞提取",
                        "example": "分析文章的情感傾向",
                        "parameters": ["文本內容", "分析維度"],
                        "output": "分析結果和統計"
                    },
                    {
                        "id": "create_search_engine",
                        "name": "創建搜索引擎工具",
                        "description": "動態創建信息檢索工具",
                        "category": "search",
                        "usage": "網頁搜索、知識檢索、信息查找",
                        "example": "搜索人工智能的最新發展",
                        "parameters": ["搜索關鍵詞", "搜索範圍"],
                        "output": "搜索結果和摘要"
                    },
                    {
                        "id": "create_logic_engine",
                        "name": "創建邏輯推理工具",
                        "description": "動態創建邏輯推理和問題解決工具",
                        "category": "reasoning",
                        "usage": "邏輯推理、問題分解、決策支持",
                        "example": "分析複雜問題的解決方案",
                        "parameters": ["問題描述", "推理類型"],
                        "output": "推理過程和結論"
                    },
                    {
                        "id": "create_code_generator",
                        "name": "創建代碼生成工具",
                        "description": "動態創建代碼生成和優化工具",
                        "category": "coding",
                        "usage": "代碼生成、代碼優化、代碼審查",
                        "example": "生成Python數據處理腳本",
                        "parameters": ["需求描述", "編程語言"],
                        "output": "生成的代碼和說明"
                    }
                ]
            },
            "rag_functions": {
                "name": "RAG知識檢索",
                "description": "基於向量數據庫的智能知識檢索",
                "functions": [
                    {
                        "id": "search_knowledge",
                        "name": "知識檢索",
                        "description": "在知識庫中搜索相關信息",
                        "category": "search",
                        "usage": "檢索項目文檔、歷史交互、技術資料",
                        "example": "搜索GAIA測試相關信息",
                        "parameters": ["查詢關鍵詞", "結果數量", "搜索範圍"],
                        "output": "相關文檔和匹配度"
                    },
                    {
                        "id": "index_document",
                        "name": "文檔索引",
                        "description": "將新文檔添加到知識庫",
                        "category": "indexing",
                        "usage": "索引新的項目文件、用戶交互數據",
                        "example": "索引新的API文檔",
                        "parameters": ["文檔內容", "元數據", "分類標籤"],
                        "output": "索引狀態和ID"
                    },
                    {
                        "id": "get_similar_content",
                        "name": "相似內容檢索",
                        "description": "基於語義相似度檢索相關內容",
                        "category": "similarity",
                        "usage": "找到相似的問題解答、相關的代碼片段",
                        "example": "找到類似的錯誤解決方案",
                        "parameters": ["參考內容", "相似度閾值"],
                        "output": "相似內容列表"
                    },
                    {
                        "id": "analyze_knowledge_gaps",
                        "name": "知識缺口分析",
                        "description": "分析知識庫中的缺失信息",
                        "category": "analysis",
                        "usage": "識別需要補充的知識領域",
                        "example": "分析缺少的技術文檔",
                        "parameters": ["分析範圍", "評估標準"],
                        "output": "缺口報告和建議"
                    }
                ]
            },
            "integration_functions": {
                "name": "集成功能",
                "description": "KiloCode和RAG的集成能力",
                "functions": [
                    {
                        "id": "knowledge_enhanced_tool_creation",
                        "name": "知識增強工具創建",
                        "description": "基於知識庫創建更智能的工具",
                        "category": "enhancement",
                        "usage": "利用歷史數據創建更準確的工具",
                        "example": "基於歷史交互創建個性化助手",
                        "parameters": ["工具類型", "知識範圍"],
                        "output": "增強型工具"
                    },
                    {
                        "id": "interactive_learning",
                        "name": "交互式學習",
                        "description": "從用戶交互中學習並改進",
                        "category": "learning",
                        "usage": "持續改進工具性能和準確性",
                        "example": "從用戶反饋中優化回答質量",
                        "parameters": ["學習數據", "改進目標"],
                        "output": "學習報告和改進建議"
                    },
                    {
                        "id": "context_aware_processing",
                        "name": "上下文感知處理",
                        "description": "基於上下文提供更準確的服務",
                        "category": "context",
                        "usage": "理解用戶意圖和環境背景",
                        "example": "根據項目背景提供相關建議",
                        "parameters": ["當前上下文", "歷史記錄"],
                        "output": "上下文感知的結果"
                    }
                ]
            },
            "system_functions": {
                "name": "系統管理功能",
                "description": "系統監控和管理能力",
                "functions": [
                    {
                        "id": "get_system_status",
                        "name": "獲取系統狀態",
                        "description": "查看系統運行狀態和統計信息",
                        "category": "monitoring",
                        "usage": "監控系統健康狀況",
                        "example": "檢查知識庫索引狀態",
                        "parameters": [],
                        "output": "系統狀態報告"
                    },
                    {
                        "id": "get_capability_list",
                        "name": "獲取功能列表",
                        "description": "列出所有可用的功能和能力",
                        "category": "info",
                        "usage": "了解系統能力和使用方法",
                        "example": "查看所有可用功能",
                        "parameters": ["分類過濾"],
                        "output": "功能列表和說明"
                    },
                    {
                        "id": "get_usage_statistics",
                        "name": "獲取使用統計",
                        "description": "查看功能使用統計和性能指標",
                        "category": "analytics",
                        "usage": "分析系統使用情況",
                        "example": "查看最常用的功能",
                        "parameters": ["時間範圍", "統計維度"],
                        "output": "使用統計報告"
                    },
                    {
                        "id": "optimize_performance",
                        "name": "性能優化",
                        "description": "優化系統性能和資源使用",
                        "category": "optimization",
                        "usage": "提升系統響應速度",
                        "example": "優化知識檢索速度",
                        "parameters": ["優化目標", "資源限制"],
                        "output": "優化報告和建議"
                    }
                ]
            }
        }
    
    def get_capability_list(self, category: Optional[str] = None, format: str = "detailed") -> Dict[str, Any]:
        """獲取功能列表"""
        try:
            if category:
                # 返回特定分類的功能
                if category in self.capabilities:
                    capabilities = {category: self.capabilities[category]}
                else:
                    return {
                        "status": "error",
                        "message": f"分類 '{category}' 不存在",
                        "available_categories": list(self.capabilities.keys())
                    }
            else:
                # 返回所有功能
                capabilities = self.capabilities
            
            if format == "simple":
                # 簡化格式
                result = {}
                for cat_name, cat_info in capabilities.items():
                    result[cat_name] = {
                        "name": cat_info["name"],
                        "description": cat_info["description"],
                        "function_count": len(cat_info["functions"]),
                        "functions": [f["name"] for f in cat_info["functions"]]
                    }
            else:
                # 詳細格式
                result = capabilities
            
            return {
                "status": "success",
                "capabilities": result,
                "total_categories": len(capabilities),
                "total_functions": sum(len(cat["functions"]) for cat in capabilities.values()),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"獲取功能列表失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_function_details(self, function_id: str) -> Dict[str, Any]:
        """獲取特定功能的詳細信息"""
        try:
            for category_name, category_info in self.capabilities.items():
                for function in category_info["functions"]:
                    if function["id"] == function_id:
                        return {
                            "status": "success",
                            "function": function,
                            "category": category_name,
                            "category_name": category_info["name"],
                            "usage_count": self.usage_stats.get(function_id, 0)
                        }
            
            return {
                "status": "error",
                "message": f"功能 '{function_id}' 不存在"
            }
            
        except Exception as e:
            logger.error(f"獲取功能詳情失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def search_functions(self, query: str) -> Dict[str, Any]:
        """搜索功能"""
        try:
            query_lower = query.lower()
            results = []
            
            for category_name, category_info in self.capabilities.items():
                for function in category_info["functions"]:
                    # 搜索功能名稱、描述、用途
                    searchable_text = f"{function['name']} {function['description']} {function['usage']}".lower()
                    
                    if query_lower in searchable_text:
                        results.append({
                            "function_id": function["id"],
                            "name": function["name"],
                            "description": function["description"],
                            "category": category_name,
                            "category_name": category_info["name"],
                            "relevance_score": searchable_text.count(query_lower)
                        })
            
            # 按相關性排序
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return {
                "status": "success",
                "query": query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            logger.error(f"搜索功能失敗: {e}")
            return {
                "status": "error",
                "message": str(e),
                "results": []
            }
    
    def record_usage(self, function_id: str):
        """記錄功能使用"""
        self.usage_stats[function_id] = self.usage_stats.get(function_id, 0) + 1
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """獲取使用統計"""
        try:
            total_usage = sum(self.usage_stats.values())
            
            # 按使用次數排序
            sorted_usage = sorted(
                self.usage_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # 獲取功能名稱
            usage_with_names = []
            for function_id, count in sorted_usage:
                function_details = self.get_function_details(function_id)
                if function_details["status"] == "success":
                    usage_with_names.append({
                        "function_id": function_id,
                        "name": function_details["function"]["name"],
                        "category": function_details["category"],
                        "usage_count": count,
                        "usage_percentage": (count / total_usage * 100) if total_usage > 0 else 0
                    })
            
            return {
                "status": "success",
                "total_usage": total_usage,
                "unique_functions_used": len(self.usage_stats),
                "most_used_functions": usage_with_names[:10],
                "usage_distribution": usage_with_names
            }
            
        except Exception as e:
            logger.error(f"獲取使用統計失敗: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


def main():
    """測試功能列表管理器"""
    print("🔧 KiloCodeRAG MCP 功能列表測試\\n")
    
    manager = KiloCodeRAGCapabilityManager()
    
    # 獲取所有功能列表（簡化格式）
    print("📋 所有功能分類（簡化格式）:")
    simple_list = manager.get_capability_list(format="simple")
    
    if simple_list["status"] == "success":
        for category, info in simple_list["capabilities"].items():
            print(f"\\n🔹 {info['name']}")
            print(f"   描述: {info['description']}")
            print(f"   功能數量: {info['function_count']}")
            print(f"   功能列表: {', '.join(info['functions'])}")
    
    print("\\n" + "="*60)
    
    # 獲取特定分類的詳細功能
    print("\\n🛠️ KiloCode功能詳細列表:")
    kilocode_details = manager.get_capability_list(category="kilocode_functions")
    
    if kilocode_details["status"] == "success":
        functions = kilocode_details["capabilities"]["kilocode_functions"]["functions"]
        for func in functions:
            print(f"\\n• {func['name']} ({func['id']})")
            print(f"  描述: {func['description']}")
            print(f"  用途: {func['usage']}")
            print(f"  示例: {func['example']}")
    
    print("\\n" + "="*60)
    
    # 搜索功能
    print("\\n🔍 功能搜索測試:")
    search_queries = ["計算", "數據", "搜索", "知識"]
    
    for query in search_queries:
        results = manager.search_functions(query)
        print(f"\\n搜索 '{query}': {results['total_results']} 個結果")
        
        for result in results["results"][:2]:  # 只顯示前2個結果
            print(f"  • {result['name']} (相關性: {result['relevance_score']})")
    
    print("\\n" + "="*60)
    
    # 模擬使用統計
    print("\\n📊 使用統計測試:")
    
    # 模擬一些使用記錄
    test_usage = [
        "create_calculator", "search_knowledge", "create_data_processor",
        "search_knowledge", "create_calculator", "index_document",
        "search_knowledge", "get_system_status"
    ]
    
    for func_id in test_usage:
        manager.record_usage(func_id)
    
    stats = manager.get_usage_statistics()
    if stats["status"] == "success":
        print(f"總使用次數: {stats['total_usage']}")
        print(f"使用過的功能數: {stats['unique_functions_used']}")
        print("\\n最常用功能:")
        
        for func in stats["most_used_functions"][:5]:
            print(f"  • {func['name']}: {func['usage_count']} 次 ({func['usage_percentage']:.1f}%)")
    
    print("\\n✅ 功能列表測試完成！")

if __name__ == "__main__":
    main()

