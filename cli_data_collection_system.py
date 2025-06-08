#!/usr/bin/env python3
"""
CLI數據收集和存儲系統實現
基於分類架構的完整數據管理系統
"""

import os
import json
import sqlite3
import hashlib
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
import re

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 枚舉定義
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
    interaction_id: str
    session_id: str
    timestamp: datetime
    command: str
    user_hash: Optional[str] = None
    
    # 輸入信息
    arguments: Dict[str, Any] = None
    context: Dict[str, Any] = None
    
    # 分類信息
    task_type: TaskType = TaskType.SYSTEM_OPERATION
    task_subcategory: str = ""
    complexity_level: ComplexityLevel = ComplexityLevel.SIMPLE
    
    # 執行信息
    execution_time: float = 0.0
    tools_used: List[str] = None
    mcp_adapters_involved: List[str] = None
    
    # 結果信息
    result_status: ResultStatus = ResultStatus.SUCCESS_ACCEPTABLE
    output_data: Dict[str, Any] = None
    error_info: Optional[Dict[str, Any]] = None
    
    # 質量評估
    accuracy_score: Optional[float] = None
    user_satisfaction: Optional[int] = None
    learning_value: LearningValue = LearningValue.LOW
    
    # 元數據
    system_version: str = "1.0.0"
    environment_info: Dict[str, Any] = None
    
    def __post_init__(self):
        """初始化後處理"""
        if self.arguments is None:
            self.arguments = {}
        if self.context is None:
            self.context = {}
        if self.tools_used is None:
            self.tools_used = []
        if self.mcp_adapters_involved is None:
            self.mcp_adapters_involved = []
        if self.output_data is None:
            self.output_data = {}
        if self.environment_info is None:
            self.environment_info = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        data = asdict(self)
        # 處理枚舉類型
        data['task_type'] = self.task_type.value
        data['complexity_level'] = self.complexity_level.value
        data['result_status'] = self.result_status.value
        data['learning_value'] = self.learning_value.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
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

class CLIDataClassifier:
    """CLI數據分類器"""
    
    def __init__(self):
        self.task_keywords = {
            TaskType.GAIA_TESTING: ["gaia", "test", "benchmark", "level", "accuracy"],
            TaskType.MCP_MANAGEMENT: ["mcp", "adapter", "list", "load", "register"],
            TaskType.DATA_ANALYSIS: ["analyze", "data", "file", "csv", "excel", "statistics"],
            TaskType.CODE_GENERATION: ["generate", "code", "script", "create", "build"],
            TaskType.SYSTEM_OPERATION: ["status", "config", "help", "version", "info"]
        }
    
    def classify_task_type(self, command: str, arguments: Dict[str, Any]) -> TaskType:
        """分類任務類型"""
        
        command_lower = command.lower()
        args_str = " ".join(str(v) for v in arguments.values()).lower()
        full_text = f"{command_lower} {args_str}"
        
        # 計算每種任務類型的匹配分數
        scores = {}
        for task_type, keywords in self.task_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            scores[task_type] = score
        
        # 返回得分最高的任務類型
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return TaskType.SYSTEM_OPERATION
    
    def classify_subcategory(self, task_type: TaskType, command: str, arguments: Dict[str, Any]) -> str:
        """分類子類別"""
        
        subcategory_map = {
            TaskType.GAIA_TESTING: {
                "level1": ["level 1", "--level 1", "level1"],
                "level2": ["level 2", "--level 2", "level2"],
                "level3": ["level 3", "--level 3", "level3"],
                "validation": ["validation", "validate", "verify"],
                "analysis": ["analyze", "analysis", "report"]
            },
            TaskType.MCP_MANAGEMENT: {
                "list": ["list", "--list", "show"],
                "load": ["load", "--load", "import"],
                "test": ["test", "--test", "check"],
                "configure": ["config", "configure", "setup"],
                "debug": ["debug", "troubleshoot", "fix"]
            }
        }
        
        if task_type not in subcategory_map:
            return "general"
        
        command_lower = command.lower()
        args_str = " ".join(str(v) for v in arguments.values()).lower()
        full_text = f"{command_lower} {args_str}"
        
        for subcategory, keywords in subcategory_map[task_type].items():
            if any(keyword in full_text for keyword in keywords):
                return subcategory
        
        return "general"
    
    def assess_complexity(self, command: str, arguments: Dict[str, Any], context: Dict[str, Any]) -> ComplexityLevel:
        """評估複雜度"""
        
        # 計算複雜度指標
        arg_count = len(arguments)
        command_length = len(command.split())
        context_size = len(context)
        
        # 檢查複雜參數
        complex_args = ["--max-tasks", "--level", "--config", "--custom"]
        complex_arg_count = sum(1 for arg in arguments.keys() if any(ca in str(arg) for ca in complex_args))
        
        # 計算總複雜度分數
        complexity_score = (
            arg_count * 0.3 +
            command_length * 0.2 +
            context_size * 0.1 +
            complex_arg_count * 0.4
        )
        
        if complexity_score <= 1.0:
            return ComplexityLevel.SIMPLE
        elif complexity_score <= 3.0:
            return ComplexityLevel.MODERATE
        elif complexity_score <= 6.0:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.EXPERT
    
    def assess_learning_value(self, interaction: CLIInteractionData) -> LearningValue:
        """評估學習價值"""
        
        score = 0.0
        
        # 基於任務類型
        if interaction.task_type == TaskType.GAIA_TESTING:
            score += 0.4
        elif interaction.task_type == TaskType.MCP_MANAGEMENT:
            score += 0.3
        elif interaction.task_type == TaskType.DATA_ANALYSIS:
            score += 0.3
        
        # 基於複雜度
        complexity_scores = {
            ComplexityLevel.SIMPLE: 0.1,
            ComplexityLevel.MODERATE: 0.3,
            ComplexityLevel.COMPLEX: 0.5,
            ComplexityLevel.EXPERT: 0.7
        }
        score += complexity_scores.get(interaction.complexity_level, 0.1)
        
        # 基於結果狀態
        if interaction.result_status in [ResultStatus.SUCCESS_PERFECT, ResultStatus.SUCCESS_PARTIAL]:
            score += 0.3
        elif interaction.result_status == ResultStatus.SUCCESS_ACCEPTABLE:
            score += 0.1
        else:
            score -= 0.2
        
        # 基於準確率
        if interaction.accuracy_score:
            score += interaction.accuracy_score * 0.2
        
        # 基於工具使用
        if len(interaction.tools_used) > 1:
            score += 0.2
        
        # 分類學習價值
        if score >= 0.8:
            return LearningValue.HIGH
        elif score >= 0.5:
            return LearningValue.MEDIUM
        elif score >= 0.2:
            return LearningValue.LOW
        else:
            return LearningValue.NEGATIVE

