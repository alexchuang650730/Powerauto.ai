# PowerAutomation CLI工具快速參考

## 🚀 常用命令速查

### 主要CLI工具

| 工具 | 命令 | 功能 |
|------|------|------|
| **主CLI** | `python powerautomation_cli.py` | 統一入口 |
| **MCP管理** | `python mcptool/cli/enhanced_mcp_cli.py` | MCP適配器管理 |
| **GAIA測試** | `python real_api_gaia_tester.py` | AI能力測試 |
| **數據收集** | `python cli_data_collection_system.py` | 數據收集分析 |
| **上下文監控** | `python context_monitor_cli.py` | 上下文監控 |

### 快速命令

```bash
# 系統狀態檢查
python mcptool/cli/enhanced_mcp_cli.py --status

# 運行GAIA測試
python mcptool/cli/enhanced_mcp_cli.py --gaia --level 1 --max-tasks 5

# 查看適配器列表
python mcptool/cli/enhanced_mcp_cli.py --list

# 測試特定適配器
python mcptool/cli/enhanced_mcp_cli.py --test claude_mcp

# 上下文使用情況
python context_monitor_cli.py --status

# 生成數據分析報告
python cli_data_analysis_tools.py
```

## 📊 MCP管理命令

```bash
# 基本操作
--status                    # 查看系統狀態
--list                      # 列出所有適配器
--test ADAPTER             # 測試指定適配器
--test-all                 # 測試所有適配器

# GAIA測試
--gaia --level 1           # Level 1測試
--gaia --level 2           # Level 2測試
--gaia --level all         # 所有級別測試
--max-tasks N              # 限制測試題目數量

# 配置管理
--configure ADAPTER        # 配置適配器
--show-config ADAPTER      # 查看配置
--reset-config ADAPTER     # 重置配置

# 監控診斷
--health-check             # 健康檢查
--diagnose ADAPTER         # 診斷問題
--performance-report       # 性能報告
```

## 🧪 GAIA測試命令

```bash
# 基本測試
python real_api_gaia_tester.py --level 1 --max-tasks 5

# 高級選項
--model claude             # 指定AI模型
--model gemini            # 使用Gemini
--compare-models          # 模型對比
--timeout 120             # 設置超時
--verbose                 # 詳細輸出
--output FILE             # 保存結果
--performance-analysis    # 性能分析
```

## 📈 監控命令

```bash
# 上下文監控
python context_monitor_cli.py --status          # 當前狀態
python context_monitor_cli.py --monitor         # 實時監控
python context_monitor_cli.py --report          # 生成報告

# 系統監控
python mcptool/cli/enhanced_mcp_cli.py --health-check    # 健康檢查
python mcptool/cli/enhanced_mcp_cli.py --monitor ADAPTER # 監控適配器
```

## 🔧 配置命令

```bash
# API密鑰管理
python mcptool/cli/config_cli.py --set-api-key claude YOUR_KEY
python mcptool/cli/config_cli.py --list-api-keys
python mcptool/cli/config_cli.py --test-api-key claude

# 系統配置
python mcptool/cli/config_cli.py --show-config
python mcptool/cli/config_cli.py --set-default-model MODEL
python mcptool/cli/config_cli.py --reset-config
```

## 📊 數據分析命令

```python
# Python中使用
from cli_data_collection_system import get_cli_data_collector
from cli_data_analysis_tools import CLIDataAnalyzer

# 獲取統計
collector = get_cli_data_collector()
stats = collector.get_session_stats()

# 生成報告
analyzer = CLIDataAnalyzer()
report = analyzer.generate_comprehensive_report()
```

## 🚨 故障排除

```bash
# 常見問題檢查
python mcptool/cli/enhanced_mcp_cli.py --diagnose
python mcptool/cli/config_cli.py --check-dependencies
python context_monitor_cli.py --status

# 調試模式
python mcptool/cli/enhanced_mcp_cli.py --debug --test ADAPTER
export POWERAUTOMATION_LOG_LEVEL=DEBUG
```

## 💡 最佳實踐

### 每日檢查
```bash
# 1. 系統狀態
python mcptool/cli/enhanced_mcp_cli.py --status

# 2. 快速測試
python mcptool/cli/enhanced_mcp_cli.py --gaia --level 1 --max-tasks 3

# 3. 上下文檢查
python context_monitor_cli.py --status
```

### 性能監控
```bash
# 週期性基準測試
python mcptool/cli/enhanced_mcp_cli.py --benchmark --all-adapters

# 生成性能報告
python mcptool/cli/enhanced_mcp_cli.py --performance-report --period week
```

### 數據管理
```bash
# 定期數據分析
python cli_data_analysis_tools.py

# 清理和優化
python cli_data_collection_system.py --cleanup
```

---

**需要詳細說明？查看完整文檔：`doc/PowerAutomation_CLI_Complete_Guide.md`**

