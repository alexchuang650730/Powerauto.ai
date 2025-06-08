# CLI數據分類和存儲系統設計

## 📋 基於對話數據分類的CLI數據架構

### 🎯 設計原則

參考之前的對話數據分類方案，CLI數據分類需要考慮：
1. **任務類型分類** - 不同類型的CLI任務
2. **交互模式分類** - 用戶與CLI的交互方式
3. **結果質量分類** - 執行結果的質量評估
4. **學習價值分類** - 對訓練的價值程度

---

## 🏗️ CLI數據分類架構

### 1. 主要分類維度

#### A. 任務類型分類 (Task Type Classification)
```json
{
  "task_categories": {
    "gaia_testing": {
      "description": "GAIA基準測試相關任務",
      "subcategories": ["level1", "level2", "level3", "validation", "analysis"]
    },
    "mcp_management": {
      "description": "MCP適配器管理任務", 
      "subcategories": ["list", "load", "test", "configure", "debug"]
    },
    "data_analysis": {
      "description": "數據分析和處理任務",
      "subcategories": ["file_analysis", "statistical_analysis", "visualization", "reporting"]
    },
    "code_generation": {
      "description": "代碼生成和執行任務",
      "subcategories": ["script_generation", "debugging", "optimization", "testing"]
    },
    "system_operation": {
      "description": "系統操作和維護任務",
      "subcategories": ["status_check", "configuration", "monitoring", "troubleshooting"]
    }
  }
}
```

#### B. 交互複雜度分類 (Interaction Complexity)
```json
{
  "complexity_levels": {
    "simple": {
      "description": "單一命令，直接結果",
      "examples": ["--status", "--list", "--help"],
      "training_value": "low"
    },
    "moderate": {
      "description": "多參數命令，需要處理",
      "examples": ["--gaia --level 1 --max-tasks 5"],
      "training_value": "medium"
    },
    "complex": {
      "description": "多步驟交互，複雜邏輯",
      "examples": ["interactive debugging", "multi-tool coordination"],
      "training_value": "high"
    },
    "expert": {
      "description": "高級配置，專家級操作",
      "examples": ["custom adapter creation", "system optimization"],
      "training_value": "very_high"
    }
  }
}
```

#### C. 執行結果分類 (Execution Result Classification)
```json
{
  "result_categories": {
    "success": {
      "perfect": "完全成功，結果準確",
      "partial": "部分成功，有改進空間",
      "acceptable": "可接受的結果，但不完美"
    },
    "failure": {
      "user_error": "用戶輸入錯誤",
      "system_error": "系統內部錯誤", 
      "configuration_error": "配置問題",
      "resource_error": "資源不足"
    },
    "learning_opportunity": {
      "novel_pattern": "新的使用模式",
      "edge_case": "邊界情況",
      "optimization_potential": "優化潛力",
      "feature_request": "功能需求"
    }
  }
}
```

#### D. 學習價值分類 (Learning Value Classification)
```json
{
  "learning_value": {
    "high_value": {
      "criteria": ["novel solutions", "high success rate", "complex problems"],
      "use_cases": ["model training", "best practice extraction", "pattern recognition"]
    },
    "medium_value": {
      "criteria": ["common patterns", "moderate complexity", "typical workflows"],
      "use_cases": ["workflow optimization", "user experience improvement"]
    },
    "low_value": {
      "criteria": ["routine operations", "simple commands", "standard procedures"],
      "use_cases": ["system monitoring", "basic statistics"]
    },
    "negative_value": {
      "criteria": ["errors", "failures", "misuse"],
      "use_cases": ["error prevention", "robustness improvement", "user guidance"]
    }
  }
}
```

---

## 📊 CLI數據結構定義

### 核心數據模型

