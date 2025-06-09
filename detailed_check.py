#!/usr/bin/env python3
"""
詳細檢查GAIA數據集結構
"""

from datasets import load_dataset

def detailed_check():
    print("🔍 詳細檢查GAIA數據集結構...")
    
    # 加載數據集
    ds = load_dataset('gaia-benchmark/GAIA', '2023_all', trust_remote_code=True)
    
    print(f"📊 數據集信息:")
    print(f"   - 測試集: {len(ds['test'])} 個問題")
    print(f"   - 驗證集: {len(ds['validation'])} 個問題")
    
    # 檢查前幾個問題的結構
    print(f"\n📝 前5個測試問題的結構:")
    for i, q in enumerate(ds['test'][:5]):
        print(f"   問題 {i+1}:")
        print(f"      - 字段: {list(q.keys())}")
        print(f"      - Level: {q.get('Level', 'NOT_FOUND')}")
        if 'Level' in q:
            print(f"      - Level類型: {type(q['Level'])}")
        print(f"      - task_id: {q.get('task_id', 'NOT_FOUND')}")
        print()
    
    # 嘗試不同的Level字段名
    possible_level_fields = ['Level', 'level', 'difficulty', 'Difficulty']
    
    for field in possible_level_fields:
        level1_count = 0
        for q in ds['test']:
            if q.get(field) == 1:
                level1_count += 1
        print(f"   使用字段 '{field}' 找到 {level1_count} 個Level 1問題")
    
    # 檢查所有可能的Level值
    all_levels = set()
    for q in ds['test']:
        if 'Level' in q:
            all_levels.add(q['Level'])
    
    print(f"\n📈 所有Level值: {sorted(all_levels)}")
    
    return ds

if __name__ == "__main__":
    ds = detailed_check()

