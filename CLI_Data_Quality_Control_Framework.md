# CLI數據質量控制機制

## 🎯 質量控制目標

確保CLI數據的：
- **準確性** - 數據反映真實的使用情況
- **完整性** - 關鍵字段不缺失
- **一致性** - 數據格式和分類標準統一
- **隱私性** - 不包含敏感信息
- **可用性** - 適合訓練和分析使用

---

## 🔍 數據質量檢查框架

### 1. 實時質量檢查

#### A. 數據收集階段檢查
```python
class RealTimeQualityChecker:
    """實時質量檢查器"""
    
    def validate_on_collection(self, interaction: CLIInteractionData) -> QualityReport:
        """收集時驗證"""
        
        checks = {
            "required_fields": self.check_required_fields(interaction),
            "data_types": self.check_data_types(interaction),
            "value_ranges": self.check_value_ranges(interaction),
            "privacy_compliance": self.check_privacy(interaction),
            "format_consistency": self.check_format(interaction)
        }
        
        return QualityReport(checks)
```

#### B. 關鍵質量指標
- **字段完整率** ≥ 95%
- **數據類型正確率** = 100%
- **隱私合規率** = 100%
- **格式一致性** ≥ 98%

### 2. 批量質量審核

#### A. 定期數據審核
```python
class BatchQualityAuditor:
    """批量質量審核器"""
    
    def daily_audit(self) -> AuditReport:
        """每日數據審核"""
        
        yesterday_data = self.get_yesterday_data()
        
        audit_results = {
            "data_volume": self.check_volume_trends(yesterday_data),
            "quality_metrics": self.calculate_quality_metrics(yesterday_data),
            "anomaly_detection": self.detect_anomalies(yesterday_data),
            "consistency_check": self.check_consistency(yesterday_data)
        }
        
        return AuditReport(audit_results)
```

#### B. 質量趨勢監控
- **數據量趨勢** - 檢測異常增減
- **準確率趨勢** - 監控性能變化
- **錯誤率趨勢** - 識別質量下降
- **分類分布** - 確保數據平衡

---

## 📊 質量評分系統

### 1. 綜合質量分數計算

```python
def calculate_quality_score(interaction: CLIInteractionData) -> float:
    """計算質量分數 (0-1)"""
    
    scores = {
        "completeness": calculate_completeness_score(interaction),      # 30%
        "accuracy": calculate_accuracy_score(interaction),              # 25%
        "consistency": calculate_consistency_score(interaction),        # 20%
        "timeliness": calculate_timeliness_score(interaction),         # 15%
        "uniqueness": calculate_uniqueness_score(interaction)          # 10%
    }
    
    weights = [0.30, 0.25, 0.20, 0.15, 0.10]
    
    return sum(score * weight for score, weight in zip(scores.values(), weights))
```

### 2. 質量等級分類

| 分數範圍 | 質量等級 | 使用建議 |
|---------|---------|---------|
| 0.9-1.0 | 優秀 (A) | 優先用於訓練 |
| 0.8-0.9 | 良好 (B) | 適合訓練使用 |
| 0.7-0.8 | 一般 (C) | 需要清理後使用 |
| 0.6-0.7 | 較差 (D) | 僅用於統計分析 |
| 0.0-0.6 | 差 (F) | 不建議使用 |

---

## 🛡️ 隱私保護機制

### 1. 敏感信息檢測

#### A. 自動檢測模式
```python
class PrivacyProtector:
    """隱私保護器"""
    
    SENSITIVE_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}-\d{3}-\d{4}\b',
        "credit_card": r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "api_key": r'\b[A-Za-z0-9]{32,}\b'
    }
    
    def scan_for_sensitive_data(self, text: str) -> List[str]:
        """掃描敏感數據"""
        
        detected = []
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            if re.search(pattern, text):
                detected.append(pattern_name)
        
        return detected
```