```python
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class TaskType(Enum):
    GAIA_TESTING = "gaia_testing"
    MCP_MANAGEMENT = "mcp_management" 
    DATA_ANALYSIS = "data_analysis"
    CODE_GENERATION = "code_generation"
    SYSTEM_OPERATION = "system_operation"

class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

class ResultStatus(Enum):
    SUCCESS_PERFECT = "success_perfect"
    SUCCESS_PARTIAL = "success_partial"
    SUCCESS_ACCEPTABLE = "success_acceptable"
    FAILURE_USER = "failure_user"
    FAILURE_SYSTEM = "failure_system"
    FAILURE_CONFIG = "failure_config"
    FAILURE_RESOURCE = "failure_resource"

class LearningValue(Enum):
    HIGH = "high_value"
    MEDIUM = "medium_value"
    LOW = "low_value"
    NEGATIVE = "negative_value"

@dataclass
class CLIInteractionData:
    """CLI交互數據結構"""
    
    # 基本信息
    session_id: str
    timestamp: datetime
    user_id: Optional[str] = None  # 匿名化處理
    
    # 輸入信息
    command: str
    arguments: Dict[str, Any]
    context: Dict[str, Any]
    
    # 分類信息
    task_type: TaskType
    task_subcategory: str
    complexity_level: ComplexityLevel
    
    # 執行信息
    execution_time: float
    tools_used: List[str]
    mcp_adapters_involved: List[str]
    
    # 結果信息
    result_status: ResultStatus
    output_data: Dict[str, Any]
    error_info: Optional[Dict[str, Any]]
    
    # 質量評估
    accuracy_score: Optional[float]
    user_satisfaction: Optional[int]  # 1-5評分
    learning_value: LearningValue
    
    # 元數據
    system_version: str
    environment_info: Dict[str, Any]
    
    def to_training_format(self) -> Dict[str, Any]:
        """轉換為訓練數據格式"""
        return {
            "input": {
                "task_type": self.task_type.value,
                "complexity": self.complexity_level.value,
                "command": self.command,
                "arguments": self.arguments,
                "context": self.context
            },
            "process": {
                "tools_used": self.tools_used,
                "mcp_adapters": self.mcp_adapters_involved,
                "execution_time": self.execution_time
            },
            "output": {
                "status": self.result_status.value,
                "accuracy": self.accuracy_score,
                "satisfaction": self.user_satisfaction,
                "learning_value": self.learning_value.value
            },
            "metadata": {
                "timestamp": self.timestamp.isoformat(),
                "session_id": self.session_id,
                "version": self.system_version
            }
        }
```

---

## 🗂️ 存儲架構設計

### 1. 分層存儲結構

```
cli_training_data/
├── raw_data/                    # 原始數據
│   ├── daily/                   # 按日期分組
│   │   ├── 2025-06-08/
│   │   │   ├── gaia_testing/
│   │   │   ├── mcp_management/
│   │   │   └── data_analysis/
│   │   └── 2025-06-09/
│   └── sessions/                # 按會話分組
│       ├── session_001/
│       └── session_002/
├── processed_data/              # 處理後數據
│   ├── categorized/             # 按分類整理
│   │   ├── high_value/
│   │   ├── medium_value/
│   │   └── learning_patterns/
│   ├── aggregated/              # 聚合統計
│   └── cleaned/                 # 清理後數據
├── training_sets/               # 訓練集
│   ├── gaia_optimization/
│   ├── tool_selection/
│   ├── error_prevention/
│   └── workflow_optimization/
└── metadata/                    # 元數據
    ├── schemas/
    ├── statistics/
    └── quality_reports/
```

### 2. 數據庫設計