class CLIDataValidator:
    """CLI數據驗證器"""
    
    def __init__(self):
        self.sensitive_patterns = [
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # 信用卡號
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 郵箱
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP地址
        ]
    
    def validate_interaction(self, interaction: CLIInteractionData) -> bool:
        """驗證交互數據"""
        
        checks = [
            self._check_required_fields(interaction),
            self._check_data_types(interaction),
            self._check_value_ranges(interaction),
            self._check_privacy_compliance(interaction)
        ]
        
        return all(checks)
    
    def _check_required_fields(self, interaction: CLIInteractionData) -> bool:
        """檢查必需字段"""
        required_fields = ['interaction_id', 'session_id', 'timestamp', 'command']
        
        for field in required_fields:
            if not hasattr(interaction, field) or getattr(interaction, field) is None:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def _check_data_types(self, interaction: CLIInteractionData) -> bool:
        """檢查數據類型"""
        try:
            # 檢查時間戳
            if not isinstance(interaction.timestamp, datetime):
                return False
            
            # 檢查執行時間
            if interaction.execution_time < 0:
                return False
            
            # 檢查用戶滿意度
            if interaction.user_satisfaction is not None:
                if not (1 <= interaction.user_satisfaction <= 5):
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Data type check failed: {e}")
            return False
    
    def _check_value_ranges(self, interaction: CLIInteractionData) -> bool:
        """檢查值範圍"""
        
        # 檢查準確率
        if interaction.accuracy_score is not None:
            if not (0.0 <= interaction.accuracy_score <= 1.0):
                return False
        
        # 檢查執行時間（不應超過1小時）
        if interaction.execution_time > 3600:
            return False
        
        return True
    
    def _check_privacy_compliance(self, interaction: CLIInteractionData) -> bool:
        """檢查隱私合規性"""
        
        # 檢查命令中的敏感信息
        text_content = f"{interaction.command} {json.dumps(interaction.arguments)}"
        
        for pattern in self.sensitive_patterns:
            if re.search(pattern, text_content):
                logger.warning(f"Sensitive data detected in interaction {interaction.interaction_id}")
                return False
        
        return True
    
    def anonymize_data(self, interaction: CLIInteractionData) -> CLIInteractionData:
        """匿名化數據"""
        
        # 生成用戶哈希
        if interaction.user_hash:
            interaction.user_hash = hashlib.sha256(interaction.user_hash.encode()).hexdigest()[:16]
        
        # 移除環境信息中的敏感數據
        if 'ip_address' in interaction.environment_info:
            del interaction.environment_info['ip_address']
        
        if 'hostname' in interaction.environment_info:
            interaction.environment_info['hostname'] = 'anonymized'
        
        return interaction

