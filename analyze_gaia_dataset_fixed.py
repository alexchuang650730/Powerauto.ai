#!/usr/bin/env python3
"""
統計GAIA數據集的完整分布 - 修正版
"""

from datasets import load_dataset
import json

def analyze_gaia_dataset():
    print("🔍 正在分析GAIA數據集的完整分布...")
    
    try:
        # 加載完整數據集
        dataset = load_dataset('gaia-benchmark/GAIA', '2023_all', trust_remote_code=True)
        
        # 檢查可用的分割
        available_splits = list(dataset.keys())
        print(f"📊 可用的數據分割: {available_splits}")
        
        total_questions = 0
        for split in available_splits:
            split_size = len(dataset[split])
            total_questions += split_size
            print(f"   - {split}: {split_size} 個問題")
        
        print(f"   - 總計: {total_questions} 個問題")
        
        # 統計各個分割的Level分布
        total_stats = {}
        
        for split in available_splits:
            print(f"\n📈 {split.upper()}集Level分布:")
            level_count = {}
            
            for item in dataset[split]:
                level = item.get('Level', 'Unknown')
                level_key = f'Level {level}'
                level_count[level_key] = level_count.get(level_key, 0) + 1
                total_stats[level_key] = total_stats.get(level_key, 0) + 1
            
            for level in sorted(level_count.keys()):
                count = level_count[level]
                percentage = (count / len(dataset[split])) * 100
                print(f"   - {level}: {count} 個問題 ({percentage:.1f}%)")
        
        print(f"\n🎯 總體Level分布:")
        for level in sorted(total_stats.keys()):
            count = total_stats[level]
            percentage = (count / total_questions) * 100
            print(f"   - {level}: {count} 個問題 ({percentage:.1f}%)")
        
        # 檢查文件附件情況
        print(f"\n📎 文件附件統計:")
        for split in available_splits:
            with_files = 0
            without_files = 0
            
            for item in dataset[split]:
                if item.get('file_name'):
                    with_files += 1
                else:
                    without_files += 1
            
            total = len(dataset[split])
            print(f"   - {split.upper()}集: {with_files} 個有附件 ({(with_files/total)*100:.1f}%), {without_files} 個無附件 ({(without_files/total)*100:.1f}%)")
        
        # 檢查問題長度分布
        print(f"\n📝 問題長度統計:")
        for split in available_splits:
            lengths = [len(item['Question']) for item in dataset[split]]
            avg_length = sum(lengths) / len(lengths)
            min_length = min(lengths)
            max_length = max(lengths)
            print(f"   - {split.upper()}集: 平均 {avg_length:.0f} 字符, 最短 {min_length}, 最長 {max_length}")
        
        # 檢查第一個問題的結構
        print(f"\n🔍 數據結構示例 (第一個問題):")
        first_item = dataset[available_splits[0]][0]
        print(f"   - 字段: {list(first_item.keys())}")
        print(f"   - 問題ID: {first_item.get('task_id', 'N/A')}")
        print(f"   - Level: {first_item.get('Level', 'N/A')}")
        print(f"   - 問題長度: {len(first_item.get('Question', ''))} 字符")
        print(f"   - 有附件: {'是' if first_item.get('file_name') else '否'}")
        
        # 保存詳細統計
        detailed_stats = {
            'dataset_overview': {
                'available_splits': available_splits,
                'total_size': total_questions
            },
            'split_sizes': {},
            'level_distribution': {},
            'file_attachment_stats': {},
            'question_length_stats': {}
        }
        
        # 各分割大小
        for split in available_splits:
            detailed_stats['split_sizes'][split] = len(dataset[split])
        
        # 詳細Level分布
        for split in available_splits:
            level_count = {}
            for item in dataset[split]:
                level = item.get('Level', 'Unknown')
                level_key = f'Level {level}'
                level_count[level_key] = level_count.get(level_key, 0) + 1
            detailed_stats['level_distribution'][split] = level_count
        
        # 文件附件統計
        for split in available_splits:
            with_files = sum(1 for item in dataset[split] if item.get('file_name'))
            without_files = len(dataset[split]) - with_files
            detailed_stats['file_attachment_stats'][split] = {
                'with_files': with_files,
                'without_files': without_files,
                'total': len(dataset[split])
            }
        
        # 問題長度統計
        for split in available_splits:
            lengths = [len(item['Question']) for item in dataset[split]]
            detailed_stats['question_length_stats'][split] = {
                'average': sum(lengths) / len(lengths),
                'min': min(lengths),
                'max': max(lengths)
            }
        
        # 保存統計結果
        with open('gaia_dataset_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 詳細統計已保存到: gaia_dataset_statistics.json")
        
        return detailed_stats
        
    except Exception as e:
        print(f"❌ 分析失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    stats = analyze_gaia_dataset()