```sql
-- CLI交互主表
CREATE TABLE cli_interactions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    user_hash VARCHAR(64), -- 匿名化用戶標識
    
    -- 輸入信息
    command TEXT NOT NULL,
    arguments JSONB,
    context JSONB,
    
    -- 分類信息
    task_type VARCHAR(32) NOT NULL,
    task_subcategory VARCHAR(64),
    complexity_level VARCHAR(16) NOT NULL,
    
    -- 執行信息
    execution_time FLOAT,
    tools_used TEXT[],
    mcp_adapters TEXT[],
    
    -- 結果信息
    result_status VARCHAR(32) NOT NULL,
    output_data JSONB,
    error_info JSONB,
    
    -- 質量評估
    accuracy_score FLOAT,
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    learning_value VARCHAR(16) NOT NULL,
    
    -- 元數據
    system_version VARCHAR(32),
    environment_info JSONB,
    
    -- 索引
    INDEX idx_timestamp (timestamp),
    INDEX idx_task_type (task_type),
    INDEX idx_learning_value (learning_value),
    INDEX idx_result_status (result_status)
);

-- 工具使用統計表
CREATE TABLE tool_usage_stats (
    id BIGSERIAL PRIMARY KEY,
    tool_name VARCHAR(64) NOT NULL,
    task_type VARCHAR(32) NOT NULL,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    avg_execution_time FLOAT,
    avg_accuracy FLOAT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 學習模式表
CREATE TABLE learning_patterns (
    id BIGSERIAL PRIMARY KEY,
    pattern_type VARCHAR(32) NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence_score FLOAT,
    usage_frequency INTEGER DEFAULT 0,
    effectiveness_score FLOAT,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🔄 數據收集流程

### 1. 實時數據收集

```python
class CLIDataCollector:
    """CLI數據收集器"""
    
    def __init__(self):
        self.session_id = self.generate_session_id()
        self.data_buffer = []
        
    def collect_interaction(self, 
                          command: str,
                          arguments: Dict[str, Any],
                          context: Dict[str, Any]) -> str:
        """收集CLI交互數據"""
        
        interaction_id = self.generate_interaction_id()
        
        # 創建數據記錄
        interaction_data = CLIInteractionData(
            session_id=self.session_id,
            timestamp=datetime.now(),
            command=command,
            arguments=arguments,
            context=context,
            task_type=self.classify_task_type(command, arguments),
            complexity_level=self.assess_complexity(command, arguments),
            system_version=self.get_system_version(),
            environment_info=self.get_environment_info()
        )
        
        # 緩存數據
        self.data_buffer.append(interaction_data)
        
        return interaction_id
    
    def update_result(self,
                     interaction_id: str,
                     result_status: ResultStatus,
                     output_data: Dict[str, Any],
                     execution_time: float,
                     tools_used: List[str],
                     error_info: Optional[Dict[str, Any]] = None):
        """更新執行結果"""
        
        # 找到對應的交互記錄並更新
        for interaction in self.data_buffer:
            if interaction.interaction_id == interaction_id:
                interaction.result_status = result_status
                interaction.output_data = output_data
                interaction.execution_time = execution_time
                interaction.tools_used = tools_used
                interaction.error_info = error_info
                interaction.learning_value = self.assess_learning_value(interaction)
                break
    
    def flush_to_storage(self):
        """將緩存數據寫入存儲"""
        for interaction in self.data_buffer:
            self.store_interaction(interaction)
        self.data_buffer.clear()
```

### 2. 數據分類邏輯

```python
class CLIDataClassifier:
    """CLI數據分類器"""
    
    def classify_task_type(self, command: str, arguments: Dict[str, Any]) -> TaskType:
        """分類任務類型"""
        
        if "--gaia" in arguments or "gaia" in command.lower():
            return TaskType.GAIA_TESTING
        elif "--list" in arguments or "list" in command:
            return TaskType.MCP_MANAGEMENT
        elif any(keyword in command.lower() for keyword in ["analyze", "data", "file"]):
            return TaskType.DATA_ANALYSIS
        elif any(keyword in command.lower() for keyword in ["generate", "code", "script"]):
            return TaskType.CODE_GENERATION
        else:
            return TaskType.SYSTEM_OPERATION
    
    def assess_complexity(self, command: str, arguments: Dict[str, Any]) -> ComplexityLevel:
        """評估複雜度"""
        
        arg_count = len(arguments)
        command_length = len(command.split())
        
        if arg_count <= 1 and command_length <= 2:
            return ComplexityLevel.SIMPLE
        elif arg_count <= 3 and command_length <= 5:
            return ComplexityLevel.MODERATE
        elif arg_count <= 6 and command_length <= 10:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.EXPERT
    
    def assess_learning_value(self, interaction: CLIInteractionData) -> LearningValue:
        """評估學習價值"""
        
        # 基於多個因素評估
        factors = {
            "novelty": self.assess_novelty(interaction),
            "success": self.assess_success(interaction),
            "complexity": self.assess_complexity_value(interaction),
            "frequency": self.assess_frequency(interaction)
        }
        
        # 綜合評分
        total_score = sum(factors.values()) / len(factors)
        
        if total_score >= 0.8:
            return LearningValue.HIGH
        elif total_score >= 0.6:
            return LearningValue.MEDIUM
        elif total_score >= 0.3:
            return LearningValue.LOW
        else:
            return LearningValue.NEGATIVE
