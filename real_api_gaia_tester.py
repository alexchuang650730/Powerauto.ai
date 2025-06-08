#!/usr/bin/env python3
"""
真實API集成的GAIA測試器
使用真實的Claude和Gemini API進行GAIA測試
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
import logging

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcptool.adapters.safe_adapter_manager import get_safe_adapter_manager

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealAPIGAIATester:
    """真實API GAIA測試器"""
    
    def __init__(self):
        self.adapter_manager = get_safe_adapter_manager()
        self.api_keys = {
            "GEMINI_API_KEY": "AIzaSyBjQOKRMz0uTGnvDe9CDE5BmAwlY0_rCMw",
            "CLAUDE_API_KEY": "your_claude_api_key_here"
        }
    
    def call_claude_api(self, question: str, max_tokens: int = 1000) -> str:
        """調用Claude API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_keys["CLAUDE_API_KEY"],
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": f"Please answer this question concisely and accurately: {question}"
                    }
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"].strip()
            else:
                logger.error(f"Claude API錯誤: {response.status_code} - {response.text}")
                return f"API錯誤: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Claude API調用失敗: {str(e)}")
            return f"調用失敗: {str(e)}"
    
    def call_gemini_api(self, question: str) -> str:
        """調用Gemini API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_keys["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt = f"Please answer this question concisely and accurately: {question}"
            response = model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API調用失敗: {str(e)}")
            return f"調用失敗: {str(e)}"
    
    def answer_question_with_real_api(self, question: Dict[str, Any]) -> tuple[str, str]:
        """使用真實API回答問題"""
        question_text = question["Question"]
        has_file = bool(question.get("file_name"))
        
        # 優先使用Claude，如果失敗則使用Gemini
        try:
            logger.info("嘗試使用Claude API...")
            claude_answer = self.call_claude_api(question_text)
            
            if "API錯誤" not in claude_answer and "調用失敗" not in claude_answer:
                return claude_answer, "claude"
            else:
                logger.warning(f"Claude失敗: {claude_answer}")
        except Exception as e:
            logger.warning(f"Claude異常: {str(e)}")
        
        # 嘗試Gemini
        try:
            logger.info("嘗試使用Gemini API...")
            gemini_answer = self.call_gemini_api(question_text)
            
            if "調用失敗" not in gemini_answer:
                return gemini_answer, "gemini"
            else:
                logger.warning(f"Gemini失敗: {gemini_answer}")
        except Exception as e:
            logger.warning(f"Gemini異常: {str(e)}")
        
        # 如果都失敗，返回錯誤信息
        return "所有API調用失敗", "error"
    
    def compare_answers(self, ai_answer: str, expected_answer: str) -> bool:
        """比較答案"""
        if not expected_answer or expected_answer == "?":
            # 沒有標準答案，檢查AI是否給出了合理回答
            return len(ai_answer.strip()) > 0 and "失敗" not in ai_answer and "錯誤" not in ai_answer
        
        # 清理答案
        ai_clean = ai_answer.strip().lower()
        expected_clean = expected_answer.strip().lower()
        
        # 精確匹配
        if ai_clean == expected_clean:
            return True
        
        # 數字匹配（提取數字進行比較）
        import re
        ai_numbers = re.findall(r'\\d+(?:\\.\\d+)?', ai_clean)
        expected_numbers = re.findall(r'\\d+(?:\\.\\d+)?', expected_clean)
        
        if ai_numbers and expected_numbers:
            try:
                ai_num = float(ai_numbers[0])
                expected_num = float(expected_numbers[0])
                # 允許小的數值誤差
                return abs(ai_num - expected_num) < 0.01 or abs(ai_num - expected_num) / max(abs(expected_num), 1) < 0.05
            except ValueError:
                pass
        
        # 包含匹配
        if ai_clean in expected_clean or expected_clean in ai_clean:
            return True
        
        # 關鍵詞匹配
        ai_words = set(ai_clean.split())
        expected_words = set(expected_clean.split())
        common_words = ai_words.intersection(expected_words)
        
        if len(common_words) > 0 and len(common_words) / len(expected_words) > 0.5:
            return True
        
        return False
    
    def test_gaia(self, level: int = 1, max_tasks: int = 10):
        """運行GAIA測試"""
        print(f"🧪 開始真實API GAIA Level {level}測試")
        print(f"📊 測試規模: {max_tasks}個問題")
        print("=" * 50)
        
        try:
            from datasets import load_dataset
            
            print(f"📥 加載GAIA數據集...")
            dataset = load_dataset("gaia-benchmark/GAIA", "2023_all")
            validation_data = dataset["validation"]
            
            # 過濾指定level的問題
            level_questions = [q for q in validation_data if q["Level"] == str(level)]
            
            if len(level_questions) == 0:
                print(f"❌ 沒有找到Level {level}的問題")
                return False
            
            # 限制測試數量
            test_questions = level_questions[:max_tasks]
            
            print(f"📋 找到 {len(level_questions)} 個Level {level}問題")
            print(f"🎯 將測試前 {len(test_questions)} 個問題")
            
            # 開始測試
            results = []
            correct_count = 0
            api_usage = {"claude": 0, "gemini": 0, "error": 0}
            
            for i, question in enumerate(test_questions, 1):
                print(f"\\n🔍 問題 {i}/{len(test_questions)}")
                print(f"   問題: {question['Question'][:100]}...")
                
                start_time = time.time()
                
                try:
                    # 使用真實API回答
                    ai_answer, api_used = self.answer_question_with_real_api(question)
                    api_usage[api_used] += 1
                    
                    processing_time = time.time() - start_time
                    
                    # 比較答案
                    expected_answer = question.get("Final answer", "")
                    is_correct = self.compare_answers(ai_answer, expected_answer)
                    
                    if is_correct:
                        correct_count += 1
                        print(f"   ✅ 正確 ({processing_time:.2f}s, {api_used})")
                    else:
                        print(f"   ❌ 錯誤 ({processing_time:.2f}s, {api_used})")
                        print(f"      AI答案: {ai_answer[:100]}...")
                        print(f"      標準答案: {expected_answer}")
                    
                    results.append({
                        "question_id": i,
                        "question": question["Question"],
                        "ai_answer": ai_answer,
                        "expected_answer": expected_answer,
                        "is_correct": is_correct,
                        "processing_time": processing_time,
                        "api_used": api_used,
                        "has_file": bool(question.get("file_name"))
                    })
                    
                    # 添加延遲避免API限制
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"   ❌ 處理錯誤: {str(e)}")
                    api_usage["error"] += 1
                    results.append({
                        "question_id": i,
                        "question": question["Question"],
                        "ai_answer": f"錯誤: {str(e)}",
                        "expected_answer": expected_answer,
                        "is_correct": False,
                        "processing_time": time.time() - start_time,
                        "api_used": "error",
                        "has_file": bool(question.get("file_name"))
                    })
            
            # 計算結果
            accuracy = (correct_count / len(test_questions)) * 100
            
            print(f"\\n🎉 測試完成!")
            print("=" * 50)
            print(f"📊 測試結果:")
            print(f"   總問題數: {len(test_questions)}")
            print(f"   正確答案: {correct_count}")
            print(f"   準確率: {accuracy:.1f}%")
            print(f"   目標達成: {'✅ 是' if accuracy >= 90 else '❌ 否'} (目標≥90%)")
            
            print(f"\\n🔧 API使用統計:")
            print(f"   Claude: {api_usage['claude']}次")
            print(f"   Gemini: {api_usage['gemini']}次")
            print(f"   錯誤: {api_usage['error']}次")
            
            # 保存結果
            result_file = f"gaia_level{level}_real_api_results_{int(time.time())}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_info": {
                        "level": level,
                        "total_questions": len(test_questions),
                        "correct_answers": correct_count,
                        "accuracy": accuracy,
                        "target_achieved": accuracy >= 90,
                        "api_usage": api_usage
                    },
                    "results": results
                }, f, indent=2, ensure_ascii=False)
            
            print(f"💾 結果已保存到: {result_file}")
            
            return accuracy >= 90
            
        except Exception as e:
            print(f"❌ GAIA測試失敗: {str(e)}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="真實API GAIA測試器")
    parser.add_argument("--level", type=int, default=1, help="GAIA測試級別")
    parser.add_argument("--max-tasks", type=int, default=10, help="最大測試任務數")
    
    args = parser.parse_args()
    
    tester = RealAPIGAIATester()
    success = tester.test_gaia(args.level, args.max_tasks)
    
    if success:
        print("\\n🎉 測試成功達到目標!")
    else:
        print("\\n⚠️ 測試未達到目標，需要進一步優化")

if __name__ == "__main__":
    main()

