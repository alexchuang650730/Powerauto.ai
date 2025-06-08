#!/usr/bin/env python3
"""
CLI數據處理和分析工具
用於處理、分析和生成訓練數據集
"""

import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict, Counter
import logging

# 導入我們的數據結構
from cli_data_collection_system import (
    CLIInteractionData, TaskType, ComplexityLevel, 
    ResultStatus, LearningValue, CLIDataStorage
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLIDataAnalyzer:
    """CLI數據分析器"""
    
    def __init__(self, storage_dir: str = "/home/ubuntu/Powerauto.ai/cli_training_data"):
        self.storage = CLIDataStorage(storage_dir)
        self.storage_dir = Path(storage_dir)
        
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成綜合分析報告"""
        
        # 獲取所有數據
        all_interactions = self.storage.query_interactions()
        
        if not all_interactions:
            return {"error": "沒有找到任何交互數據"}
        
        report = {
            "overview": self._analyze_overview(all_interactions),
            "task_analysis": self._analyze_task_patterns(all_interactions),
            "performance_analysis": self._analyze_performance(all_interactions),
            "learning_value_analysis": self._analyze_learning_value(all_interactions),
            "tool_usage_analysis": self._analyze_tool_usage(all_interactions),
            "temporal_analysis": self._analyze_temporal_patterns(all_interactions),
            "quality_metrics": self._calculate_quality_metrics(all_interactions),
            "training_readiness": self._assess_training_readiness(all_interactions)
        }
        
        return report
    
    def _analyze_overview(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """分析概覽統計"""
        
        total_interactions = len(interactions)
        
        # 時間範圍
        timestamps = [i.timestamp for i in interactions]
        time_range = {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_days": (max(timestamps) - min(timestamps)).days
        }
        
        # 基本統計
        task_types = Counter(i.task_type.value for i in interactions)
        complexity_levels = Counter(i.complexity_level.value for i in interactions)
        result_statuses = Counter(i.result_status.value for i in interactions)
        learning_values = Counter(i.learning_value.value for i in interactions)
        
        return {
            "total_interactions": total_interactions,
            "time_range": time_range,
            "task_type_distribution": dict(task_types),
            "complexity_distribution": dict(complexity_levels),
            "result_status_distribution": dict(result_statuses),
            "learning_value_distribution": dict(learning_values)
        }
    
    def _analyze_task_patterns(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """分析任務模式"""
        
        patterns = {}
        
        # 按任務類型分組分析
        task_groups = defaultdict(list)
        for interaction in interactions:
            task_groups[interaction.task_type.value].append(interaction)
        
        for task_type, task_interactions in task_groups.items():
            # 成功率分析
            success_count = sum(1 for i in task_interactions 
                              if i.result_status in [ResultStatus.SUCCESS_PERFECT, 
                                                   ResultStatus.SUCCESS_PARTIAL,
                                                   ResultStatus.SUCCESS_ACCEPTABLE])
            success_rate = success_count / len(task_interactions)
            
            # 平均執行時間
            execution_times = [i.execution_time for i in task_interactions if i.execution_time > 0]
            avg_execution_time = np.mean(execution_times) if execution_times else 0
            
            # 平均準確率
            accuracy_scores = [i.accuracy_score for i in task_interactions if i.accuracy_score is not None]
            avg_accuracy = np.mean(accuracy_scores) if accuracy_scores else None
            
            # 複雜度分布
            complexity_dist = Counter(i.complexity_level.value for i in task_interactions)
            
            # 常用工具
            all_tools = []
            for i in task_interactions:
                all_tools.extend(i.tools_used)
            common_tools = Counter(all_tools).most_common(5)
            
            patterns[task_type] = {
                "total_interactions": len(task_interactions),
                "success_rate": success_rate,
                "average_execution_time": avg_execution_time,
                "average_accuracy": avg_accuracy,
                "complexity_distribution": dict(complexity_dist),
                "common_tools": dict(common_tools)
            }
        
        return patterns
    
    def _analyze_performance(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """分析性能指標"""
        
        # 準確率分析
        accuracy_scores = [i.accuracy_score for i in interactions if i.accuracy_score is not None]
        
        accuracy_stats = {}
        if accuracy_scores:
            accuracy_stats = {
                "mean": np.mean(accuracy_scores),
                "median": np.median(accuracy_scores),
                "std": np.std(accuracy_scores),
                "min": np.min(accuracy_scores),
                "max": np.max(accuracy_scores),
                "count": len(accuracy_scores)
            }
        
        # 執行時間分析
        execution_times = [i.execution_time for i in interactions if i.execution_time > 0]
        
        execution_stats = {}
        if execution_times:
            execution_stats = {
                "mean": np.mean(execution_times),
                "median": np.median(execution_times),
                "std": np.std(execution_times),
                "min": np.min(execution_times),
                "max": np.max(execution_times),
                "count": len(execution_times)
            }
        
        # 用戶滿意度分析
        satisfaction_scores = [i.user_satisfaction for i in interactions if i.user_satisfaction is not None]
        
        satisfaction_stats = {}
        if satisfaction_scores:
            satisfaction_stats = {
                "mean": np.mean(satisfaction_scores),
                "median": np.median(satisfaction_scores),
                "distribution": dict(Counter(satisfaction_scores)),
                "count": len(satisfaction_scores)
            }
        
        return {
            "accuracy_statistics": accuracy_stats,
            "execution_time_statistics": execution_stats,
            "user_satisfaction_statistics": satisfaction_stats
        }
    
    def _analyze_learning_value(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """分析學習價值"""
        
        # 按學習價值分組
        value_groups = defaultdict(list)
        for interaction in interactions:
            value_groups[interaction.learning_value.value].append(interaction)
        
        value_analysis = {}
        for value, value_interactions in value_groups.items():
            # 任務類型分布
            task_dist = Counter(i.task_type.value for i in value_interactions)
            
            # 複雜度分布
            complexity_dist = Counter(i.complexity_level.value for i in value_interactions)
            
            # 成功率
            success_count = sum(1 for i in value_interactions 
                              if i.result_status in [ResultStatus.SUCCESS_PERFECT, 
                                                   ResultStatus.SUCCESS_PARTIAL,
                                                   ResultStatus.SUCCESS_ACCEPTABLE])
            success_rate = success_count / len(value_interactions)
            
            value_analysis[value] = {
                "count": len(value_interactions),
                "percentage": len(value_interactions) / len(interactions) * 100,
                "task_distribution": dict(task_dist),
                "complexity_distribution": dict(complexity_dist),
                "success_rate": success_rate
            }
        
        return value_analysis
    
    def _analyze_tool_usage(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """分析工具使用模式"""
        
        # 工具使用統計
        tool_usage = defaultdict(int)
        tool_success = defaultdict(int)
        tool_accuracy = defaultdict(list)
        tool_execution_time = defaultdict(list)
        
        for interaction in interactions:
            is_success = interaction.result_status in [
                ResultStatus.SUCCESS_PERFECT, 
                ResultStatus.SUCCESS_PARTIAL,
                ResultStatus.SUCCESS_ACCEPTABLE
            ]
            
            for tool in interaction.tools_used:
                tool_usage[tool] += 1
                if is_success:
                    tool_success[tool] += 1
                
                if interaction.accuracy_score is not None:
                    tool_accuracy[tool].append(interaction.accuracy_score)
                
                if interaction.execution_time > 0:
                    tool_execution_time[tool].append(interaction.execution_time)
        
        # 計算工具統計
        tool_stats = {}
        for tool in tool_usage:
            success_rate = tool_success[tool] / tool_usage[tool] if tool_usage[tool] > 0 else 0
            avg_accuracy = np.mean(tool_accuracy[tool]) if tool_accuracy[tool] else None
            avg_execution_time = np.mean(tool_execution_time[tool]) if tool_execution_time[tool] else None
            
            tool_stats[tool] = {
                "usage_count": tool_usage[tool],
                "success_rate": success_rate,
                "average_accuracy": avg_accuracy,
                "average_execution_time": avg_execution_time
            }
        
        # 排序工具
        most_used = sorted(tool_stats.items(), key=lambda x: x[1]["usage_count"], reverse=True)[:10]
        most_successful = sorted(
            [(k, v) for k, v in tool_stats.items() if v["usage_count"] >= 2],
            key=lambda x: x[1]["success_rate"], 
            reverse=True
        )[:10]
        
        return {
            "tool_statistics": tool_stats,
            "most_used_tools": dict(most_used),
            "most_successful_tools": dict(most_successful),
            "total_unique_tools": len(tool_stats)
        }
    
    def _analyze_temporal_patterns(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """分析時間模式"""
        
        # 按小時分組
        hourly_usage = defaultdict(int)
        daily_usage = defaultdict(int)
        
        for interaction in interactions:
            hour = interaction.timestamp.hour
            date = interaction.timestamp.date()
            
            hourly_usage[hour] += 1
            daily_usage[str(date)] += 1
        
        # 計算趨勢
        sorted_daily = sorted(daily_usage.items())
        if len(sorted_daily) > 1:
            daily_trend = "increasing" if sorted_daily[-1][1] > sorted_daily[0][1] else "decreasing"
        else:
            daily_trend = "stable"
        
        return {
            "hourly_distribution": dict(hourly_usage),
            "daily_usage": dict(daily_usage),
            "usage_trend": daily_trend,
            "peak_hour": max(hourly_usage, key=hourly_usage.get) if hourly_usage else None
        }
    
    def _calculate_quality_metrics(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """計算數據質量指標"""
        
        total = len(interactions)
        
        # 完整性檢查
        complete_accuracy = sum(1 for i in interactions if i.accuracy_score is not None)
        complete_satisfaction = sum(1 for i in interactions if i.user_satisfaction is not None)
        complete_tools = sum(1 for i in interactions if i.tools_used)
        complete_execution_time = sum(1 for i in interactions if i.execution_time > 0)
        
        # 一致性檢查
        consistent_results = sum(1 for i in interactions 
                               if (i.result_status in [ResultStatus.SUCCESS_PERFECT, 
                                                     ResultStatus.SUCCESS_PARTIAL,
                                                     ResultStatus.SUCCESS_ACCEPTABLE] 
                                   and (i.accuracy_score is None or i.accuracy_score > 0)))
        
        return {
            "completeness": {
                "accuracy_score": complete_accuracy / total,
                "user_satisfaction": complete_satisfaction / total,
                "tools_used": complete_tools / total,
                "execution_time": complete_execution_time / total
            },
            "consistency": {
                "result_accuracy_alignment": consistent_results / total
            },
            "overall_quality_score": (
                (complete_accuracy + complete_satisfaction + complete_tools + complete_execution_time) 
                / (4 * total)
            )
        }
    
    def _assess_training_readiness(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """評估訓練準備度"""
        
        # 高價值數據統計
        high_value_count = sum(1 for i in interactions if i.learning_value == LearningValue.HIGH)
        medium_value_count = sum(1 for i in interactions if i.learning_value == LearningValue.MEDIUM)
        
        # 任務類型平衡性
        task_counts = Counter(i.task_type.value for i in interactions)
        task_balance_score = 1.0 - (np.std(list(task_counts.values())) / np.mean(list(task_counts.values())))
        
        # 複雜度平衡性
        complexity_counts = Counter(i.complexity_level.value for i in interactions)
        complexity_balance_score = 1.0 - (np.std(list(complexity_counts.values())) / np.mean(list(complexity_counts.values())))
        
        # 成功案例比例
        success_count = sum(1 for i in interactions 
                          if i.result_status in [ResultStatus.SUCCESS_PERFECT, 
                                               ResultStatus.SUCCESS_PARTIAL,
                                               ResultStatus.SUCCESS_ACCEPTABLE])
        success_ratio = success_count / len(interactions)
        
        # 訓練準備度評分
        readiness_score = (
            min(high_value_count / 50, 1.0) * 0.3 +  # 高價值數據充足性
            min(medium_value_count / 100, 1.0) * 0.2 +  # 中價值數據充足性
            task_balance_score * 0.2 +  # 任務類型平衡性
            complexity_balance_score * 0.1 +  # 複雜度平衡性
            min(success_ratio / 0.7, 1.0) * 0.2  # 成功案例比例
        )
        
        return {
            "high_value_samples": high_value_count,
            "medium_value_samples": medium_value_count,
            "task_balance_score": task_balance_score,
            "complexity_balance_score": complexity_balance_score,
            "success_ratio": success_ratio,
            "overall_readiness_score": readiness_score,
            "readiness_level": self._get_readiness_level(readiness_score),
            "recommendations": self._get_training_recommendations(readiness_score, interactions)
        }
    
    def _get_readiness_level(self, score: float) -> str:
        """獲取準備度等級"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _get_training_recommendations(self, score: float, interactions: List[CLIInteractionData]) -> List[str]:
        """獲取訓練建議"""
        recommendations = []
        
        if score < 0.8:
            # 檢查具體問題
            high_value_count = sum(1 for i in interactions if i.learning_value == LearningValue.HIGH)
            if high_value_count < 50:
                recommendations.append(f"需要更多高價值數據樣本（當前：{high_value_count}，建議：50+）")
            
            task_counts = Counter(i.task_type.value for i in interactions)
            min_task_count = min(task_counts.values())
            if min_task_count < 10:
                recommendations.append(f"某些任務類型數據不足（最少：{min_task_count}，建議：10+）")
            
            success_count = sum(1 for i in interactions 
                              if i.result_status in [ResultStatus.SUCCESS_PERFECT, 
                                                   ResultStatus.SUCCESS_PARTIAL,
                                                   ResultStatus.SUCCESS_ACCEPTABLE])
            success_ratio = success_count / len(interactions)
            if success_ratio < 0.7:
                recommendations.append(f"成功案例比例偏低（當前：{success_ratio:.2f}，建議：0.7+）")
        
        if not recommendations:
            recommendations.append("數據質量良好，可以開始訓練")
        
        return recommendations

class CLITrainingDataBuilder:
    """CLI訓練數據構建器"""
    
    def __init__(self, storage_dir: str = "/home/ubuntu/Powerauto.ai/cli_training_data"):
        self.storage = CLIDataStorage(storage_dir)
        self.storage_dir = Path(storage_dir)
        self.training_sets_dir = self.storage_dir / "training_sets"
        
    def build_gaia_optimization_dataset(self) -> Dict[str, Any]:
        """構建GAIA優化訓練集"""
        
        # 查詢GAIA相關的高價值交互
        gaia_interactions = self.storage.query_interactions(
            task_type=TaskType.GAIA_TESTING
        )
        
        if not gaia_interactions:
            return {"error": "沒有找到GAIA測試數據"}
        
        # 過濾高價值數據
        high_value_interactions = [
            i for i in gaia_interactions 
            if i.learning_value in [LearningValue.HIGH, LearningValue.MEDIUM]
            and i.result_status in [ResultStatus.SUCCESS_PERFECT, ResultStatus.SUCCESS_PARTIAL]
        ]
        
        # 構建訓練樣本
        training_samples = []
        for interaction in high_value_interactions:
            sample = {
                "input": {
                    "task_type": interaction.task_type.value,
                    "complexity": interaction.complexity_level.value,
                    "command": interaction.command,
                    "arguments": interaction.arguments,
                    "context": interaction.context
                },
                "optimal_strategy": {
                    "tools": interaction.tools_used,
                    "mcp_adapters": interaction.mcp_adapters_involved,
                    "execution_sequence": self._extract_execution_sequence(interaction)
                },
                "expected_outcome": {
                    "accuracy": interaction.accuracy_score,
                    "execution_time": interaction.execution_time,
                    "success_probability": self._calculate_success_probability(interaction)
                },
                "metadata": {
                    "interaction_id": interaction.interaction_id,
                    "timestamp": interaction.timestamp.isoformat(),
                    "learning_value": interaction.learning_value.value
                }
            }
            training_samples.append(sample)
        
        dataset = {
            "dataset_name": "gaia_optimization",
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "samples": training_samples,
            "metadata": {
                "total_samples": len(training_samples),
                "source_interactions": len(gaia_interactions),
                "quality_score": self._calculate_dataset_quality(training_samples)
            }
        }
        
        # 保存數據集
        output_path = self.training_sets_dir / "gaia_optimization_dataset.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"GAIA優化數據集已保存到: {output_path}")
        
        return dataset
    
    def build_tool_selection_dataset(self) -> Dict[str, Any]:
        """構建工具選擇訓練集"""
        
        # 獲取所有成功的交互
        successful_interactions = self.storage.query_interactions(
            result_status=[ResultStatus.SUCCESS_PERFECT, ResultStatus.SUCCESS_PARTIAL]
        )
        
        if not successful_interactions:
            return {"error": "沒有找到成功的交互數據"}
        
        # 分析工具選擇模式
        tool_patterns = self._analyze_tool_selection_patterns(successful_interactions)
        
        # 構建工具選擇樣本
        selection_samples = []
        for pattern in tool_patterns:
            sample = {
                "task_description": {
                    "task_type": pattern["task_type"],
                    "complexity": pattern["complexity"],
                    "context_features": pattern["context_features"]
                },
                "available_tools": pattern["available_tools"],
                "optimal_selection": {
                    "selected_tools": pattern["best_tools"],
                    "selection_rationale": pattern["rationale"],
                    "expected_performance": pattern["performance"]
                },
                "alternatives": pattern["alternatives"]
            }
            selection_samples.append(sample)
        
        dataset = {
            "dataset_name": "tool_selection",
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "samples": selection_samples,
            "metadata": {
                "total_samples": len(selection_samples),
                "pattern_count": len(tool_patterns)
            }
        }
        
        # 保存數據集
        output_path = self.training_sets_dir / "tool_selection_dataset.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"工具選擇數據集已保存到: {output_path}")
        
        return dataset
    
    def build_error_prevention_dataset(self) -> Dict[str, Any]:
        """構建錯誤預防訓練集"""
        
        # 獲取失敗的交互
        failed_interactions = self.storage.query_interactions(
            result_status=[ResultStatus.FAILURE_USER, ResultStatus.FAILURE_SYSTEM, 
                          ResultStatus.FAILURE_CONFIG, ResultStatus.FAILURE_RESOURCE]
        )
        
        if not failed_interactions:
            return {"error": "沒有找到失敗的交互數據"}
        
        # 構建錯誤預防樣本
        error_samples = []
        for interaction in failed_interactions:
            sample = {
                "input_context": {
                    "command": interaction.command,
                    "arguments": interaction.arguments,
                    "context": interaction.context,
                    "task_type": interaction.task_type.value,
                    "complexity": interaction.complexity_level.value
                },
                "error_info": {
                    "error_type": interaction.result_status.value,
                    "error_details": interaction.error_info,
                    "tools_attempted": interaction.tools_used
                },
                "prevention_strategy": {
                    "validation_checks": self._suggest_validation_checks(interaction),
                    "alternative_approaches": self._suggest_alternatives(interaction),
                    "risk_factors": self._identify_risk_factors(interaction)
                }
            }
            error_samples.append(sample)
        
        dataset = {
            "dataset_name": "error_prevention",
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "samples": error_samples,
            "metadata": {
                "total_samples": len(error_samples),
                "error_types": list(set(i.result_status.value for i in failed_interactions))
            }
        }
        
        # 保存數據集
        output_path = self.training_sets_dir / "error_prevention_dataset.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"錯誤預防數據集已保存到: {output_path}")
        
        return dataset
    
    def _extract_execution_sequence(self, interaction: CLIInteractionData) -> List[str]:
        """提取執行序列"""
        # 這裡可以根據實際情況提取工具的執行順序
        return interaction.tools_used
    
    def _calculate_success_probability(self, interaction: CLIInteractionData) -> float:
        """計算成功概率"""
        # 基於歷史數據計算類似任務的成功概率
        base_prob = 0.7  # 基礎概率
        
        if interaction.accuracy_score:
            base_prob = interaction.accuracy_score
        
        # 根據複雜度調整
        complexity_adjustment = {
            ComplexityLevel.SIMPLE: 0.1,
            ComplexityLevel.MODERATE: 0.0,
            ComplexityLevel.COMPLEX: -0.1,
            ComplexityLevel.EXPERT: -0.2
        }
        
        adjusted_prob = base_prob + complexity_adjustment.get(interaction.complexity_level, 0)
        return max(0.0, min(1.0, adjusted_prob))
    
    def _calculate_dataset_quality(self, samples: List[Dict[str, Any]]) -> float:
        """計算數據集質量分數"""
        if not samples:
            return 0.0
        
        # 基於樣本數量、多樣性等因素計算質量分數
        sample_count_score = min(len(samples) / 100, 1.0)  # 100個樣本為滿分
        
        # 可以添加更多質量指標
        return sample_count_score
    
    def _analyze_tool_selection_patterns(self, interactions: List[CLIInteractionData]) -> List[Dict[str, Any]]:
        """分析工具選擇模式"""
        
        patterns = []
        
        # 按任務類型和複雜度分組
        groups = defaultdict(list)
        for interaction in interactions:
            key = (interaction.task_type.value, interaction.complexity_level.value)
            groups[key].append(interaction)
        
        for (task_type, complexity), group_interactions in groups.items():
            if len(group_interactions) < 2:  # 至少需要2個樣本
                continue
            
            # 分析最常用的工具組合
            tool_combinations = Counter(tuple(sorted(i.tools_used)) for i in group_interactions)
            most_common_tools = tool_combinations.most_common(1)[0][0] if tool_combinations else []
            
            # 計算性能指標
            avg_accuracy = np.mean([i.accuracy_score for i in group_interactions 
                                  if i.accuracy_score is not None])
            avg_execution_time = np.mean([i.execution_time for i in group_interactions 
                                        if i.execution_time > 0])
            
            pattern = {
                "task_type": task_type,
                "complexity": complexity,
                "context_features": self._extract_context_features(group_interactions),
                "available_tools": list(set(tool for i in group_interactions for tool in i.tools_used)),
                "best_tools": list(most_common_tools),
                "rationale": f"最常用組合，平均準確率: {avg_accuracy:.2f}",
                "performance": {
                    "accuracy": avg_accuracy,
                    "execution_time": avg_execution_time
                },
                "alternatives": []  # 可以添加其他工具組合
            }
            patterns.append(pattern)
        
        return patterns
    
    def _extract_context_features(self, interactions: List[CLIInteractionData]) -> Dict[str, Any]:
        """提取上下文特徵"""
        
        # 分析常見的上下文特徵
        all_contexts = [i.context for i in interactions if i.context]
        
        if not all_contexts:
            return {}
        
        # 提取常見的鍵值對
        common_features = {}
        for context in all_contexts:
            for key, value in context.items():
                if key not in common_features:
                    common_features[key] = []
                common_features[key].append(value)
        
        # 計算最常見的值
        feature_summary = {}
        for key, values in common_features.items():
            if len(set(values)) == 1:
                feature_summary[key] = values[0]
            else:
                feature_summary[key] = Counter(values).most_common(1)[0][0]
        
        return feature_summary
    
    def _suggest_validation_checks(self, interaction: CLIInteractionData) -> List[str]:
        """建議驗證檢查"""
        checks = []
        
        if interaction.result_status == ResultStatus.FAILURE_USER:
            checks.append("輸入參數驗證")
            checks.append("命令格式檢查")
        elif interaction.result_status == ResultStatus.FAILURE_SYSTEM:
            checks.append("系統資源檢查")
            checks.append("依賴項驗證")
        elif interaction.result_status == ResultStatus.FAILURE_CONFIG:
            checks.append("配置文件驗證")
            checks.append("環境變量檢查")
        
        return checks
    
    def _suggest_alternatives(self, interaction: CLIInteractionData) -> List[str]:
        """建議替代方案"""
        alternatives = []
        
        # 基於失敗的工具建議替代工具
        for tool in interaction.tools_used:
            if "claude" in tool.lower():
                alternatives.append("嘗試使用gemini_mcp")
            elif "gemini" in tool.lower():
                alternatives.append("嘗試使用claude_mcp")
        
        return alternatives
    
    def _identify_risk_factors(self, interaction: CLIInteractionData) -> List[str]:
        """識別風險因素"""
        risks = []
        
        if interaction.complexity_level == ComplexityLevel.EXPERT:
            risks.append("高複雜度任務")
        
        if interaction.execution_time > 60:
            risks.append("長時間執行")
        
        if len(interaction.tools_used) > 5:
            risks.append("使用過多工具")
        
        return risks

def main():
    """主函數 - 演示數據分析和處理功能"""
    
    print("🔍 CLI數據處理和分析工具")
    print("=" * 40)
    
    # 初始化分析器
    analyzer = CLIDataAnalyzer()
    
    # 生成綜合報告
    print("📊 生成綜合分析報告...")
    report = analyzer.generate_comprehensive_report()
    
    if "error" in report:
        print(f"❌ {report['error']}")
        return
    
    # 顯示概覽
    overview = report["overview"]
    print(f"\n📈 數據概覽:")
    print(f"   總交互數: {overview['total_interactions']}")
    print(f"   時間範圍: {overview['time_range']['duration_days']}天")
    print(f"   任務類型: {list(overview['task_type_distribution'].keys())}")
    
    # 顯示性能分析
    performance = report["performance_analysis"]
    if performance["accuracy_statistics"]:
        acc_stats = performance["accuracy_statistics"]
        print(f"\n🎯 準確率統計:")
        print(f"   平均準確率: {acc_stats['mean']:.3f}")
        print(f"   準確率範圍: {acc_stats['min']:.3f} - {acc_stats['max']:.3f}")
    
    # 顯示訓練準備度
    readiness = report["training_readiness"]
    print(f"\n🚀 訓練準備度:")
    print(f"   準備度等級: {readiness['readiness_level']}")
    print(f"   準備度分數: {readiness['overall_readiness_score']:.3f}")
    print(f"   高價值樣本: {readiness['high_value_samples']}")
    
    # 保存報告
    report_path = "/home/ubuntu/Powerauto.ai/cli_training_data/metadata/analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 分析報告已保存到: {report_path}")
    
    # 構建訓練數據集
    print("\n🏗️ 構建訓練數據集...")
    builder = CLITrainingDataBuilder()
    
    # 構建GAIA優化數據集
    gaia_dataset = builder.build_gaia_optimization_dataset()
    if "error" not in gaia_dataset:
        print(f"   ✅ GAIA優化數據集: {gaia_dataset['metadata']['total_samples']}個樣本")
    
    # 構建工具選擇數據集
    tool_dataset = builder.build_tool_selection_dataset()
    if "error" not in tool_dataset:
        print(f"   ✅ 工具選擇數據集: {tool_dataset['metadata']['total_samples']}個樣本")
    
    # 構建錯誤預防數據集
    error_dataset = builder.build_error_prevention_dataset()
    if "error" not in error_dataset:
        print(f"   ✅ 錯誤預防數據集: {error_dataset['metadata']['total_samples']}個樣本")
    
    print("\n🎉 數據處理和分析完成!")

if __name__ == "__main__":
    main()