```

---

## 📈 數據質量控制

### 1. 數據驗證規則

```python
class CLIDataValidator:
    """CLI數據驗證器"""
    
    def validate_interaction(self, interaction: CLIInteractionData) -> bool:
        """驗證交互數據"""
        
        checks = [
            self.check_required_fields(interaction),
            self.check_data_types(interaction),
            self.check_value_ranges(interaction),
            self.check_consistency(interaction),
            self.check_privacy_compliance(interaction)
        ]
        
        return all(checks)
    
    def check_privacy_compliance(self, interaction: CLIInteractionData) -> bool:
        """檢查隱私合規性"""
        
        # 確保沒有敏感信息
        sensitive_patterns = [
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # 信用卡號
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 郵箱
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        ]
        
        text_content = str(interaction.command) + str(interaction.arguments)
        
        for pattern in sensitive_patterns:
            if re.search(pattern, text_content):
                return False
        
        return True
```

### 2. 數據清理流程

```python
class CLIDataCleaner:
    """CLI數據清理器"""
    
    def clean_interaction_data(self, raw_data: List[CLIInteractionData]) -> List[CLIInteractionData]:
        """清理交互數據"""
        
        cleaned_data = []
        
        for interaction in raw_data:
            # 匿名化處理
            interaction = self.anonymize_data(interaction)
            
            # 標準化格式
            interaction = self.standardize_format(interaction)
            
            # 移除敏感信息
            interaction = self.remove_sensitive_info(interaction)
            
            # 驗證數據質量
            if self.validate_quality(interaction):
                cleaned_data.append(interaction)
        
        return cleaned_data
    
    def anonymize_data(self, interaction: CLIInteractionData) -> CLIInteractionData:
        """匿名化數據"""
        
        # 移除或哈希化用戶標識
        if interaction.user_id:
            interaction.user_id = hashlib.sha256(interaction.user_id.encode()).hexdigest()[:16]
        
        # 移除IP地址等敏感信息
        if 'ip_address' in interaction.environment_info:
            del interaction.environment_info['ip_address']
        
        return interaction
```

---

## 🎯 訓練數據生成

### 1. 訓練集構建

```python
class TrainingDataBuilder:
    """訓練數據構建器"""
    
    def build_gaia_optimization_dataset(self) -> Dict[str, Any]:
        """構建GAIA優化訓練集"""
        
        # 查詢GAIA相關的高價值交互
        gaia_interactions = self.query_interactions(
            task_type=TaskType.GAIA_TESTING,
            learning_value=[LearningValue.HIGH, LearningValue.MEDIUM],
            result_status=[ResultStatus.SUCCESS_PERFECT, ResultStatus.SUCCESS_PARTIAL]
        )
        
        # 構建訓練樣本
        training_samples = []
        for interaction in gaia_interactions:
            sample = {
                "input": {
                    "question_type": self.extract_question_type(interaction),
                    "complexity": interaction.complexity_level.value,
                    "context": interaction.context
                },
                "optimal_strategy": {
                    "tools": interaction.tools_used,
                    "sequence": self.extract_tool_sequence(interaction),
                    "parameters": self.extract_parameters(interaction)
                },
                "expected_outcome": {
                    "accuracy": interaction.accuracy_score,
                    "execution_time": interaction.execution_time,
                    "success_probability": self.calculate_success_probability(interaction)
                }
            }
            training_samples.append(sample)
        
        return {
            "dataset_name": "gaia_optimization",
            "version": "1.0",
            "samples": training_samples,
            "metadata": {
                "total_samples": len(training_samples),
                "collection_period": self.get_collection_period(),
                "quality_score": self.calculate_dataset_quality(training_samples)
            }
        }
    
    def build_tool_selection_dataset(self) -> Dict[str, Any]:
        """構建工具選擇訓練集"""
        
        # 分析工具使用模式
        tool_patterns = self.analyze_tool_patterns()
        
        # 構建工具選擇樣本
        selection_samples = []
        for pattern in tool_patterns:
            sample = {
                "task_description": pattern["task_description"],
                "available_tools": pattern["available_tools"],
                "optimal_selection": pattern["best_tools"],
                "performance_metrics": pattern["metrics"]
            }
            selection_samples.append(sample)
        
        return {
            "dataset_name": "tool_selection",
            "version": "1.0", 
            "samples": selection_samples
        }
