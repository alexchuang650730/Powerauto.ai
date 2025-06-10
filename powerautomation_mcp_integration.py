#!/usr/bin/env python3
"""
集成到PowerAutomation的簡化MCP選擇器
與GAIA測試系統集成
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from simple_mcp_selector import SimpleMCPSelector, IntegratedMCPSystem

logger = logging.getLogger(__name__)

class PowerAutomationMCPIntegration:
    """PowerAutomation MCP集成系統"""
    
    def __init__(self):
        """初始化集成系統"""
        self.mcp_system = IntegratedMCPSystem()
        self.selector = SimpleMCPSelector()
        
        # 與現有適配器集成
        self.existing_adapters = {
            "gemini": "SimpleGeminiAdapter",
            "claude": "SimpleClaudeAdapter", 
            "smart_tool_engine": "SimpleSmartToolEngine",
            "webagent": "SimpleWebAgent",
            "sequential_thinking": "SimpleSequentialThinking",
            "kilocode": "SimpleKiloCodeAdapter"
        }
        
        logger.info("PowerAutomation MCP集成系統初始化完成")
    
    def enhanced_adapter_selection(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        增強的適配器選擇 - 結合搜索引擎和現有適配器
        
        Args:
            question: 用戶問題
            context: 上下文信息
            
        Returns:
            選中的適配器名稱
        """
        try:
            # 步驟1: 檢查是否有現有適配器能處理
            existing_match = self._check_existing_adapters(question)
            if existing_match:
                logger.info(f"使用現有適配器: {existing_match}")
                return existing_match
            
            # 步驟2: 使用智能選擇器尋找新工具
            recommendations = self.selector.select_tool(question)
            
            if recommendations:
                best_tool = recommendations[0]
                
                # 步驟3: 嘗試快速部署新工具
                deployment = self.selector.quick_deploy(
                    best_tool["name"], 
                    best_tool["platform"]
                )
                
                if deployment["status"] == "success":
                    # 動態註冊新適配器
                    adapter_name = self._register_dynamic_adapter(best_tool, deployment)
                    logger.info(f"動態部署新適配器: {adapter_name}")
                    return adapter_name
            
            # 步驟4: 回退到KiloCode作為最後防線
            logger.info("回退到KiloCode適配器")
            return "kilocode"
            
        except Exception as e:
            logger.error(f"適配器選擇失敗: {e}")
            return "gemini"  # 默認回退
    
    def _check_existing_adapters(self, question: str) -> Optional[str]:
        """檢查現有適配器是否能處理問題"""
        question_lower = question.lower()
        
        # 現有適配器的匹配規則
        adapter_rules = {
            "webagent": ["搜索", "網頁", "查找", "search", "web", "google"],
            "sequential_thinking": ["分析", "推理", "步驟", "思考", "複雜", "邏輯"],
            "smart_tool_engine": ["工具", "處理", "執行", "tool", "process"],
            "claude": ["計算", "數學", "math", "calculate", "分析"],
            "gemini": ["圖片", "圖像", "多模態", "image", "photo"]
        }
        
        for adapter, keywords in adapter_rules.items():
            if any(keyword in question_lower for keyword in keywords):
                return adapter
        
        return None
    
    def _register_dynamic_adapter(self, tool_info: Dict[str, Any], deployment: Dict[str, Any]) -> str:
        """動態註冊新適配器"""
        adapter_name = f"dynamic_{tool_info['name'].replace('-', '_')}"
        
        # 創建動態適配器配置
        adapter_config = {
            "name": adapter_name,
            "tool_name": tool_info["name"],
            "platform": tool_info["platform"],
            "api_endpoint": deployment.get("endpoint"),
            "install_command": deployment.get("install_command"),
            "confidence": tool_info.get("confidence", 0.8)
        }
        
        # 保存到動態適配器註冊表
        self._save_dynamic_adapter(adapter_config)
        
        return adapter_name
    
    def _save_dynamic_adapter(self, config: Dict[str, Any]):
        """保存動態適配器配置"""
        dynamic_adapters_file = "/home/ubuntu/Powerauto.ai/dynamic_adapters.json"
        
        try:
            # 讀取現有配置
            if os.path.exists(dynamic_adapters_file):
                with open(dynamic_adapters_file, 'r', encoding='utf-8') as f:
                    adapters = json.load(f)
            else:
                adapters = {}
            
            # 添加新適配器
            adapters[config["name"]] = config
            
            # 保存配置
            with open(dynamic_adapters_file, 'w', encoding='utf-8') as f:
                json.dump(adapters, f, ensure_ascii=False, indent=2)
                
            logger.info(f"動態適配器配置已保存: {config['name']}")
            
        except Exception as e:
            logger.error(f"保存動態適配器配置失敗: {e}")
    
    def get_all_available_adapters(self) -> List[str]:
        """獲取所有可用適配器（包括動態適配器）"""
        adapters = list(self.existing_adapters.keys())
        
        # 添加動態適配器
        dynamic_adapters_file = "/home/ubuntu/Powerauto.ai/dynamic_adapters.json"
        if os.path.exists(dynamic_adapters_file):
            try:
                with open(dynamic_adapters_file, 'r', encoding='utf-8') as f:
                    dynamic_adapters = json.load(f)
                    adapters.extend(dynamic_adapters.keys())
            except Exception as e:
                logger.warning(f"讀取動態適配器失敗: {e}")
        
        return adapters
    
    def process_gaia_question(self, question: str, expected_answer: str = None) -> Dict[str, Any]:
        """
        處理GAIA問題 - 集成智能選擇器
        
        Args:
            question: GAIA問題
            expected_answer: 期望答案（用於驗證）
            
        Returns:
            處理結果
        """
        try:
            # 選擇最佳適配器
            selected_adapter = self.enhanced_adapter_selection(question)
            
            # 模擬處理過程
            processing_result = {
                "question": question,
                "selected_adapter": selected_adapter,
                "processing_time": 2.5,
                "status": "success"
            }
            
            # 如果是動態適配器，添加部署信息
            if selected_adapter.startswith("dynamic_"):
                processing_result["deployment_info"] = {
                    "type": "dynamic",
                    "auto_deployed": True,
                    "platform": "auto-detected"
                }
            
            # 生成模擬答案
            if "計算" in question or "數學" in question:
                processing_result["answer"] = "42"
            elif "搜索" in question or "查找" in question:
                processing_result["answer"] = "已找到相關信息"
            else:
                processing_result["answer"] = f"使用{selected_adapter}處理完成"
            
            # 驗證答案（如果提供了期望答案）
            if expected_answer:
                processing_result["accuracy"] = self._calculate_accuracy(
                    processing_result["answer"], expected_answer
                )
            
            return processing_result
            
        except Exception as e:
            logger.error(f"GAIA問題處理失敗: {e}")
            return {
                "question": question,
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_accuracy(self, ai_answer: str, expected_answer: str) -> float:
        """計算答案準確率"""
        if not ai_answer or not expected_answer:
            return 0.0
        
        # 簡化的準確率計算
        ai_clean = ai_answer.strip().lower()
        expected_clean = expected_answer.strip().lower()
        
        if ai_clean == expected_clean:
            return 1.0
        elif ai_clean in expected_clean or expected_clean in ai_clean:
            return 0.8
        else:
            return 0.3


def main():
    """測試PowerAutomation MCP集成"""
    integration = PowerAutomationMCPIntegration()
    
    # 測試GAIA問題
    test_questions = [
        "計算 2+2 等於多少？",
        "搜索關於人工智能的最新信息",
        "分析這段文本的情感傾向",
        "處理CSV數據文件",
        "創建一個自動化工作流"
    ]
    
    print("🧪 PowerAutomation MCP集成測試\\n")
    
    for question in test_questions:
        print(f"❓ 問題: {question}")
        result = integration.process_gaia_question(question)
        
        if result["status"] == "success":
            print(f"🎯 選中適配器: {result['selected_adapter']}")
            print(f"💬 答案: {result['answer']}")
            print(f"⏱️ 處理時間: {result['processing_time']}s")
            
            if "deployment_info" in result:
                print(f"🚀 動態部署: {result['deployment_info']['auto_deployed']}")
        else:
            print(f"❌ 錯誤: {result['error']}")
        
        print("-" * 50)
    
    # 顯示所有可用適配器
    all_adapters = integration.get_all_available_adapters()
    print(f"\\n📋 可用適配器總數: {len(all_adapters)}")
    print(f"適配器列表: {', '.join(all_adapters)}")

if __name__ == "__main__":
    main()

