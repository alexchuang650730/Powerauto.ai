#!/usr/bin/env python3
"""
GAIA Level 1 完整測試執行器

執行165題完整測試，使用真實API，生成詳細結果
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GAIA_Complete_Tester")

class GAIACompleteTestExecutor:
    """GAIA Level 1 完整測試執行器"""
    
    def __init__(self):
        self.unified_registry = None
        self.test_questions = []
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # 初始化組件
        self._init_components()
        self._load_test_data()
    
    def _init_components(self):
        """初始化測試組件"""
        try:
            # 初始化統一適配器接口
            from mcptool.core.unified_adapter_interface import UnifiedAdapterRegistry
            from mcptool.adapters.core.safe_mcp_registry import CompleteMCPRegistry
            
            registry = CompleteMCPRegistry()
            self.unified_registry = UnifiedAdapterRegistry(registry)
            
            logger.info(f"✅ 測試組件初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 測試組件初始化失敗: {e}")
            raise
    
    def _load_test_data(self):
        """載入測試數據"""
        try:
            data_file = "/home/ubuntu/Powerauto.ai/gaia_level1_complete_dataset.json"
            with open(data_file, 'r', encoding='utf-8') as f:
                self.test_questions = json.load(f)
            
            logger.info(f"✅ 載入了 {len(self.test_questions)} 個測試題目")
            
        except Exception as e:
            logger.error(f"❌ 載入測試數據失敗: {e}")
            raise
    
    def _select_adapter_for_question(self, question: Dict[str, Any]) -> str:
        """為問題選擇最適合的適配器"""
        category = question.get("category", "unknown").lower()
        difficulty = question.get("difficulty", "medium").lower()
        
        # 根據類別和難度選擇適配器
        adapter_selection = {
            # 語言和文學類優先使用Claude
            "literature": "claude",
            "language": "claude",
            "art": "claude",
            "music": "claude",
            "history": "claude",
            
            # 數學和科學類優先使用Gemini
            "math": "gemini", 
            "science": "gemini",
            "logic": "gemini",
            
            # 技術類使用智能工具引擎
            "technology": "smart_tool_engine",
            "economics": "claude",
            
            # 地理和常識類使用Claude
            "geography": "claude",
            "common_sense": "claude",
            
            # 默認使用Claude
            "unknown": "claude"
        }
        
        selected_adapter = adapter_selection.get(category, "claude")
        
        # 對於困難題目，優先使用Claude
        if difficulty == "hard":
            selected_adapter = "claude"
        
        # 確保選擇的適配器可用
        available_adapters = self.unified_registry.list_adapters()
        if selected_adapter not in available_adapters:
            # 回退到第一個可用的適配器
            selected_adapter = available_adapters[0] if available_adapters else "claude"
        
        return selected_adapter
    
    def _process_single_question(self, question: Dict[str, Any], question_index: int) -> Dict[str, Any]:
        """處理單個問題"""
        question_id = question.get("id", f"question_{question_index}")
        question_text = question.get("question", "")
        expected_answer = question.get("answer", "")
        category = question.get("category", "unknown")
        difficulty = question.get("difficulty", "medium")
        
        logger.info(f"處理問題 {question_index+1}/165: {question_id}")
        
        # 選擇適配器
        selected_adapter = self._select_adapter_for_question(question)
        
        # 記錄開始時間
        start_time = time.time()
        
        try:
            # 獲取適配器
            adapter = self.unified_registry.get_adapter(selected_adapter)
            if not adapter:
                raise Exception(f"無法獲取適配器: {selected_adapter}")
            
            # 處理問題
            result = adapter.process(question_text)
            
            # 記錄結束時間
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 提取答案
            actual_answer = ""
            success = result.get("success", False)
            
            if success:
                actual_answer = str(result.get("data", "")).strip()
            else:
                actual_answer = f"錯誤: {result.get('error', 'Unknown error')}"
            
            # 判斷正確性
            is_correct = self._check_answer_correctness(expected_answer, actual_answer)
            
            # 構建結果
            question_result = {
                "question_id": question_id,
                "question": question_text,
                "category": category,
                "difficulty": difficulty,
                "expected_answer": expected_answer,
                "actual_answer": actual_answer,
                "correct": is_correct,
                "success": success,
                "adapter_used": selected_adapter,
                "execution_time": execution_time,
                "raw_response": result,
                "timestamp": datetime.now().isoformat(),
                "error": result.get("error", "") if not success else ""
            }
            
            # 記錄結果
            status_icon = "✅" if is_correct else "❌"
            logger.info(f"{status_icon} {question_id}: {'正確' if is_correct else '錯誤'} ({execution_time:.3f}s)")
            
            return question_result
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            error_result = {
                "question_id": question_id,
                "question": question_text,
                "category": category,
                "difficulty": difficulty,
                "expected_answer": expected_answer,
                "actual_answer": f"處理異常: {str(e)}",
                "correct": False,
                "success": False,
                "adapter_used": selected_adapter,
                "execution_time": execution_time,
                "raw_response": {"error": str(e)},
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            
            logger.error(f"❌ {question_id}: 處理異常 - {e}")
            return error_result
    
    def _check_answer_correctness(self, expected: str, actual: str) -> bool:
        """檢查答案正確性"""
        if not expected or not actual:
            return False
        
        # 清理和標準化答案
        expected_clean = str(expected).strip().lower()
        actual_clean = str(actual).strip().lower()
        
        # 移除常見的標點符號
        import re
        expected_clean = re.sub(r'[.,!?;:]', '', expected_clean)
        actual_clean = re.sub(r'[.,!?;:]', '', actual_clean)
        
        # 直接匹配
        if expected_clean == actual_clean:
            return True
        
        # 包含匹配（實際答案包含預期答案）
        if expected_clean in actual_clean:
            return True
        
        # 數字匹配（提取數字進行比較）
        expected_numbers = re.findall(r'\\d+(?:\\.\\d+)?', expected_clean)
        actual_numbers = re.findall(r'\\d+(?:\\.\\d+)?', actual_clean)
        
        if expected_numbers and actual_numbers:
            try:
                expected_num = float(expected_numbers[0])
                actual_num = float(actual_numbers[0])
                return abs(expected_num - actual_num) < 0.01
            except:
                pass
        
        # 關鍵詞匹配
        expected_words = set(expected_clean.split())
        actual_words = set(actual_clean.split())
        
        # 如果預期答案的主要詞彙都在實際答案中
        if expected_words and len(expected_words.intersection(actual_words)) >= len(expected_words) * 0.8:
            return True
        
        return False
    
    def run_complete_test(self, max_questions: int = None) -> Dict[str, Any]:
        """運行完整測試"""
        logger.info(f"🎯 開始GAIA Level 1完整測試")
        
        self.start_time = datetime.now()
        test_questions = self.test_questions[:max_questions] if max_questions else self.test_questions
        
        logger.info(f"測試題目數: {len(test_questions)}")
        
        # 處理每個問題
        for i, question in enumerate(test_questions):
            try:
                result = self._process_single_question(question, i)
                self.results.append(result)
                
                # 顯示進度
                if (i + 1) % 10 == 0:
                    correct_count = sum(1 for r in self.results if r.get("correct", False))
                    accuracy = correct_count / len(self.results) if self.results else 0
                    logger.info(f"進度: {i+1}/{len(test_questions)} - 當前準確率: {accuracy:.1%}")
                
                # 短暫延遲避免API限制
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"處理問題 {i+1} 時發生錯誤: {e}")
                continue
        
        self.end_time = datetime.now()
        
        # 生成最終結果
        final_results = self._generate_final_results()
        
        logger.info(f"🎯 GAIA測試完成: {final_results['summary']['correct_answers']}/{final_results['summary']['total_questions']} 正確 ({final_results['summary']['accuracy']:.1%})")
        
        return final_results
    
    def _generate_final_results(self) -> Dict[str, Any]:
        """生成最終結果"""
        total_questions = len(self.results)
        correct_answers = sum(1 for r in self.results if r.get("correct", False))
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        total_time = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        avg_time = sum(r.get("execution_time", 0) for r in self.results) / total_questions if total_questions > 0 else 0
        
        # 按類別統計
        category_stats = {}
        adapter_stats = {}
        difficulty_stats = {}
        
        for result in self.results:
            category = result.get("category", "unknown")
            adapter = result.get("adapter_used", "unknown")
            difficulty = result.get("difficulty", "unknown")
            correct = result.get("correct", False)
            
            # 類別統計
            if category not in category_stats:
                category_stats[category] = {"total": 0, "correct": 0}
            category_stats[category]["total"] += 1
            if correct:
                category_stats[category]["correct"] += 1
            
            # 適配器統計
            if adapter not in adapter_stats:
                adapter_stats[adapter] = {"total": 0, "correct": 0}
            adapter_stats[adapter]["total"] += 1
            if correct:
                adapter_stats[adapter]["correct"] += 1
            
            # 難度統計
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {"total": 0, "correct": 0}
            difficulty_stats[difficulty]["total"] += 1
            if correct:
                difficulty_stats[difficulty]["correct"] += 1
        
        return {
            "metadata": {
                "test_name": "GAIA Level 1 Complete Test",
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_duration": total_time,
                "questions_source": "gaia_level1_complete_dataset.json"
            },
            "summary": {
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "accuracy": accuracy,
                "average_execution_time": avg_time,
                "total_execution_time": sum(r.get("execution_time", 0) for r in self.results)
            },
            "statistics": {
                "by_category": category_stats,
                "by_adapter": adapter_stats,
                "by_difficulty": difficulty_stats
            },
            "detailed_results": self.results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """保存測試結果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/ubuntu/Powerauto.ai/gaia_level1_complete_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 測試結果已保存: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ 保存結果失敗: {e}")
            return ""

def main():
    """主函數"""
    print("🎯 GAIA Level 1 完整測試執行器")
    print("=" * 50)
    
    try:
        # 創建測試執行器
        executor = GAIACompleteTestExecutor()
        
        # 運行完整測試
        print("開始執行165題完整測試...")
        results = executor.run_complete_test()
        
        # 保存結果
        result_file = executor.save_results(results)
        
        # 顯示摘要
        summary = results["summary"]
        print(f"\\n📊 測試完成摘要:")
        print(f"總題目數: {summary['total_questions']}")
        print(f"正確答案: {summary['correct_answers']}")
        print(f"準確率: {summary['accuracy']:.1%}")
        print(f"平均執行時間: {summary['average_execution_time']:.3f}秒")
        print(f"總執行時間: {summary['total_execution_time']:.3f}秒")
        
        print(f"\\n📄 詳細結果已保存: {result_file}")
        
        return result_file
        
    except Exception as e:
        print(f"❌ 測試執行失敗: {e}")
        return None

if __name__ == "__main__":
    main()