```

---

## 🔄 持續學習集成

### 1. RL-SRT集成

```python
class CLIDataRLIntegration:
    """CLI數據強化學習集成"""
    
    def __init__(self):
        self.rl_srt_adapter = self.get_rl_srt_adapter()
        
    def feed_to_rl_system(self, interaction_data: List[CLIInteractionData]):
        """將CLI數據餵給RL系統"""
        
        # 轉換為RL訓練格式
        rl_episodes = []
        for interaction in interaction_data:
            episode = {
                "state": self.extract_state(interaction),
                "action": self.extract_action(interaction),
                "reward": self.calculate_reward(interaction),
                "next_state": self.extract_next_state(interaction)
            }
            rl_episodes.append(episode)
        
        # 餵給RL-SRT系統
        self.rl_srt_adapter.train_from_episodes(rl_episodes)
    
    def calculate_reward(self, interaction: CLIInteractionData) -> float:
        """計算獎勵值"""
        
        base_reward = 0.0
        
        # 基於結果狀態
        if interaction.result_status == ResultStatus.SUCCESS_PERFECT:
            base_reward += 1.0
        elif interaction.result_status == ResultStatus.SUCCESS_PARTIAL:
            base_reward += 0.7
        elif interaction.result_status == ResultStatus.SUCCESS_ACCEPTABLE:
            base_reward += 0.5
        else:
            base_reward -= 0.5
        
        # 基於準確率
        if interaction.accuracy_score:
            base_reward += interaction.accuracy_score * 0.5
        
        # 基於執行效率
        if interaction.execution_time:
            efficiency_bonus = max(0, (10 - interaction.execution_time) / 10 * 0.3)
            base_reward += efficiency_bonus
        
        # 基於用戶滿意度
        if interaction.user_satisfaction:
            satisfaction_bonus = (interaction.user_satisfaction - 3) / 2 * 0.2
            base_reward += satisfaction_bonus
        
        return base_reward
```

---

## 📊 監控和分析

### 1. 數據質量監控

```python
class CLIDataMonitor:
    """CLI數據監控器"""
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """生成數據質量報告"""
        
        return {
            "collection_stats": {
                "total_interactions": self.count_total_interactions(),
                "daily_average": self.calculate_daily_average(),
                "task_type_distribution": self.get_task_distribution(),
                "complexity_distribution": self.get_complexity_distribution()
            },
            "quality_metrics": {
                "data_completeness": self.calculate_completeness(),
                "accuracy_scores": self.get_accuracy_distribution(),
                "error_rates": self.calculate_error_rates(),
                "learning_value_distribution": self.get_learning_value_distribution()
            },
            "training_readiness": {
                "high_value_samples": self.count_high_value_samples(),
                "balanced_distribution": self.check_balance(),
                "sufficient_volume": self.check_volume_sufficiency()
            }
        }
```

這個設計確保了CLI數據能夠按照結構化的方式收集、分類和存儲，為後續的訓練和優化提供高質量的數據基礎。