#### B. 數據匿名化處理
```python
def anonymize_interaction(interaction: CLIInteractionData) -> CLIInteractionData:
    """匿名化交互數據"""
    
    # 用戶標識哈希化
    if interaction.user_hash:
        interaction.user_hash = hashlib.sha256(interaction.user_hash.encode()).hexdigest()[:16]
    
    # 移除環境敏感信息
    safe_env_info = {
        "python_version": interaction.environment_info.get("python_version"),
        "platform": interaction.environment_info.get("platform"),
        "timestamp": interaction.environment_info.get("timestamp")
    }
    interaction.environment_info = safe_env_info
    
    # 清理命令中的敏感信息
    interaction.command = sanitize_command(interaction.command)
    
    return interaction
```

### 2. 隱私合規檢查清單

- [ ] **個人身份信息 (PII)** - 已移除或匿名化
- [ ] **聯繫信息** - 郵箱、電話已清理
- [ ] **財務信息** - 信用卡、銀行信息已清理
- [ ] **技術憑證** - API密鑰、密碼已清理
- [ ] **網絡信息** - IP地址、主機名已匿名化
- [ ] **用戶標識** - 已哈希化處理

---

## 🔧 數據清理流程

### 1. 自動清理管道

```python
class DataCleaningPipeline:
    """數據清理管道"""
    
    def __init__(self):
        self.cleaners = [
            DuplicateRemover(),
            FormatStandardizer(),
            OutlierDetector(),
            IncompleteDataHandler(),
            PrivacyProtector()
        ]
    
    def clean_batch(self, interactions: List[CLIInteractionData]) -> List[CLIInteractionData]:
        """批量清理數據"""
        
        cleaned_data = interactions
        
        for cleaner in self.cleaners:
            cleaned_data = cleaner.process(cleaned_data)
            logger.info(f"{cleaner.__class__.__name__}: {len(cleaned_data)} records remaining")
        
        return cleaned_data
```

### 2. 清理規則

#### A. 重複數據處理
```python
class DuplicateRemover:
    """重複數據移除器"""
    
    def identify_duplicates(self, interactions: List[CLIInteractionData]) -> List[str]:
        """識別重複數據"""
        
        seen_signatures = set()
        duplicates = []
        
        for interaction in interactions:
            # 創建數據簽名
            signature = self.create_signature(interaction)
            
            if signature in seen_signatures:
                duplicates.append(interaction.interaction_id)
            else:
                seen_signatures.add(signature)
        
        return duplicates
    
    def create_signature(self, interaction: CLIInteractionData) -> str:
        """創建數據簽名"""
        
        key_fields = [
            interaction.command,
            json.dumps(interaction.arguments, sort_keys=True),
            interaction.task_type.value,
            str(interaction.execution_time),
            str(interaction.accuracy_score)
        ]
        
        return hashlib.md5("|".join(key_fields).encode()).hexdigest()
```

#### B. 異常值檢測
```python
class OutlierDetector:
    """異常值檢測器"""
    
    def detect_execution_time_outliers(self, interactions: List[CLIInteractionData]) -> List[str]:
        """檢測執行時間異常值"""
        
        execution_times = [i.execution_time for i in interactions if i.execution_time > 0]
        
        if len(execution_times) < 10:
            return []  # 數據太少，不檢測異常值
        
        Q1 = np.percentile(execution_times, 25)
        Q3 = np.percentile(execution_times, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = []
        for interaction in interactions:
            if (interaction.execution_time < lower_bound or 
                interaction.execution_time > upper_bound):
                outliers.append(interaction.interaction_id)
        
        return outliers
```

---

## 📈 質量監控儀表板

### 1. 實時質量指標

```python
class QualityDashboard:
    """質量監控儀表板"""
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """獲取實時質量指標"""
        
        recent_data = self.get_recent_interactions(hours=24)
        
        return {
            "data_volume": {
                "last_24h": len(recent_data),
                "hourly_average": len(recent_data) / 24,
                "trend": self.calculate_volume_trend()
            },
            "quality_scores": {
                "average": np.mean([self.calculate_quality_score(i) for i in recent_data]),
                "distribution": self.get_quality_distribution(recent_data),
                "trend": self.calculate_quality_trend()
            },
            "error_rates": {
                "collection_errors": self.get_collection_error_rate(),
                "validation_failures": self.get_validation_failure_rate(),
                "privacy_violations": self.get_privacy_violation_rate()
            },
            "completeness": {
                "required_fields": self.calculate_field_completeness(recent_data),
                "optional_fields": self.calculate_optional_completeness(recent_data)
            }
        }
```

