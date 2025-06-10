#!/usr/bin/env python3
"""
檢查GAIA數據集結構
"""

from datasets import load_dataset

def check_gaia_dataset():
    print("🔍 正在檢查GAIA數據集結構...")
    
    # 加載數據集
    ds = load_dataset('gaia-benchmark/GAIA', '2023_all', trust_remote_code=True)
    
    print(f"📊 數據集信息:")
    print(f"   - 測試集: {len(ds['test'])} 個問題")
    print(f"   - 驗證集: {len(ds['validation'])} 個問題")
    
    # 檢查測試集的Level分布
    test_levels = {}
    for q in ds['test']:
        level = q['Level']
        test_levels[level] = test_levels.get(level, 0) + 1
    
    print(f"\n📈 測試集Level分布:")
    for level in sorted(test_levels.keys()):
        print(f"   - Level {level}: {test_levels[level]} 個問題")
    
    # 檢查驗證集的Level分布
    val_levels = {}
    for q in ds['validation']:
        level = q['Level']
        val_levels[level] = val_levels.get(level, 0) + 1
    
    print(f"\n📈 驗證集Level分布:")
    for level in sorted(val_levels.keys()):
        print(f"   - Level {level}: {val_levels[level]} 個問題")
    
    # 找到Level 1問題
    level1_val = [q for q in ds['validation'] if q['Level'] == 1]
    if level1_val:
        print(f"\n📝 第一個Level 1驗證問題示例:")
        q = level1_val[0]
        print(f"   - ID: {q['task_id']}")
        print(f"   - Level: {q['Level']}")
        print(f"   - 問題: {q['Question'][:200]}...")
        if q.get('file_name'):
            print(f"   - 附件: {q['file_name']}")
    
    return ds, level1_val

if __name__ == "__main__":
    ds, level1_questions = check_gaia_dataset()
    print(f"\n✅ 找到 {len(level1_questions)} 個Level 1驗證問題可用於測試")

