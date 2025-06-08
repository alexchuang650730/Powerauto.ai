# PowerAutomation CLI數據收集系統 - 快速入門指南

## 🚀 5分鐘快速上手

### 1. 基本使用

```python
# 導入系統
from cli_data_collection_system import get_cli_data_collector
from cli_data_collection_system import ResultStatus

# 獲取收集器
collector = get_cli_data_collector()

# 開始記錄
interaction_id = collector.start_interaction(
    command="python your_script.py",
    arguments={"param": "value"},
    context={"purpose": "data_analysis"}
)

# 執行你的代碼...
# ...

# 結束記錄
collector.end_interaction(
    interaction_id=interaction_id,
    result_status=ResultStatus.SUCCESS_PERFECT,
    output_data={"result": "success"},
    execution_time=2.5,
    tools_used=["pandas", "numpy"],
    accuracy_score=0.95,
    user_satisfaction=5
)

print("✅ 數據記錄完成！")
```

### 2. 查看統計

```python
# 獲取會話統計
stats = collector.get_session_stats()
print(f"總交互數: {stats['total_interactions']}")
print(f"平均準確率: {stats['average_accuracy']:.2f}")
```

### 3. 生成分析報告

```python
from cli_data_analysis_tools import CLIDataAnalyzer

analyzer = CLIDataAnalyzer()
report = analyzer.generate_comprehensive_report()

print(f"數據質量分數: {report['quality_metrics']['overall_quality_score']:.3f}")
print(f"訓練準備度: {report['training_readiness']['readiness_level']}")
```

## 📊 數據分類說明

### 任務類型 (TaskType)
- `GAIA_TESTING` - GAIA測試任務
- `MCP_MANAGEMENT` - MCP管理操作
- `DATA_ANALYSIS` - 數據分析任務
- `CODE_GENERATION` - 代碼生成任務
- `SYSTEM_OPERATION` - 系統操作任務

### 執行結果 (ResultStatus)
- `SUCCESS_PERFECT` - 完美成功
- `SUCCESS_PARTIAL` - 部分成功
- `SUCCESS_ACCEPTABLE` - 可接受的成功
- `FAILURE_USER` - 用戶錯誤
- `FAILURE_SYSTEM` - 系統錯誤

### 學習價值 (LearningValue)
- `HIGH` - 高價值（用於優先訓練）
- `MEDIUM` - 中價值（適合訓練）
- `LOW` - 低價值（統計用途）
- `NEGATIVE` - 負價值（不建議使用）

## 🛡️ 隱私保護

系統自動進行以下保護：
- ✅ 用戶ID匿名化
- ✅ 敏感信息檢測和清理
- ✅ 環境信息過濾
- ✅ 數據加密存儲

## 📈 數據價值

您的每次CLI使用都在為社區創造價值：
- 🧠 **集體智慧** - 最佳實踐自動學習
- 🎯 **性能提升** - 系統準確率持續改進
- 🔧 **工具優化** - 自動選擇最佳工具組合
- 🚀 **創新發現** - 發現新的使用模式

## 🤝 社區貢獻

參與數據共享，您將獲得：
- 📊 更智能的系統推薦
- 🎁 貢獻積分獎勵
- 💰 改進收益分配
- 🏆 社區認可

## 📞 需要幫助？

- 📖 完整文檔: `doc/CLI_Data_Collection_Tutorial.md`
- 🐛 問題報告: GitHub Issues
- 💬 社區討論: 開發者論壇
- 📧 技術支持: 開發團隊郵箱

---

**開始使用，讓您的每次CLI操作都為AI的進步做出貢獻！** 🌟