class CLIDataStorage:
    """CLI數據存儲系統"""
    
    def __init__(self, storage_dir: str = "/home/ubuntu/Powerauto.ai/cli_training_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 創建子目錄
        self.raw_data_dir = self.storage_dir / "raw_data"
        self.processed_data_dir = self.storage_dir / "processed_data"
        self.training_sets_dir = self.storage_dir / "training_sets"
        self.metadata_dir = self.storage_dir / "metadata"
        
        for dir_path in [self.raw_data_dir, self.processed_data_dir, self.training_sets_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 初始化數據庫
        self.db_path = self.storage_dir / "cli_interactions.db"
        self._init_database()
    
    def _init_database(self):
        """初始化數據庫"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 創建主表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cli_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interaction_id TEXT UNIQUE NOT NULL,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_hash TEXT,
                    
                    command TEXT NOT NULL,
                    arguments TEXT,
                    context TEXT,
                    
                    task_type TEXT NOT NULL,
                    task_subcategory TEXT,
                    complexity_level TEXT NOT NULL,
                    
                    execution_time REAL,
                    tools_used TEXT,
                    mcp_adapters TEXT,
                    
                    result_status TEXT NOT NULL,
                    output_data TEXT,
                    error_info TEXT,
                    
                    accuracy_score REAL,
                    user_satisfaction INTEGER,
                    learning_value TEXT NOT NULL,
                    
                    system_version TEXT,
                    environment_info TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON cli_interactions(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_task_type ON cli_interactions(task_type)",
                "CREATE INDEX IF NOT EXISTS idx_learning_value ON cli_interactions(learning_value)",
                "CREATE INDEX IF NOT EXISTS idx_result_status ON cli_interactions(result_status)",
                "CREATE INDEX IF NOT EXISTS idx_session_id ON cli_interactions(session_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
    
    def store_interaction(self, interaction: CLIInteractionData) -> bool:
        """存儲交互數據"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cli_interactions (
                        interaction_id, session_id, timestamp, user_hash,
                        command, arguments, context,
                        task_type, task_subcategory, complexity_level,
                        execution_time, tools_used, mcp_adapters,
                        result_status, output_data, error_info,
                        accuracy_score, user_satisfaction, learning_value,
                        system_version, environment_info
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.interaction_id,
                    interaction.session_id,
                    interaction.timestamp.isoformat(),
                    interaction.user_hash,
                    interaction.command,
                    json.dumps(interaction.arguments),
                    json.dumps(interaction.context),
                    interaction.task_type.value,
                    interaction.task_subcategory,
                    interaction.complexity_level.value,
                    interaction.execution_time,
                    json.dumps(interaction.tools_used),
                    json.dumps(interaction.mcp_adapters_involved),
                    interaction.result_status.value,
                    json.dumps(interaction.output_data),
                    json.dumps(interaction.error_info) if interaction.error_info else None,
                    interaction.accuracy_score,
                    interaction.user_satisfaction,
                    interaction.learning_value.value,
                    interaction.system_version,
                    json.dumps(interaction.environment_info)
                ))
                
                conn.commit()
            
            # 同時保存到文件系統
            self._store_to_filesystem(interaction)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            return False
    
    def _store_to_filesystem(self, interaction: CLIInteractionData):
        """存儲到文件系統"""
        
        # 按日期和任務類型組織
        date_str = interaction.timestamp.strftime("%Y-%m-%d")
        task_type_str = interaction.task_type.value
        
        file_dir = self.raw_data_dir / "daily" / date_str / task_type_str
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存為JSON文件
        file_path = file_dir / f"{interaction.interaction_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(interaction.to_dict(), f, indent=2, ensure_ascii=False)
    
    def query_interactions(self, 
                          task_type: Optional[TaskType] = None,
                          learning_value: Optional[List[LearningValue]] = None,
                          result_status: Optional[List[ResultStatus]] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          limit: Optional[int] = None) -> List[CLIInteractionData]:
        """查詢交互數據"""
        
        query = "SELECT * FROM cli_interactions WHERE 1=1"
        params = []
        
        if task_type:
            query += " AND task_type = ?"
            params.append(task_type.value)
        
        if learning_value:
            placeholders = ",".join("?" * len(learning_value))
            query += f" AND learning_value IN ({placeholders})"
            params.extend([lv.value for lv in learning_value])
        
        if result_status:
            placeholders = ",".join("?" * len(result_status))
            query += f" AND result_status IN ({placeholders})"
            params.extend([rs.value for rs in result_status])
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
        
        # 轉換為CLIInteractionData對象
        interactions = []
        for row in rows:
            interaction = self._row_to_interaction(row)
            interactions.append(interaction)
        
        return interactions
    
    def _row_to_interaction(self, row) -> CLIInteractionData:
        """將數據庫行轉換為CLIInteractionData對象"""
        
        return CLIInteractionData(
            interaction_id=row[1],
            session_id=row[2],
            timestamp=datetime.fromisoformat(row[3]),
            user_hash=row[4],
            command=row[5],
            arguments=json.loads(row[6]) if row[6] else {},
            context=json.loads(row[7]) if row[7] else {},
            task_type=TaskType(row[8]),
            task_subcategory=row[9] or "",
            complexity_level=ComplexityLevel(row[10]),
            execution_time=row[11] or 0.0,
            tools_used=json.loads(row[12]) if row[12] else [],
            mcp_adapters_involved=json.loads(row[13]) if row[13] else [],
            result_status=ResultStatus(row[14]),
            output_data=json.loads(row[15]) if row[15] else {},
            error_info=json.loads(row[16]) if row[16] else None,
            accuracy_score=row[17],
            user_satisfaction=row[18],
            learning_value=LearningValue(row[19]),
            system_version=row[20] or "1.0.0",
            environment_info=json.loads(row[21]) if row[21] else {}
        )