### 2. 質量報警機制

```python
class QualityAlertSystem:
    """質量報警系統"""
    
    ALERT_THRESHOLDS = {
        "low_data_volume": 10,      # 每小時少於10個交互
        "low_quality_score": 0.7,   # 平均質量分數低於0.7
        "high_error_rate": 0.05,    # 錯誤率高於5%
        "privacy_violation": 1      # 任何隱私違規
    }
    
    def check_alerts(self) -> List[Alert]:
        """檢查報警條件"""
        
        alerts = []
        metrics = self.get_current_metrics()
        
        # 檢查數據量
        if metrics["hourly_volume"] < self.ALERT_THRESHOLDS["low_data_volume"]:
            alerts.append(Alert(
                type="low_data_volume",
                severity="warning",
                message=f"數據量過低: {metrics['hourly_volume']}/小時"
            ))
        
        # 檢查質量分數
        if metrics["avg_quality"] < self.ALERT_THRESHOLDS["low_quality_score"]:
            alerts.append(Alert(
                type="low_quality_score",
                severity="warning",
                message=f"質量分數過低: {metrics['avg_quality']:.3f}"
            ))
        
        # 檢查隱私違規
        if metrics["privacy_violations"] > 0:
            alerts.append(Alert(
                type="privacy_violation",
                severity="critical",
                message=f"發現隱私違規: {metrics['privacy_violations']}次"
            ))
        
        return alerts
```

---

## 🎯 質量改進建議

### 1. 自動質量改進

```python
class QualityImprover:
    """質量改進器"""
    
    def suggest_improvements(self, quality_report: QualityReport) -> List[Improvement]:
        """建議質量改進措施"""
        
        improvements = []
        
        # 基於質量報告生成建議
        if quality_report.completeness_score < 0.9:
            improvements.append(Improvement(
                type="completeness",
                priority="high",
                action="增強必需字段驗證",
                expected_impact="提升完整性10-15%"
            ))
        
        if quality_report.consistency_score < 0.8:
            improvements.append(Improvement(
                type="consistency",
                priority="medium",
                action="標準化數據格式",
                expected_impact="提升一致性15-20%"
            ))
        
        return improvements
```

### 2. 質量提升路線圖

#### 短期目標 (1-2週)
- [ ] 實現實時質量檢查
- [ ] 建立基本報警機制
- [ ] 完善隱私保護

#### 中期目標 (1個月)
- [ ] 部署自動清理管道
- [ ] 建立質量監控儀表板
- [ ] 實現異常檢測

#### 長期目標 (2-3個月)
- [ ] 機器學習質量評估
- [ ] 自動質量改進
- [ ] 完整質量管理體系

---

## 📋 質量控制檢查清單

### 數據收集階段
- [ ] 必需字段完整性檢查
- [ ] 數據類型驗證
- [ ] 值範圍檢查
- [ ] 隱私信息掃描
- [ ] 格式一致性驗證

### 數據存儲階段
- [ ] 重複數據檢測
- [ ] 數據完整性校驗
- [ ] 索引一致性檢查
- [ ] 備份完整性驗證

### 數據處理階段
- [ ] 異常值檢測
- [ ] 數據清理驗證
- [ ] 轉換正確性檢查
- [ ] 聚合結果驗證

### 數據使用階段
- [ ] 訓練數據質量評估
- [ ] 模型性能相關性分析
- [ ] 數據偏差檢測
- [ ] 結果可解釋性驗證

---

## 🔄 持續質量改進

### 1. 質量反饋循環

```
數據收集 → 質量檢查 → 問題識別 → 改進措施 → 效果評估 → 流程優化
    ↑                                                           ↓
    ←←←←←←←←←←←←←←← 持續改進 ←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

### 2. 質量文化建設

- **質量意識** - 所有參與者都重視數據質量
- **責任明確** - 每個環節都有質量責任人
- **持續改進** - 定期評估和優化質量流程
- **工具支持** - 提供充分的質量控制工具

這個質量控制機制確保CLI數據能夠滿足訓練和分析的高質量要求，為PowerAutomation系統的持續改進提供可靠的數據基礎。

