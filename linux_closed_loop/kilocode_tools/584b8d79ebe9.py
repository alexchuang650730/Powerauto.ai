#!/usr/bin/env python3
"""
data_analyzer - 自動生成的數據分析工具
需求: 數據分析: 分析收入預測數據並生成趨勢報告
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(data_source: str, analysis_type: str = "descriptive") -> dict:
    """分析數據"""
    results = {
        "tool_name": "data_analyzer",
        "data_source": data_source,
        "analysis_type": analysis_type,
        "timestamp": datetime.now().isoformat(),
        "analysis_results": {},
        "success": False
    }
    
    try:
        # 加載數據
        if data_source.endswith('.csv'):
            df = pd.read_csv(data_source)
        elif data_source.endswith('.json'):
            df = pd.read_json(data_source)
        else:
            results["error"] = "不支持的數據格式"
            return results
        
        # 基本統計分析
        results["analysis_results"]["basic_stats"] = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        # 數值列統計
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            results["analysis_results"]["numeric_analysis"] = {
                "descriptive_stats": df[numeric_columns].describe().to_dict(),
                "correlation_matrix": df[numeric_columns].corr().to_dict()
            }
        
        # 分類列分析
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            results["analysis_results"]["categorical_analysis"] = {}
            for col in categorical_columns[:5]:  # 限制前5列
                results["analysis_results"]["categorical_analysis"][col] = {
                    "unique_count": df[col].nunique(),
                    "top_values": df[col].value_counts().head().to_dict()
                }
        
        results["success"] = True
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = analyze_data(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("使用方法: python {} <data_file>".format(sys.argv[0]))
