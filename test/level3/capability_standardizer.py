#!/usr/bin/env python3
"""
MCP能力聲明標準化模組
標準化MCP適配器的能力聲明格式和驗證機制

包括：
- 能力聲明格式標準化
- 能力驗證機制
- 能力文檔生成
- 能力兼容性檢查
- 能力版本管理
"""

import sys
import os
import json
import logging
import re
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import jsonschema

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

class CapabilityType(Enum):
    """能力類型枚舉"""
    PROCESSING = "processing"
    STORAGE = "storage"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    AUTOMATION = "automation"
    SECURITY = "security"

class CapabilityLevel(Enum):
    """能力等級枚舉"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class StandardCapability:
    """標準化能力定義"""
    name: str
    type: CapabilityType
    level: CapabilityLevel
    description: str
    version: str
    operations: List[str]
    parameters: Dict[str, Any]
    dependencies: List[str]
    metadata: Dict[str, Any]

@dataclass
class CapabilityValidationResult:
    """能力驗證結果"""
    adapter_name: str
    capability_name: str
    is_valid: bool
    compliance_score: float
    issues: List[str]
    suggestions: List[str]
    details: Dict[str, Any]

class MCPCapabilityStandardizer:
    """MCP能力聲明標準化器"""
    
    def __init__(self):
        self.capability_schema = self._create_capability_schema()
        self.standard_capabilities = self._load_standard_capabilities()
        self.validation_results = []
        
    def _create_capability_schema(self) -> Dict[str, Any]:
        """創建能力聲明JSON Schema"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "MCP Capability Declaration Schema",
            "type": "object",
            "required": ["name", "version", "description", "capabilities"],
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9_]*$",
                    "description": "適配器名稱，使用小寫字母、數字和下劃線"
                },
                "version": {
                    "type": "string",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$",
                    "description": "版本號，遵循語義化版本規範"
                },
                "description": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 500,
                    "description": "適配器描述，10-500字符"
                },
                "capabilities": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "level", "operations"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "能力名稱"
                            },
                            "type": {
                                "type": "string",
                                "enum": [t.value for t in CapabilityType],
                                "description": "能力類型"
                            },
                            "level": {
                                "type": "string",
                                "enum": [l.value for l in CapabilityLevel],
                                "description": "能力等級"
                            },
                            "description": {
                                "type": "string",
                                "minLength": 5,
                                "description": "能力描述"
                            },
                            "operations": {
                                "type": "array",
                                "minItems": 1,
                                "items": {
                                    "type": "string"
                                },
                                "description": "支持的操作列表"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "操作參數定義"
                            },
                            "dependencies": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "依賴的其他能力"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "額外的元數據"
                            }
                        }
                    }
                },
                "supported_operations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "適配器支持的所有操作"
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "author": {"type": "string"},
                        "license": {"type": "string"},
                        "homepage": {"type": "string"},
                        "documentation": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    
    def _load_standard_capabilities(self) -> Dict[str, StandardCapability]:
        """載入標準能力定義"""
        return {
            "data_processing": StandardCapability(
                name="data_processing",
                type=CapabilityType.PROCESSING,
                level=CapabilityLevel.BASIC,
                description="基本數據處理能力",
                version="1.0.0",
                operations=["process", "transform", "validate"],
                parameters={
                    "input_format": ["json", "text", "binary"],
                    "output_format": ["json", "text", "binary"],
                    "max_size": "10MB"
                },
                dependencies=[],
                metadata={"category": "core"}
            ),
            "memory_management": StandardCapability(
                name="memory_management",
                type=CapabilityType.STORAGE,
                level=CapabilityLevel.INTERMEDIATE,
                description="記憶體管理和存儲能力",
                version="1.0.0",
                operations=["store", "retrieve", "update", "delete", "search"],
                parameters={
                    "storage_type": ["memory", "disk", "database"],
                    "max_capacity": "1GB",
                    "persistence": True
                },
                dependencies=["data_processing"],
                metadata={"category": "storage"}
            ),
            "api_integration": StandardCapability(
                name="api_integration",
                type=CapabilityType.INTEGRATION,
                level=CapabilityLevel.ADVANCED,
                description="外部API集成能力",
                version="1.0.0",
                operations=["connect", "authenticate", "request", "response"],
                parameters={
                    "protocols": ["http", "https", "websocket"],
                    "auth_methods": ["api_key", "oauth", "basic"],
                    "rate_limit": "100/min"
                },
                dependencies=["data_processing"],
                metadata={"category": "integration"}
            ),
            "monitoring": StandardCapability(
                name="monitoring",
                type=CapabilityType.MONITORING,
                level=CapabilityLevel.INTERMEDIATE,
                description="系統監控和指標收集能力",
                version="1.0.0",
                operations=["monitor", "collect_metrics", "alert", "report"],
                parameters={
                    "metrics": ["performance", "errors", "usage"],
                    "alert_channels": ["email", "webhook", "log"],
                    "retention": "30d"
                },
                dependencies=[],
                metadata={"category": "monitoring"}
            )
        }
    
    def validate_capability_declaration(self, adapter_name: str, capability_declaration: Dict[str, Any]) -> CapabilityValidationResult:
        """驗證能力聲明"""
        issues = []
        suggestions = []
        details = {}
        
        # JSON Schema驗證
        try:
            jsonschema.validate(capability_declaration, self.capability_schema)
            details["schema_valid"] = True
        except jsonschema.ValidationError as e:
            issues.append(f"Schema驗證失敗: {e.message}")
            details["schema_valid"] = False
            details["schema_error"] = str(e)
        
        # 語義驗證
        semantic_score = self._validate_semantic_correctness(capability_declaration, issues, suggestions)
        details["semantic_score"] = semantic_score
        
        # 完整性檢查
        completeness_score = self._validate_completeness(capability_declaration, issues, suggestions)
        details["completeness_score"] = completeness_score
        
        # 一致性檢查
        consistency_score = self._validate_consistency(capability_declaration, issues, suggestions)
        details["consistency_score"] = consistency_score
        
        # 標準符合性檢查
        standard_score = self._validate_standard_compliance(capability_declaration, issues, suggestions)
        details["standard_score"] = standard_score
        
        # 計算總體合規分數
        compliance_score = (semantic_score + completeness_score + consistency_score + standard_score) / 4
        
        # 判斷是否有效
        is_valid = len(issues) == 0 and compliance_score >= 0.8
        
        return CapabilityValidationResult(
            adapter_name=adapter_name,
            capability_name=capability_declaration.get("name", "unknown"),
            is_valid=is_valid,
            compliance_score=compliance_score,
            issues=issues,
            suggestions=suggestions,
            details=details
        )
    
    def _validate_semantic_correctness(self, declaration: Dict[str, Any], issues: List[str], suggestions: List[str]) -> float:
        """驗證語義正確性"""
        score = 1.0
        
        # 檢查名稱語義
        name = declaration.get("name", "")
        if not re.match(r"^[a-z][a-z0-9_]*$", name):
            issues.append("適配器名稱應使用小寫字母、數字和下劃線")
            score -= 0.2
        
        # 檢查描述質量
        description = declaration.get("description", "")
        if len(description) < 10:
            issues.append("描述過短，應至少包含10個字符")
            score -= 0.2
        elif len(description) > 500:
            issues.append("描述過長，應不超過500個字符")
            score -= 0.1
        
        # 檢查版本格式
        version = declaration.get("version", "")
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            issues.append("版本號應遵循語義化版本規範 (x.y.z)")
            score -= 0.2
        
        # 檢查能力定義
        capabilities = declaration.get("capabilities", [])
        if not capabilities:
            issues.append("至少應定義一個能力")
            score -= 0.3
        
        for cap in capabilities:
            if not cap.get("operations"):
                issues.append(f"能力 '{cap.get('name', 'unknown')}' 缺少操作定義")
                score -= 0.1
        
        return max(0.0, score)
    
    def _validate_completeness(self, declaration: Dict[str, Any], issues: List[str], suggestions: List[str]) -> float:
        """驗證完整性"""
        score = 1.0
        required_fields = ["name", "version", "description", "capabilities"]
        
        for field in required_fields:
            if field not in declaration:
                issues.append(f"缺少必需字段: {field}")
                score -= 0.25
        
        # 檢查能力完整性
        capabilities = declaration.get("capabilities", [])
        for cap in capabilities:
            required_cap_fields = ["name", "type", "level", "operations"]
            for field in required_cap_fields:
                if field not in cap:
                    issues.append(f"能力 '{cap.get('name', 'unknown')}' 缺少字段: {field}")
                    score -= 0.1
        
        # 建議添加可選字段
        optional_fields = ["supported_operations", "metadata"]
        for field in optional_fields:
            if field not in declaration:
                suggestions.append(f"建議添加 {field} 字段以提供更完整的信息")
        
        return max(0.0, score)
    
    def _validate_consistency(self, declaration: Dict[str, Any], issues: List[str], suggestions: List[str]) -> float:
        """驗證一致性"""
        score = 1.0
        
        # 檢查操作一致性
        all_operations = set()
        capabilities = declaration.get("capabilities", [])
        
        for cap in capabilities:
            operations = cap.get("operations", [])
            all_operations.update(operations)
        
        declared_operations = set(declaration.get("supported_operations", []))
        
        if declared_operations and all_operations != declared_operations:
            missing_ops = all_operations - declared_operations
            extra_ops = declared_operations - all_operations
            
            if missing_ops:
                issues.append(f"supported_operations 缺少操作: {list(missing_ops)}")
                score -= 0.2
            
            if extra_ops:
                issues.append(f"supported_operations 包含未定義的操作: {list(extra_ops)}")
                score -= 0.2
        
        # 檢查依賴一致性
        capability_names = {cap.get("name") for cap in capabilities}
        for cap in capabilities:
            dependencies = cap.get("dependencies", [])
            for dep in dependencies:
                if dep not in capability_names and dep not in self.standard_capabilities:
                    issues.append(f"能力 '{cap.get('name')}' 依賴未定義的能力: {dep}")
                    score -= 0.1
        
        return max(0.0, score)
    
    def _validate_standard_compliance(self, declaration: Dict[str, Any], issues: List[str], suggestions: List[str]) -> float:
        """驗證標準符合性"""
        score = 1.0
        
        capabilities = declaration.get("capabilities", [])
        
        for cap in capabilities:
            cap_type = cap.get("type")
            cap_level = cap.get("level")
            
            # 檢查類型是否有效
            if cap_type not in [t.value for t in CapabilityType]:
                issues.append(f"能力 '{cap.get('name')}' 使用了無效的類型: {cap_type}")
                score -= 0.2
            
            # 檢查等級是否有效
            if cap_level not in [l.value for l in CapabilityLevel]:
                issues.append(f"能力 '{cap.get('name')}' 使用了無效的等級: {cap_level}")
                score -= 0.2
            
            # 檢查是否符合標準能力定義
            cap_name = cap.get("name")
            if cap_name in self.standard_capabilities:
                standard_cap = self.standard_capabilities[cap_name]
                
                if cap_type != standard_cap.type.value:
                    suggestions.append(f"能力 '{cap_name}' 的類型建議使用標準類型: {standard_cap.type.value}")
                
                if cap_level != standard_cap.level.value:
                    suggestions.append(f"能力 '{cap_name}' 的等級建議使用標準等級: {standard_cap.level.value}")
        
        return max(0.0, score)
    
    def standardize_capability_declaration(self, adapter_name: str, current_declaration: Dict[str, Any]) -> Dict[str, Any]:
        """標準化能力聲明"""
        standardized = current_declaration.copy()
        
        # 確保基本結構
        if "name" not in standardized:
            standardized["name"] = adapter_name.lower().replace("-", "_")
        
        if "version" not in standardized:
            standardized["version"] = "1.0.0"
        
        if "description" not in standardized:
            standardized["description"] = f"MCP適配器: {adapter_name}"
        
        if "capabilities" not in standardized:
            standardized["capabilities"] = []
        
        # 標準化能力定義
        capabilities = standardized["capabilities"]
        for cap in capabilities:
            # 確保必需字段
            if "name" not in cap:
                cap["name"] = "unknown_capability"
            
            if "type" not in cap:
                cap["type"] = CapabilityType.PROCESSING.value
            
            if "level" not in cap:
                cap["level"] = CapabilityLevel.BASIC.value
            
            if "operations" not in cap:
                cap["operations"] = ["process"]
            
            if "description" not in cap:
                cap["description"] = f"能力: {cap['name']}"
            
            # 添加標準字段
            if "parameters" not in cap:
                cap["parameters"] = {}
            
            if "dependencies" not in cap:
                cap["dependencies"] = []
            
            if "metadata" not in cap:
                cap["metadata"] = {}
        
        # 生成supported_operations
        all_operations = set()
        for cap in capabilities:
            all_operations.update(cap.get("operations", []))
        
        standardized["supported_operations"] = sorted(list(all_operations))
        
        # 添加標準元數據
        if "metadata" not in standardized:
            standardized["metadata"] = {}
        
        metadata = standardized["metadata"]
        if "created_at" not in metadata:
            metadata["created_at"] = datetime.now().isoformat()
        
        if "standard_version" not in metadata:
            metadata["standard_version"] = "1.0.0"
        
        return standardized
    
    def generate_capability_documentation(self, declaration: Dict[str, Any]) -> str:
        """生成能力文檔"""
        name = declaration.get("name", "Unknown")
        version = declaration.get("version", "Unknown")
        description = declaration.get("description", "No description available")
        capabilities = declaration.get("capabilities", [])
        
        doc = f"""
# {name} MCP適配器

## 基本信息
- **名稱**: {name}
- **版本**: {version}
- **描述**: {description}

## 能力列表

"""
        
        for cap in capabilities:
            cap_name = cap.get("name", "Unknown")
            cap_type = cap.get("type", "Unknown")
            cap_level = cap.get("level", "Unknown")
            cap_desc = cap.get("description", "No description")
            operations = cap.get("operations", [])
            
            doc += f"""### {cap_name}
- **類型**: {cap_type}
- **等級**: {cap_level}
- **描述**: {cap_desc}
- **支持操作**: {', '.join(operations)}

"""
            
            # 添加參數信息
            parameters = cap.get("parameters", {})
            if parameters:
                doc += "**參數**:\n"
                for param, value in parameters.items():
                    doc += f"- `{param}`: {value}\n"
                doc += "\n"
            
            # 添加依賴信息
            dependencies = cap.get("dependencies", [])
            if dependencies:
                doc += f"**依賴**: {', '.join(dependencies)}\n\n"
        
        # 添加操作列表
        supported_operations = declaration.get("supported_operations", [])
        if supported_operations:
            doc += f"""## 支持的操作

{', '.join(supported_operations)}

"""
        
        # 添加元數據
        metadata = declaration.get("metadata", {})
        if metadata:
            doc += "## 元數據\n\n"
            for key, value in metadata.items():
                doc += f"- **{key}**: {value}\n"
        
        return doc
    
    def run_capability_standardization(self, adapter_name: str = None) -> List[CapabilityValidationResult]:
        """運行能力標準化測試"""
        logger.info("開始MCP能力聲明標準化...")
        
        # 發現適配器
        try:
            from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
            registry = SafeMCPRegistry()
            adapters = registry.list_adapters()
            
            # 轉換為字典格式
            adapter_dict = {}
            if isinstance(adapters, list):
                for item in adapters:
                    if isinstance(item, tuple) and len(item) >= 2:
                        name, instance = item[0], item[1]
                        adapter_dict[name] = {"name": name, "instance": instance}
                    elif hasattr(item, 'name'):
                        adapter_dict[item.name] = {"name": item.name, "instance": item}
            elif isinstance(adapters, dict):
                adapter_dict = adapters
                
        except Exception as e:
            logger.error(f"無法從註冊表獲取適配器: {e}")
            return []
        
        # 選擇要測試的適配器
        if adapter_name:
            if adapter_name not in adapter_dict:
                logger.error(f"未找到適配器: {adapter_name}")
                return []
            test_adapters = {adapter_name: adapter_dict[adapter_name]}
        else:
            # 限制測試數量
            test_adapters = dict(list(adapter_dict.items())[:5])
        
        results = []
        
        for name, adapter_info in test_adapters.items():
            adapter_instance = adapter_info.get("instance")
            if not adapter_instance:
                logger.warning(f"無法獲取適配器實例: {name}")
                continue
            
            logger.info(f"標準化適配器能力聲明: {name}")
            
            # 獲取當前能力聲明
            current_declaration = self._extract_capability_declaration(name, adapter_instance)
            
            # 驗證能力聲明
            validation_result = self.validate_capability_declaration(name, current_declaration)
            results.append(validation_result)
            
            # 生成標準化聲明
            standardized_declaration = self.standardize_capability_declaration(name, current_declaration)
            
            # 保存標準化聲明
            self._save_standardized_declaration(name, standardized_declaration)
            
            # 生成文檔
            documentation = self.generate_capability_documentation(standardized_declaration)
            self._save_capability_documentation(name, documentation)
        
        self.validation_results = results
        logger.info(f"能力標準化完成，處理了 {len(results)} 個適配器")
        
        return results
    
    def _extract_capability_declaration(self, adapter_name: str, adapter_instance: Any) -> Dict[str, Any]:
        """提取適配器的能力聲明"""
        declaration = {
            "name": adapter_name,
            "version": "1.0.0",
            "description": f"MCP適配器: {adapter_name}",
            "capabilities": []
        }
        
        # 嘗試從get_capabilities方法獲取
        if hasattr(adapter_instance, 'get_capabilities'):
            try:
                capabilities = adapter_instance.get_capabilities()
                if isinstance(capabilities, list):
                    declaration["capabilities"] = [
                        {
                            "name": cap if isinstance(cap, str) else str(cap),
                            "type": CapabilityType.PROCESSING.value,
                            "level": CapabilityLevel.BASIC.value,
                            "description": f"能力: {cap}",
                            "operations": ["process"]
                        }
                        for cap in capabilities
                    ]
                elif isinstance(capabilities, dict):
                    declaration.update(capabilities)
            except Exception as e:
                logger.warning(f"無法獲取 {adapter_name} 的能力聲明: {e}")
        
        # 從類文檔和方法推斷能力
        if hasattr(adapter_instance, '__doc__') and adapter_instance.__doc__:
            declaration["description"] = adapter_instance.__doc__.strip()
        
        # 檢查常見方法
        common_methods = ["process", "initialize", "cleanup", "get_status"]
        available_operations = []
        for method in common_methods:
            if hasattr(adapter_instance, method):
                available_operations.append(method)
        
        if available_operations and not declaration["capabilities"]:
            declaration["capabilities"] = [{
                "name": "basic_processing",
                "type": CapabilityType.PROCESSING.value,
                "level": CapabilityLevel.BASIC.value,
                "description": "基本處理能力",
                "operations": available_operations
            }]
        
        return declaration
    
    def _save_standardized_declaration(self, adapter_name: str, declaration: Dict[str, Any]):
        """保存標準化聲明"""
        output_dir = Path("standardized_capabilities")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{adapter_name}_capability.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(declaration, f, indent=2, ensure_ascii=False)
        
        logger.info(f"標準化聲明已保存到: {output_file}")
    
    def _save_capability_documentation(self, adapter_name: str, documentation: str):
        """保存能力文檔"""
        output_dir = Path("capability_docs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{adapter_name}_capabilities.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        logger.info(f"能力文檔已保存到: {output_file}")
    
    def generate_standardization_report(self) -> str:
        """生成標準化報告"""
        if not self.validation_results:
            return "# MCP能力聲明標準化報告\n\n無測試結果可用。"
        
        total_adapters = len(self.validation_results)
        valid_adapters = sum(1 for r in self.validation_results if r.is_valid)
        avg_compliance = sum(r.compliance_score for r in self.validation_results) / total_adapters
        
        report = f"""
# MCP能力聲明標準化報告

## 📊 總體統計
- **測試時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **測試適配器數**: {total_adapters}
- **符合標準數**: {valid_adapters}
- **符合率**: {(valid_adapters/total_adapters*100):.1f}%
- **平均合規分數**: {avg_compliance:.1%}

## 🔍 詳細結果
"""
        
        for result in self.validation_results:
            status = "✅" if result.is_valid else "❌"
            
            report += f"""
### {status} {result.adapter_name}
- **合規分數**: {result.compliance_score:.1%}
- **問題數量**: {len(result.issues)}
- **建議數量**: {len(result.suggestions)}

"""
            
            if result.issues:
                report += "**問題**:\n"
                for issue in result.issues[:3]:
                    report += f"- ⚠️ {issue}\n"
                if len(result.issues) > 3:
                    report += f"- ... 還有 {len(result.issues) - 3} 個問題\n"
                report += "\n"
            
            if result.suggestions:
                report += "**建議**:\n"
                for suggestion in result.suggestions[:3]:
                    report += f"- 💡 {suggestion}\n"
                if len(result.suggestions) > 3:
                    report += f"- ... 還有 {len(result.suggestions) - 3} 個建議\n"
                report += "\n"
        
        report += f"""
## 📋 標準化改進

### 能力聲明標準
1. **命名規範**: 使用小寫字母、數字和下劃線
2. **版本管理**: 遵循語義化版本規範
3. **描述質量**: 提供清晰、詳細的描述
4. **能力分類**: 使用標準的能力類型和等級
5. **操作定義**: 明確列出支持的操作

### 改進建議
1. 統一能力聲明格式
2. 完善能力描述和文檔
3. 建立能力依賴關係
4. 實施版本兼容性檢查
5. 提供能力測試和驗證

## 🏆 標準化評估

{'✅ 能力聲明達到標準化要求' if (valid_adapters/total_adapters) >= 0.8 else '⚠️ 能力聲明需要標準化改進' if (valid_adapters/total_adapters) >= 0.6 else '❌ 能力聲明未達到標準化要求'}

**整體符合率**: {(valid_adapters/total_adapters*100):.1f}%
**平均合規分數**: {avg_compliance:.1%}
"""
        
        return report

if __name__ == "__main__":
    standardizer = MCPCapabilityStandardizer()
    results = standardizer.run_capability_standardization()
    
    # 生成報告
    report = standardizer.generate_standardization_report()
    
    # 保存報告
    report_file = Path("mcp_capability_standardization_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ MCP能力聲明標準化完成")
    print(f"📄 報告已保存到: {report_file}")
    if results:
        valid_count = sum(1 for r in results if r.is_valid)
        avg_score = sum(r.compliance_score for r in results) / len(results)
        print(f"🎯 標準化結果: {valid_count}/{len(results)} 個適配器符合標準")
        print(f"📊 平均合規分數: {avg_score:.1%}")
    else:
        print("⚠️ 未找到可處理的適配器")

