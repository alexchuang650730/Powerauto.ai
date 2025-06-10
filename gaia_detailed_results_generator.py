#!/usr/bin/env python3
"""
GAIA測試詳細結果表格生成器

生成包含題目、預期答案、真實答案、解決工具、所花時間的詳細表格
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import os

class GAIADetailedResultsGenerator:
    """GAIA詳細結果表格生成器"""
    
    def __init__(self):
        self.results_data = []
    
    def process_test_results(self, results_file: str) -> pd.DataFrame:
        """處理測試結果並生成詳細表格"""
        
        # 載入測試結果
        with open(results_file, 'r', encoding='utf-8') as f:
            test_results = json.load(f)
        
        detailed_results = test_results.get("detailed_results", [])
        
        # 處理每個結果
        table_data = []
        
        for i, result in enumerate(detailed_results, 1):
            row = {
                "序號": i,
                "題目ID": result.get("question_id", f"question_{i}"),
                "題目": result.get("question", "N/A"),
                "類別": result.get("category", "unknown"),
                "難度": result.get("difficulty", "unknown"),
                "預期答案": result.get("expected_answer", "N/A"),
                "真實答案": result.get("actual_answer", "N/A"),
                "是否正確": "✅" if result.get("correct", False) else "❌",
                "使用適配器": result.get("adapter_used", "unknown"),
                "適配器類型": self._get_adapter_type(result.get("adapter_used", "")),
                "執行時間(秒)": round(result.get("execution_time", 0), 3),
                "成功狀態": "成功" if result.get("success", False) else "失敗",
                "錯誤信息": result.get("error", "") if not result.get("success", False) else "",
                "置信度": self._extract_confidence(result),
                "響應長度": len(str(result.get("actual_answer", ""))) if result.get("actual_answer") else 0,
                "處理層級": self._determine_processing_layer(result.get("adapter_used", "")),
                "工具分類": self._classify_tool(result.get("adapter_used", ""))
            }
            
            table_data.append(row)
        
        # 創建DataFrame
        df = pd.DataFrame(table_data)
        
        return df
    
    def _get_adapter_type(self, adapter_name: str) -> str:
        """獲取適配器類型"""
        adapter_types = {
            "claude": "AI模型",
            "gemini": "AI模型", 
            "smart_tool_engine": "工具引擎",
            "webagent": "Web代理",
            "unified_memory": "記憶系統",
            "context_monitor": "監控系統",
            "sequential_thinking": "推理引擎",
            "kilocode": "代碼引擎",
            "cloud_edge_data": "數據處理"
        }
        
        for key, value in adapter_types.items():
            if key in adapter_name.lower():
                return value
        
        return "通用適配器"
    
    def _extract_confidence(self, result: Dict[str, Any]) -> float:
        """提取置信度"""
        # 嘗試從原始響應中提取置信度
        raw_response = result.get("raw_response", {})
        if isinstance(raw_response, dict):
            confidence = raw_response.get("confidence", 0.0)
            if isinstance(confidence, (int, float)):
                return round(confidence, 3)
        
        # 根據執行時間和成功狀態估算置信度
        if result.get("correct", False):
            execution_time = result.get("execution_time", 0)
            if execution_time < 1.0:
                return 0.95
            elif execution_time < 3.0:
                return 0.90
            else:
                return 0.85
        else:
            return 0.30
    
    def _determine_processing_layer(self, adapter_name: str) -> str:
        """確定處理層級"""
        layer_mapping = {
            "claude": "LLM層",
            "gemini": "LLM層",
            "smart_tool_engine": "工具層",
            "webagent": "應用層",
            "unified_memory": "數據層",
            "context_monitor": "監控層",
            "sequential_thinking": "推理層",
            "kilocode": "執行層",
            "cloud_edge_data": "基礎設施層"
        }
        
        for key, value in layer_mapping.items():
            if key in adapter_name.lower():
                return value
        
        return "未知層"
    
    def _classify_tool(self, adapter_name: str) -> str:
        """工具分類"""
        tool_classification = {
            "claude": "語言模型",
            "gemini": "語言模型",
            "smart_tool_engine": "智能工具",
            "webagent": "網絡工具",
            "unified_memory": "存儲工具",
            "context_monitor": "監控工具",
            "sequential_thinking": "推理工具",
            "kilocode": "編程工具",
            "cloud_edge_data": "數據工具"
        }
        
        for key, value in tool_classification.items():
            if key in adapter_name.lower():
                return value
        
        return "通用工具"
    
    def generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成摘要統計"""
        total_questions = len(df)
        correct_answers = len(df[df["是否正確"] == "✅"])
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        # 按類別統計
        category_stats = df.groupby("類別").agg({
            "是否正確": lambda x: (x == "✅").sum(),
            "序號": "count",
            "執行時間(秒)": "mean"
        }).rename(columns={"是否正確": "正確數", "序號": "總數", "執行時間(秒)": "平均時間"})
        category_stats["準確率"] = category_stats["正確數"] / category_stats["總數"]
        
        # 按適配器統計
        adapter_stats = df.groupby("使用適配器").agg({
            "是否正確": lambda x: (x == "✅").sum(),
            "序號": "count",
            "執行時間(秒)": "mean"
        }).rename(columns={"是否正確": "正確數", "序號": "總數", "執行時間(秒)": "平均時間"})
        adapter_stats["準確率"] = adapter_stats["正確數"] / adapter_stats["總數"]
        
        # 按難度統計
        difficulty_stats = df.groupby("難度").agg({
            "是否正確": lambda x: (x == "✅").sum(),
            "序號": "count",
            "執行時間(秒)": "mean"
        }).rename(columns={"是否正確": "正確數", "序號": "總數", "執行時間(秒)": "平均時間"})
        difficulty_stats["準確率"] = difficulty_stats["正確數"] / difficulty_stats["總數"]
        
        # 按處理層級統計
        layer_stats = df.groupby("處理層級").agg({
            "是否正確": lambda x: (x == "✅").sum(),
            "序號": "count",
            "執行時間(秒)": "mean"
        }).rename(columns={"是否正確": "正確數", "序號": "總數", "執行時間(秒)": "平均時間"})
        layer_stats["準確率"] = layer_stats["正確數"] / layer_stats["總數"]
        
        return {
            "總體統計": {
                "總題目數": total_questions,
                "正確答案數": correct_answers,
                "總體準確率": round(accuracy, 4),
                "平均執行時間": round(df["執行時間(秒)"].mean(), 3),
                "總執行時間": round(df["執行時間(秒)"].sum(), 3)
            },
            "按類別統計": category_stats.round(4).to_dict(),
            "按適配器統計": adapter_stats.round(4).to_dict(),
            "按難度統計": difficulty_stats.round(4).to_dict(),
            "按處理層級統計": layer_stats.round(4).to_dict()
        }
    
    def save_detailed_results(self, df: pd.DataFrame, stats: Dict[str, Any], 
                            base_filename: str = None) -> Dict[str, str]:
        """保存詳細結果到多種格式"""
        
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"/home/ubuntu/Powerauto.ai/gaia_level1_detailed_results_{timestamp}"
        
        saved_files = {}
        
        try:
            # 保存為Excel文件（包含多個工作表）
            excel_file = f"{base_filename}.xlsx"
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # 主結果表
                df.to_excel(writer, sheet_name='詳細結果', index=False)
                
                # 統計表
                for stat_name, stat_data in stats.items():
                    if isinstance(stat_data, dict) and stat_name != "總體統計":
                        stat_df = pd.DataFrame(stat_data).T
                        sheet_name = stat_name.replace("統計", "")[:31]  # Excel工作表名稱限制
                        stat_df.to_excel(writer, sheet_name=sheet_name)
                
                # 總體統計
                overall_stats = pd.DataFrame([stats["總體統計"]])
                overall_stats.to_excel(writer, sheet_name='總體統計', index=False)
            
            saved_files["excel"] = excel_file
            
            # 保存為CSV文件
            csv_file = f"{base_filename}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            saved_files["csv"] = csv_file
            
            # 保存為JSON文件
            json_file = f"{base_filename}.json"
            result_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_questions": len(df),
                    "data_source": "GAIA Level 1 Complete Test"
                },
                "statistics": stats,
                "detailed_results": df.to_dict('records')
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            saved_files["json"] = json_file
            
            # 保存為HTML表格
            html_file = f"{base_filename}.html"
            html_content = self._generate_html_report(df, stats)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            saved_files["html"] = html_file
            
            print(f"✅ 詳細結果已保存到:")
            for format_type, file_path in saved_files.items():
                print(f"  {format_type.upper()}: {file_path}")
            
        except Exception as e:
            print(f"❌ 保存結果時發生錯誤: {e}")
        
        return saved_files
    
    def _generate_html_report(self, df: pd.DataFrame, stats: Dict[str, Any]) -> str:
        """生成HTML報告"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GAIA Level 1 詳細測試結果</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .correct {{ color: green; font-weight: bold; }}
        .incorrect {{ color: red; font-weight: bold; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .summary-card {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; }}
        .summary-card h3 {{ margin-top: 0; color: #333; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 GAIA Level 1 完整測試結果報告</h1>
        <p><strong>生成時間:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>測試題目:</strong> {len(df)} 題</p>
        <p><strong>總體準確率:</strong> {stats['總體統計']['總體準確率']:.1%}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>📊 總體統計</h3>
            <p><strong>總題目數:</strong> {stats['總體統計']['總題目數']}</p>
            <p><strong>正確答案數:</strong> {stats['總體統計']['正確答案數']}</p>
            <p><strong>準確率:</strong> {stats['總體統計']['總體準確率']:.1%}</p>
            <p><strong>平均執行時間:</strong> {stats['總體統計']['平均執行時間']:.3f}秒</p>
            <p><strong>總執行時間:</strong> {stats['總體統計']['總執行時間']:.3f}秒</p>
        </div>
    </div>
    
    <h2>📋 詳細測試結果</h2>
    {df.to_html(classes='table table-striped', escape=False, index=False)}
    
</body>
</html>
        """
        
        return html_template
    
    def print_summary(self, stats: Dict[str, Any]):
        """打印摘要統計"""
        print("\\n📊 GAIA Level 1 完整測試摘要")
        print("=" * 50)
        
        overall = stats["總體統計"]
        print(f"總題目數: {overall['總題目數']}")
        print(f"正確答案數: {overall['正確答案數']}")
        print(f"總體準確率: {overall['總體準確率']:.1%}")
        print(f"平均執行時間: {overall['平均執行時間']:.3f}秒")
        print(f"總執行時間: {overall['總執行時間']:.3f}秒")
        
        print("\\n📋 按類別統計:")
        for category, data in stats["按類別統計"].items():
            if isinstance(data, dict):
                correct = data.get('正確數', 0)
                total = data.get('總數', 0) 
                accuracy = data.get('準確率', 0)
                avg_time = data.get('平均時間', 0)
                print(f"  {category}: {correct}/{total} ({accuracy:.1%}) - 平均{avg_time:.2f}秒")
        
        print("\\n🤖 按適配器統計:")
        for adapter, data in stats["按適配器統計"].items():
            if isinstance(data, dict):
                correct = data.get('正確數', 0)
                total = data.get('總數', 0)
                accuracy = data.get('準確率', 0)
                avg_time = data.get('平均時間', 0)
                print(f"  {adapter}: {correct}/{total} ({accuracy:.1%}) - 平均{avg_time:.2f}秒")
        
        print("\\n🎯 按難度統計:")
        for difficulty, data in stats["按難度統計"].items():
            if isinstance(data, dict):
                correct = data.get('正確數', 0)
                total = data.get('總數', 0)
                accuracy = data.get('準確率', 0)
                avg_time = data.get('平均時間', 0)
                print(f"  {difficulty}: {correct}/{total} ({accuracy:.1%}) - 平均{avg_time:.2f}秒")

