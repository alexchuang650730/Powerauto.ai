#!/usr/bin/env python3
"""
智能MCP選擇和部署系統
使用搜索引擎進行工具發現和自動部署
"""

import os
import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ToolPlatform(Enum):
    """工具平台枚舉"""
    MCP_SO = "mcp.so"
    ACI_DEV = "aci.dev"
    ZAPIER = "zapier.com"
    GITHUB = "github.com"
    CUSTOM = "custom"

@dataclass
class ToolRecommendation:
    """工具推薦結果"""
    name: str
    platform: ToolPlatform
    description: str
    confidence_score: float
    download_url: str
    installation_command: str
    api_endpoint: Optional[str] = None
    documentation_url: Optional[str] = None

class IntelligentMCPSelector:
    """智能MCP選擇器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化智能MCP選擇器"""
        self.config = config or {}
        
        # 搜索引擎配置
        self.search_engines = {
            "google": "https://www.googleapis.com/customsearch/v1",
            "bing": "https://api.bing.microsoft.com/v7.0/search",
            "duckduckgo": "https://api.duckduckgo.com/"
        }
        
        # 工具平台API配置
        self.platform_apis = {
            ToolPlatform.MCP_SO: {
                "search_url": "https://api.mcp.so/v1/search",
                "download_url": "https://api.mcp.so/v1/download",
                "api_key": os.getenv("MCP_SO_API_KEY")
            },
            ToolPlatform.ACI_DEV: {
                "search_url": "https://api.aci.dev/v1/tools/search",
                "download_url": "https://api.aci.dev/v1/tools/download",
                "api_key": os.getenv("ACI_DEV_API_KEY")
            },
            ToolPlatform.ZAPIER: {
                "search_url": "https://zapier.com/api/v1/apps/search",
                "download_url": "https://zapier.com/api/v1/apps/install",
                "api_key": os.getenv("ZAPIER_API_KEY")
            }
        }
        
        # 意圖分析提示模板
        self.intent_analysis_prompt = """
        分析以下用戶請求，推薦最合適的工具類型和具體工具名稱：
        
        用戶請求: {user_request}
        
        請提供：
        1. 主要意圖類型 (如: 數據處理, 網頁搜索, 計算, 文本分析等)
        2. 推薦的工具類型 (如: API工具, 數據庫工具, AI模型等)
        3. 具體工具名稱建議 (如: pandas, requests, openai等)
        4. 搜索關鍵詞 (用於在工具平台搜索)
        
        以JSON格式回答。
        """
        
        logger.info("智能MCP選擇器初始化完成")
    
    def select_best_mcp(self, user_request: str) -> List[ToolRecommendation]:
        """
        為用戶請求選擇最佳MCP工具
        
        Args:
            user_request: 用戶請求描述
            
        Returns:
            推薦的工具列表
        """
        try:
            # 步驟1: 分析用戶意圖
            intent_analysis = self._analyze_user_intent(user_request)
            
            # 步驟2: 使用搜索引擎查找相關工具
            search_results = self._search_relevant_tools(intent_analysis)
            
            # 步驟3: 在各個平台搜索具體工具
            platform_results = self._search_platform_tools(intent_analysis)
            
            # 步驟4: 合併和排序結果
            recommendations = self._merge_and_rank_results(
                search_results, platform_results, user_request
            )
            
            logger.info(f"為請求 '{user_request}' 找到 {len(recommendations)} 個工具推薦")
            return recommendations
            
        except Exception as e:
            logger.error(f"MCP選擇失敗: {e}")
            return []
    
    def _analyze_user_intent(self, user_request: str) -> Dict[str, Any]:
        """分析用戶意圖"""
        # 使用簡化的意圖分析
        intent_keywords = {
            "data_processing": ["數據", "處理", "分析", "統計", "data", "process"],
            "web_search": ["搜索", "查找", "網頁", "search", "web", "google"],
            "calculation": ["計算", "數學", "運算", "math", "calculate"],
            "text_analysis": ["文本", "文字", "語言", "text", "nlp"],
            "image_processing": ["圖片", "圖像", "照片", "image", "photo"],
            "api_integration": ["API", "接口", "集成", "連接", "integration"],
            "automation": ["自動化", "工作流", "automation", "workflow"],
            "ai_model": ["AI", "人工智能", "模型", "machine learning", "ML"]
        }
        
        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword.lower() in user_request.lower() for keyword in keywords):
                detected_intents.append(intent)
        
        # 生成搜索關鍵詞
        search_keywords = self._generate_search_keywords(user_request, detected_intents)
        
        return {
            "primary_intent": detected_intents[0] if detected_intents else "general",
            "all_intents": detected_intents,
            "search_keywords": search_keywords,
            "original_request": user_request
        }
    
    def _generate_search_keywords(self, user_request: str, intents: List[str]) -> List[str]:
        """生成搜索關鍵詞"""
        keywords = []
        
        # 基於意圖生成關鍵詞
        intent_keywords_map = {
            "data_processing": ["pandas", "numpy", "data analysis tool", "csv processor"],
            "web_search": ["web scraper", "search api", "google search", "web crawler"],
            "calculation": ["calculator", "math library", "computation tool"],
            "text_analysis": ["nlp tool", "text processor", "language model"],
            "image_processing": ["image editor", "photo tool", "computer vision"],
            "api_integration": ["api client", "rest api", "webhook"],
            "automation": ["automation tool", "workflow engine", "task scheduler"],
            "ai_model": ["ai model", "machine learning", "neural network"]
        }
        
        for intent in intents:
            if intent in intent_keywords_map:
                keywords.extend(intent_keywords_map[intent])
        
        # 從用戶請求中提取關鍵詞
        import re
        words = re.findall(r'\\b\\w+\\b', user_request.lower())
        important_words = [word for word in words if len(word) > 3]
        keywords.extend(important_words[:5])  # 取前5個重要詞
        
        return list(set(keywords))  # 去重
    
    def _search_relevant_tools(self, intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用搜索引擎查找相關工具"""
        search_results = []
        
        for keyword in intent_analysis["search_keywords"][:3]:  # 限制搜索次數
            try:
                # 構造搜索查詢
                query = f"{keyword} tool api mcp automation"
                
                # 模擬搜索結果（實際應該調用搜索API）
                mock_results = self._mock_search_results(query, keyword)
                search_results.extend(mock_results)
                
                time.sleep(0.5)  # 避免請求過快
                
            except Exception as e:
                logger.warning(f"搜索關鍵詞 '{keyword}' 失敗: {e}")
        
        return search_results
    
    def _mock_search_results(self, query: str, keyword: str) -> List[Dict[str, Any]]:
        """模擬搜索結果（實際應該調用真實搜索API）"""
        # 這裡提供一些模擬的搜索結果
        mock_tools = {
            "pandas": {
                "name": "pandas-mcp",
                "description": "Data analysis and manipulation tool",
                "platform": "github.com",
                "url": "https://github.com/pandas-dev/pandas"
            },
            "requests": {
                "name": "requests-mcp",
                "description": "HTTP library for API calls",
                "platform": "github.com", 
                "url": "https://github.com/psf/requests"
            },
            "search": {
                "name": "google-search-mcp",
                "description": "Google search API integration",
                "platform": "mcp.so",
                "url": "https://mcp.so/tools/google-search"
            },
            "calculator": {
                "name": "math-calculator-mcp",
                "description": "Advanced mathematical calculator",
                "platform": "aci.dev",
                "url": "https://aci.dev/tools/calculator"
            }
        }
        
        results = []
        for tool_key, tool_info in mock_tools.items():
            if tool_key.lower() in keyword.lower() or keyword.lower() in tool_info["description"].lower():
                results.append(tool_info)
        
        return results
    
    def _search_platform_tools(self, intent_analysis: Dict[str, Any]) -> Dict[ToolPlatform, List[Dict]]:
        """在各個工具平台搜索"""
        platform_results = {}
        
        for platform in ToolPlatform:
            if platform == ToolPlatform.CUSTOM:
                continue
                
            try:
                results = self._search_single_platform(platform, intent_analysis)
                platform_results[platform] = results
            except Exception as e:
                logger.warning(f"平台 {platform.value} 搜索失敗: {e}")
                platform_results[platform] = []
        
        return platform_results
    
    def _search_single_platform(self, platform: ToolPlatform, intent_analysis: Dict[str, Any]) -> List[Dict]:
        """在單個平台搜索工具"""
        if platform not in self.platform_apis:
            return []
        
        api_config = self.platform_apis[platform]
        
        # 模擬平台搜索結果
        mock_platform_tools = {
            ToolPlatform.MCP_SO: [
                {
                    "name": "web-scraper-pro",
                    "description": "Professional web scraping tool",
                    "download_url": "https://mcp.so/download/web-scraper-pro",
                    "api_endpoint": "https://api.mcp.so/web-scraper-pro"
                },
                {
                    "name": "data-analyzer",
                    "description": "Advanced data analysis toolkit",
                    "download_url": "https://mcp.so/download/data-analyzer",
                    "api_endpoint": "https://api.mcp.so/data-analyzer"
                }
            ],
            ToolPlatform.ACI_DEV: [
                {
                    "name": "smart-calculator",
                    "description": "AI-powered calculator with natural language",
                    "download_url": "https://aci.dev/download/smart-calculator",
                    "api_endpoint": "https://api.aci.dev/smart-calculator"
                },
                {
                    "name": "text-processor",
                    "description": "Advanced text processing and NLP",
                    "download_url": "https://aci.dev/download/text-processor",
                    "api_endpoint": "https://api.aci.dev/text-processor"
                }
            ],
            ToolPlatform.ZAPIER: [
                {
                    "name": "workflow-automation",
                    "description": "Automated workflow management",
                    "download_url": "https://zapier.com/apps/workflow-automation",
                    "api_endpoint": "https://hooks.zapier.com/workflow-automation"
                }
            ]
        }
        
        return mock_platform_tools.get(platform, [])
    
    def _merge_and_rank_results(self, search_results: List[Dict], 
                               platform_results: Dict[ToolPlatform, List[Dict]], 
                               user_request: str) -> List[ToolRecommendation]:
        """合併和排序結果"""
        all_recommendations = []
        
        # 處理搜索引擎結果
        for result in search_results:
            platform = self._determine_platform(result.get("platform", ""))
            recommendation = ToolRecommendation(
                name=result["name"],
                platform=platform,
                description=result["description"],
                confidence_score=self._calculate_confidence(result, user_request),
                download_url=result["url"],
                installation_command=f"pip install {result['name']}"
            )
            all_recommendations.append(recommendation)
        
        # 處理平台結果
        for platform, results in platform_results.items():
            for result in results:
                recommendation = ToolRecommendation(
                    name=result["name"],
                    platform=platform,
                    description=result["description"],
                    confidence_score=self._calculate_confidence(result, user_request),
                    download_url=result["download_url"],
                    installation_command=self._generate_install_command(platform, result["name"]),
                    api_endpoint=result.get("api_endpoint")
                )
                all_recommendations.append(recommendation)
        
        # 按信心分數排序
        all_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return all_recommendations[:10]  # 返回前10個推薦
    
    def _determine_platform(self, platform_str: str) -> ToolPlatform:
        """確定工具平台"""
        platform_mapping = {
            "mcp.so": ToolPlatform.MCP_SO,
            "aci.dev": ToolPlatform.ACI_DEV,
            "zapier.com": ToolPlatform.ZAPIER,
            "github.com": ToolPlatform.GITHUB
        }
        
        for key, platform in platform_mapping.items():
            if key in platform_str.lower():
                return platform
        
        return ToolPlatform.CUSTOM
    
    def _calculate_confidence(self, tool_info: Dict, user_request: str) -> float:
        """計算工具推薦的信心分數"""
        score = 0.0
        
        # 基於描述匹配
        description = tool_info.get("description", "").lower()
        request_words = user_request.lower().split()
        
        for word in request_words:
            if len(word) > 3 and word in description:
                score += 0.2
        
        # 基於工具名稱匹配
        name = tool_info.get("name", "").lower()
        for word in request_words:
            if len(word) > 3 and word in name:
                score += 0.3
        
        # 平台加權
        platform_weights = {
            "mcp.so": 0.3,
            "aci.dev": 0.25,
            "zapier.com": 0.2,
            "github.com": 0.15
        }
        
        platform = tool_info.get("platform", "")
        for platform_key, weight in platform_weights.items():
            if platform_key in platform:
                score += weight
                break
        
        return min(score, 1.0)  # 限制在0-1之間
    
    def _generate_install_command(self, platform: ToolPlatform, tool_name: str) -> str:
        """生成安裝命令"""
        install_commands = {
            ToolPlatform.MCP_SO: f"mcp install {tool_name}",
            ToolPlatform.ACI_DEV: f"aci install {tool_name}",
            ToolPlatform.ZAPIER: f"zapier install {tool_name}",
            ToolPlatform.GITHUB: f"git clone https://github.com/{tool_name}",
            ToolPlatform.CUSTOM: f"pip install {tool_name}"
        }
        
        return install_commands.get(platform, f"pip install {tool_name}")


def main():
    """測試智能MCP選擇器"""
    selector = IntelligentMCPSelector()
    
    # 測試用例
    test_requests = [
        "我需要分析CSV數據文件",
        "幫我搜索網頁信息",
        "計算複雜的數學公式",
        "處理和分析文本內容",
        "自動化工作流程"
    ]
    
    for request in test_requests:
        print(f"\\n🔍 用戶請求: {request}")
        recommendations = selector.select_best_mcp(request)
        
        print(f"📋 推薦工具 ({len(recommendations)}個):")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec.name} ({rec.platform.value})")
            print(f"     描述: {rec.description}")
            print(f"     信心分數: {rec.confidence_score:.2f}")
            print(f"     安裝: {rec.installation_command}")

if __name__ == "__main__":
    main()