class CLIDataCollector:
    """CLI數據收集器"""
    
    def __init__(self, storage_dir: str = "/home/ubuntu/Powerauto.ai/cli_training_data"):
        self.session_id = str(uuid.uuid4())
        self.classifier = CLIDataClassifier()
        self.validator = CLIDataValidator()
        self.storage = CLIDataStorage(storage_dir)
        self.data_buffer = []
        self.buffer_lock = threading.Lock()
        
        logger.info(f"CLI數據收集器初始化完成，會話ID: {self.session_id}")
    
    def start_interaction(self, 
                         command: str,
                         arguments: Dict[str, Any],
                         context: Dict[str, Any] = None,
                         user_id: Optional[str] = None) -> str:
        """開始記錄CLI交互"""
        
        interaction_id = str(uuid.uuid4())
        
        # 創建交互數據
        interaction = CLIInteractionData(
            interaction_id=interaction_id,
            session_id=self.session_id,
            timestamp=datetime.now(timezone.utc),
            user_hash=user_id,
            command=command,
            arguments=arguments,
            context=context or {},
            system_version="1.0.0",
            environment_info=self._get_environment_info()
        )
        
        # 分類
        interaction.task_type = self.classifier.classify_task_type(command, arguments)
        interaction.task_subcategory = self.classifier.classify_subcategory(
            interaction.task_type, command, arguments
        )
        interaction.complexity_level = self.classifier.assess_complexity(
            command, arguments, context or {}
        )
        
        # 添加到緩存
        with self.buffer_lock:
            self.data_buffer.append(interaction)
        
        logger.info(f"開始記錄交互: {interaction_id} ({interaction.task_type.value})")
        
        return interaction_id
    
    def end_interaction(self,
                       interaction_id: str,
                       result_status: ResultStatus,
                       output_data: Dict[str, Any],
                       execution_time: float,
                       tools_used: List[str] = None,
                       mcp_adapters: List[str] = None,
                       accuracy_score: Optional[float] = None,
                       user_satisfaction: Optional[int] = None,
                       error_info: Optional[Dict[str, Any]] = None):
        """結束記錄CLI交互"""
        
        with self.buffer_lock:
            # 找到對應的交互記錄
            interaction = None
            for i, inter in enumerate(self.data_buffer):
                if inter.interaction_id == interaction_id:
                    interaction = inter
                    break
            
            if interaction is None:
                logger.warning(f"未找到交互記錄: {interaction_id}")
                return
            
            # 更新結果信息
            interaction.result_status = result_status
            interaction.output_data = output_data
            interaction.execution_time = execution_time
            interaction.tools_used = tools_used or []
            interaction.mcp_adapters_involved = mcp_adapters or []
            interaction.accuracy_score = accuracy_score
            interaction.user_satisfaction = user_satisfaction
            interaction.error_info = error_info
            
            # 評估學習價值
            interaction.learning_value = self.classifier.assess_learning_value(interaction)
            
            # 驗證和匿名化
            if self.validator.validate_interaction(interaction):
                interaction = self.validator.anonymize_data(interaction)
                
                # 存儲數據
                if self.storage.store_interaction(interaction):
                    logger.info(f"交互記錄已保存: {interaction_id}")
                else:
                    logger.error(f"交互記錄保存失敗: {interaction_id}")
            else:
                logger.warning(f"交互記錄驗證失敗: {interaction_id}")
            
            # 從緩存中移除
            self.data_buffer.remove(interaction)
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """獲取環境信息"""
        
        return {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            "platform": os.name,
            "working_directory": os.getcwd(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """獲取會話統計"""
        
        # 查詢當前會話的數據
        interactions = self.storage.query_interactions()
        session_interactions = [i for i in interactions if i.session_id == self.session_id]
        
        if not session_interactions:
            return {"session_id": self.session_id, "total_interactions": 0}
        
        # 統計信息
        task_types = {}
        complexity_levels = {}
        result_statuses = {}
        learning_values = {}
        
        total_execution_time = 0
        accuracy_scores = []
        
        for interaction in session_interactions:
            # 任務類型統計
            task_type = interaction.task_type.value
            task_types[task_type] = task_types.get(task_type, 0) + 1
            
            # 複雜度統計
            complexity = interaction.complexity_level.value
            complexity_levels[complexity] = complexity_levels.get(complexity, 0) + 1
            
            # 結果狀態統計
            status = interaction.result_status.value
            result_statuses[status] = result_statuses.get(status, 0) + 1
            
            # 學習價值統計
            value = interaction.learning_value.value
            learning_values[value] = learning_values.get(value, 0) + 1
            
            # 性能統計
            total_execution_time += interaction.execution_time
            if interaction.accuracy_score is not None:
                accuracy_scores.append(interaction.accuracy_score)
        
        return {
            "session_id": self.session_id,
            "total_interactions": len(session_interactions),
            "task_type_distribution": task_types,
            "complexity_distribution": complexity_levels,
            "result_status_distribution": result_statuses,
            "learning_value_distribution": learning_values,
            "total_execution_time": total_execution_time,
            "average_execution_time": total_execution_time / len(session_interactions),
            "average_accuracy": sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else None,
            "high_value_interactions": learning_values.get("high_value", 0)
        }

# 全局收集器實例
_cli_data_collector = None
_collector_lock = threading.Lock()

def get_cli_data_collector() -> CLIDataCollector:
    """獲取CLI數據收集器的全局實例"""
    global _cli_data_collector
    
    if _cli_data_collector is None:
        with _collector_lock:
            if _cli_data_collector is None:
                _cli_data_collector = CLIDataCollector()
    
    return _cli_data_collector

if __name__ == "__main__":
    # 測試代碼
    collector = get_cli_data_collector()
    
    print("🔍 CLI數據收集系統測試")
    print("=" * 40)
    
    # 模擬一個GAIA測試交互
    interaction_id = collector.start_interaction(
        command="python enhanced_mcp_cli.py",
        arguments={"gaia": True, "level": 1, "max-tasks": 5},
        context={"test_mode": True, "target_accuracy": 0.9}
    )
    
    print(f"開始交互: {interaction_id}")
    
    # 模擬執行結果
    collector.end_interaction(
        interaction_id=interaction_id,
        result_status=ResultStatus.SUCCESS_PARTIAL,
        output_data={"accuracy": 0.6, "correct_answers": 3, "total_questions": 5},
        execution_time=45.2,
        tools_used=["claude_mcp", "gemini_mcp", "webagent_core"],
        mcp_adapters=["claude_adapter", "gemini_adapter"],
        accuracy_score=0.6,
        user_satisfaction=4
    )
    
    print(f"結束交互: {interaction_id}")
    
    # 獲取統計信息
    stats = collector.get_session_stats()
    print(f"\n📊 會話統計:")
    print(f"   總交互數: {stats['total_interactions']}")
    print(f"   任務類型分布: {stats['task_type_distribution']}")
    print(f"   學習價值分布: {stats['learning_value_distribution']}")
    print(f"   平均準確率: {stats['average_accuracy']:.2f}" if stats['average_accuracy'] else "   平均準確率: N/A")
    
    print("\n✅ 測試完成")