# 測試腳本
if __name__ == "__main__":
    print("📊 GAIA詳細結果表格生成器測試")
    
    # 創建生成器
    generator = GAIADetailedResultsGenerator()
    
    # 模擬測試結果數據
    sample_results = {
        "summary": {
            "total_questions": 5,
            "correct_answers": 4,
            "accuracy": 0.8
        },
        "detailed_results": [
            {
                "question_id": "gaia_001",
                "question": "What is the capital of France?",
                "expected_answer": "Paris",
                "actual_answer": "Paris",
                "correct": True,
                "adapter_used": "claude",
                "execution_time": 1.234,
                "success": True,
                "category": "geography",
                "difficulty": "easy"
            },
            {
                "question_id": "gaia_002",
                "question": "What is 15 + 27?",
                "expected_answer": "42",
                "actual_answer": "42",
                "correct": True,
                "adapter_used": "gemini",
                "execution_time": 0.856,
                "success": True,
                "category": "math",
                "difficulty": "easy"
            }
        ]
    }
    
    # 保存樣本數據
    sample_file = "/home/ubuntu/Powerauto.ai/sample_test_results.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_results, f, indent=2, ensure_ascii=False)
    
    # 處理結果
    df = generator.process_test_results(sample_file)
    stats = generator.generate_summary_statistics(df)
    
    # 打印摘要
    generator.print_summary(stats)
    
    # 保存結果
    saved_files = generator.save_detailed_results(df, stats, "/home/ubuntu/Powerauto.ai/sample_detailed_results")
    
    print("\\n🎯 詳細結果表格生成器測試完成")

