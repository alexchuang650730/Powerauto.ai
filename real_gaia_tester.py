#!/usr/bin/env python3
"""
PowerAutomation真實GAIA測試器
使用真實的GAIA validation數據和PowerAutomation CLI進行測試
"""

import json
import time
import subprocess
import sys
from pathlib import Path

def load_real_gaia_data():
    """加載真實GAIA測試數據"""
    with open('real_gaia_test_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def test_with_powerautomation_cli(question_data):
    """使用PowerAutomation CLI測試單個問題"""
    question = question_data['Question']
    expected_answer = question_data['Final answer']
    task_id = question_data['task_id']
    
    print(f"\n🔍 測試問題: {task_id}")
    print(f"問題: {question[:100]}...")
    print(f"期望答案: {expected_answer}")
    
    try:
        # 使用PowerAutomation的統一MCP CLI
        cmd = [
            sys.executable, 
            'mcptool/cli/unified_mcp_cli.py',
            'query',
            question
        ]
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2分鐘超時
            cwd='/home/ubuntu/Powerauto.ai'
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if result.returncode == 0:
            ai_answer = result.stdout.strip()
            
            # 簡單的答案匹配檢查
            is_correct = str(expected_answer).lower().strip() in ai_answer.lower()
            
            print(f"✅ AI回答: {ai_answer[:200]}...")
            print(f"⏱️ 處理時間: {processing_time:.2f}秒")
            print(f"🎯 正確性: {'✅ 正確' if is_correct else '❌ 錯誤'}")
            
            return {
                "task_id": task_id,
                "question": question,
                "expected_answer": expected_answer,
                "ai_answer": ai_answer,
                "is_correct": is_correct,
                "processing_time": processing_time,
                "success": True,
                "error": None
            }
        else:
            error_msg = result.stderr or "未知錯誤"
            print(f"❌ CLI執行失敗: {error_msg}")
            
            return {
                "task_id": task_id,
                "question": question,
                "expected_answer": expected_answer,
                "ai_answer": None,
                "is_correct": False,
                "processing_time": processing_time,
                "success": False,
                "error": error_msg
            }
            
    except subprocess.TimeoutExpired:
        print("⏰ 測試超時")
        return {
            "task_id": task_id,
            "question": question,
            "expected_answer": expected_answer,
            "ai_answer": None,
            "is_correct": False,
            "processing_time": 120,
            "success": False,
            "error": "超時"
        }
    except Exception as e:
        print(f"💥 測試異常: {str(e)}")
        return {
            "task_id": task_id,
            "question": question,
            "expected_answer": expected_answer,
            "ai_answer": None,
            "is_correct": False,
            "processing_time": 0,
            "success": False,
            "error": str(e)
        }

def main():
    """主測試流程"""
    print("🚀 PowerAutomation真實GAIA測試開始")
    print("=" * 60)
    
    # 加載測試數據
    test_data = load_real_gaia_data()
    print(f"📊 加載了 {len(test_data)} 個真實GAIA問題")
    
    results = []
    correct_count = 0
    total_time = 0
    
    # 逐個測試
    for i, question_data in enumerate(test_data):
        print(f"\n📝 進度: {i+1}/{len(test_data)}")
        
        result = test_with_powerautomation_cli(question_data)
        results.append(result)
        
        if result['is_correct']:
            correct_count += 1
        
        total_time += result['processing_time']
        
        # 短暫休息避免API限制
        time.sleep(2)
    
    # 計算統計結果
    accuracy = (correct_count / len(test_data)) * 100
    avg_time = total_time / len(test_data)
    
    print("\n" + "=" * 60)
    print("🎯 PowerAutomation真實GAIA測試結果")
    print("=" * 60)
    print(f"📊 總問題數: {len(test_data)}")
    print(f"✅ 正確答案: {correct_count}")
    print(f"❌ 錯誤答案: {len(test_data) - correct_count}")
    print(f"🎯 準確率: {accuracy:.2f}%")
    print(f"⏱️ 總時間: {total_time:.2f}秒")
    print(f"⚡ 平均時間: {avg_time:.2f}秒/問題")
    print(f"🎖️ 目標達成: {'✅ 是' if accuracy >= 90 else '❌ 否'} (目標≥90%)")
    
    # 保存詳細結果
    timestamp = int(time.time())
    result_file = f"powerautomation_real_gaia_results_{timestamp}.json"
    
    final_result = {
        "test_type": "PowerAutomation真實GAIA測試",
        "timestamp": timestamp,
        "total_questions": len(test_data),
        "correct_answers": correct_count,
        "accuracy": accuracy,
        "total_time": total_time,
        "average_time": avg_time,
        "target_achieved": accuracy >= 90,
        "results": results
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print(f"💾 詳細結果已保存到: {result_file}")
    
    return accuracy >= 90

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

