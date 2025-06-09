#!/usr/bin/env python3
"""
快速GAIA測試 - 測試幾個問題
"""

import os
import sys
import json
import time
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcptool.adapters.core.safe_mcp_registry import get_registry

def quick_gaia_test():
    """快速GAIA測試"""
    print("🚀 快速GAIA測試 - 100%註冊率MCP系統")
    print("=" * 50)
    
    # 初始化註冊表
    registry = get_registry()
    available_adapters = registry.list_adapters()
    
    print(f"✅ 可用適配器: {len(available_adapters)}個")
    for adapter in available_adapters:
        print(f"   • {adapter}")
    
    # 測試問題
    test_questions = [
        {
            "question": "What is 2 + 2 * 3?",
            "expected": "8",
            "type": "math"
        },
        {
            "question": "What is the capital of France?",
            "expected": "Paris",
            "type": "knowledge"
        },
        {
            "question": "Calculate the area of a circle with radius 5",
            "expected": "78.54",
            "type": "calculation"
        }
    ]
    
    print(f"\n🧪 測試 {len(test_questions)} 個問題...")
    
    results = []
    correct_count = 0
    
    for i, test in enumerate(test_questions):
        print(f"\n問題 {i+1}: {test['question']}")
        
        # 選擇適配器
        if test['type'] == 'math' or test['type'] == 'calculation':
            adapter_name = 'smart_tool_engine' if 'smart_tool_engine' in available_adapters else 'claude'
        else:
            adapter_name = 'claude' if 'claude' in available_adapters else available_adapters[0]
        
        print(f"使用適配器: {adapter_name}")
        
        try:
            # 獲取適配器並處理
            adapter = registry.get_adapter(adapter_name)
            start_time = time.time()
            
            if hasattr(adapter, 'process'):
                answer = adapter.process(test['question'])
            else:
                answer = f"適配器 {adapter_name} 處理: {test['question']}"
            
            processing_time = time.time() - start_time
            
            # 簡單答案比較
            is_correct = str(test['expected']).lower() in str(answer).lower()
            
            if is_correct:
                correct_count += 1
                print(f"✅ 正確! 答案: {answer}")
            else:
                print(f"❌ 錯誤. 期望: {test['expected']}, 得到: {answer}")
            
            results.append({
                "question": test['question'],
                "expected": test['expected'],
                "answer": str(answer),
                "adapter": adapter_name,
                "is_correct": is_correct,
                "processing_time": processing_time
            })
            
        except Exception as e:
            print(f"❌ 處理失敗: {e}")
            results.append({
                "question": test['question'],
                "expected": test['expected'],
                "answer": f"錯誤: {e}",
                "adapter": adapter_name,
                "is_correct": False,
                "processing_time": 0
            })
    
    # 計算結果
    accuracy = (correct_count / len(test_questions)) * 100
    total_time = sum(r['processing_time'] for r in results)
    
    print(f"\n📊 測試結果:")
    print(f"   正確答案: {correct_count}/{len(test_questions)}")
    print(f"   準確率: {accuracy:.1f}%")
    print(f"   總處理時間: {total_time:.2f}秒")
    print(f"   平均處理時間: {total_time/len(test_questions):.2f}秒")
    
    # 保存結果
    result_file = f"quick_gaia_test_results_{int(time.time())}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_info": {
                "total_questions": len(test_questions),
                "correct_answers": correct_count,
                "accuracy": accuracy,
                "total_time": total_time,
                "available_adapters": available_adapters
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 詳細結果保存到: {result_file}")
    
    return accuracy, available_adapters

if __name__ == "__main__":
    try:
        accuracy, adapters = quick_gaia_test()
        print(f"\n🎯 快速測試完成! 準確率: {accuracy:.1f}%")
        print(f"🔧 可用適配器: {len(adapters)}個")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

