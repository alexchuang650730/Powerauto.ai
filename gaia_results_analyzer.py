#!/usr/bin/env python3
"""
GAIA Level 1 完整測試結果分析器

分析165題測試結果並生成詳細表格
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path

def analyze_gaia_results(result_file: str):
    """分析GAIA測試結果"""
    
    print("🎯 GAIA Level 1 完整測試結果分析")
    print("=" * 60)
    
    # 載入結果
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 基本統計
    summary = results.get("summary", {})
    detailed_results = results.get("detailed_results", [])
    
    print(f"📊 測試摘要:")
    print(f"總題目數: {summary.get('total_questions', 0)}")
    print(f"正確答案: {summary.get('correct_answers', 0)}")
    print(f"準確率: {summary.get('accuracy', 0):.1%}")
    
    # 按類別統計
    print(f"\\n📋 按類別詳細統計:")
    category_stats = summary.get("category_stats", {})
    for category, stats in category_stats.items():
        total = stats.get("total", 0)
        correct = stats.get("correct", 0)
        accuracy = stats.get("accuracy", 0)
        print(f"  {category:12}: {correct:2}/{total:2} ({accuracy:6.1%})")
    
    # 按適配器統計
    print(f"\\n🤖 按適配器統計:")
    adapter_stats = {}
    for result in detailed_results:
        adapter = result.get("adapter_used", "unknown")
        if adapter not in adapter_stats:
            adapter_stats[adapter] = {"total": 0, "correct": 0, "time": 0}
        
        adapter_stats[adapter]["total"] += 1
        if result.get("correct", False):
            adapter_stats[adapter]["correct"] += 1
        adapter_stats[adapter]["time"] += result.get("execution_time", 0)
    
    for adapter, stats in adapter_stats.items():
        total = stats["total"]
        correct = stats["correct"]
        accuracy = correct / total if total > 0 else 0
        avg_time = stats["time"] / total if total > 0 else 0
        print(f"  {adapter:12}: {correct:2}/{total:2} ({accuracy:6.1%}) - 平均{avg_time:.2f}秒")
    
    # 生成詳細表格
    print(f"\\n📄 生成詳細結果表格...")
    
    # 準備數據
    table_data = []
    for i, result in enumerate(detailed_results, 1):
        table_data.append({
            "序號": i,
            "題目ID": result.get("question_id", ""),
            "題目": result.get("question", "")[:50] + "..." if len(result.get("question", "")) > 50 else result.get("question", ""),
            "類別": result.get("category", ""),
            "難度": result.get("difficulty", ""),
            "預期答案": result.get("expected_answer", ""),
            "實際答案": result.get("actual_answer", "")[:50] + "..." if len(str(result.get("actual_answer", ""))) > 50 else str(result.get("actual_answer", "")),
            "正確性": "✅" if result.get("correct", False) else "❌",
            "使用適配器": result.get("adapter_used", ""),
            "執行時間(秒)": f"{result.get('execution_time', 0):.3f}",
            "錯誤信息": result.get("error", "") if result.get("error") else ""
        })
    
    # 創建DataFrame
    df = pd.DataFrame(table_data)
    
    # 保存為多種格式
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"gaia_level1_detailed_results_{timestamp}"
    
    # Excel格式
    excel_file = f"/home/ubuntu/Powerauto.ai/{base_name}.xlsx"
    df.to_excel(excel_file, index=False, sheet_name="GAIA_Level1_Results")
    
    # CSV格式
    csv_file = f"/home/ubuntu/Powerauto.ai/{base_name}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    # HTML格式（美化表格）
    html_file = f"/home/ubuntu/Powerauto.ai/{base_name}.html"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GAIA Level 1 測試結果</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; text-align: center; }}
            .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .correct {{ color: green; font-weight: bold; }}
            .incorrect {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>🎯 GAIA Level 1 測試結果詳細報告</h1>
        
        <div class="summary">
            <h2>📊 測試摘要</h2>
            <p><strong>總題目數:</strong> {summary.get('total_questions', 0)}</p>
            <p><strong>正確答案:</strong> {summary.get('correct_answers', 0)}</p>
            <p><strong>準確率:</strong> {summary.get('accuracy', 0):.1%}</p>
            <p><strong>測試時間:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        {df.to_html(escape=False, classes='table table-striped', table_id='results_table')}
        
        <script>
            // 為正確性列添加樣式
            document.querySelectorAll('td').forEach(cell => {{
                if (cell.textContent === '✅') {{
                    cell.className = 'correct';
                }} else if (cell.textContent === '❌') {{
                    cell.className = 'incorrect';
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 詳細結果已保存:")
    print(f"  📊 Excel: {excel_file}")
    print(f"  📄 CSV: {csv_file}")
    print(f"  🌐 HTML: {html_file}")
    
    # 顯示前10行作為預覽
    print(f"\\n📋 結果預覽 (前10題):")
    print(df.head(10).to_string(index=False))
    
    # 錯誤分析
    print(f"\\n❌ 錯誤題目分析:")
    incorrect_results = [r for r in detailed_results if not r.get("correct", False)]
    
    if incorrect_results:
        print(f"錯誤題目數: {len(incorrect_results)}")
        for result in incorrect_results[:5]:  # 顯示前5個錯誤
            print(f"  {result.get('question_id', '')}: {result.get('question', '')[:60]}...")
            print(f"    期望: {result.get('expected_answer', '')}")
            print(f"    實際: {result.get('actual_answer', '')}")
            print(f"    適配器: {result.get('adapter_used', '')}")
            print()
    else:
        print("🎉 沒有錯誤題目！")
    
    return {
        "excel_file": excel_file,
        "csv_file": csv_file, 
        "html_file": html_file,
        "summary": summary,
        "detailed_results": detailed_results
    }

if __name__ == "__main__":
    result_file = "/home/ubuntu/Powerauto.ai/gaia_test_results_robust_20250608_183110.json"
    analyze_gaia_results(result_file)

