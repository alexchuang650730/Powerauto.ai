#!/usr/bin/env python3
"""
PowerAutomation Linux環境閉環系統

整合Manus交互分類、KiloCode工具生成、文檔分析等功能
實現完整的Linux環境閉環學習和改進系統
"""

import os
import json
import time
import hashlib
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import subprocess
import shutil
import pandas as pd
import numpy as np
from PIL import Image
import requests

# 導入之前的系統
from interaction_log_manager import InteractionLogManager, InteractionType, DeliverableType
from rl_srt_learning_system import RLSRTLearningEngine, LearningExperience, LearningMode

class DocumentType(Enum):
    """文檔類型枚舉"""
    BUSINESS_PPT = "business_ppt"
    TECHNICAL_DOC = "technical_doc"
    FINANCIAL_REPORT = "financial_report"
    MARKET_ANALYSIS = "market_analysis"
    PRODUCT_SPEC = "product_spec"
    INVESTMENT_PITCH = "investment_pitch"

class AnalysisTemplate(Enum):
    """分析模板枚舉"""
    BUSINESS_STRATEGY = "business_strategy"
    TECHNICAL_REVIEW = "technical_review"
    FINANCIAL_ANALYSIS = "financial_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    PERFORMANCE_METRICS = "performance_metrics"

@dataclass
class DocumentAnalysisTask:
    """文檔分析任務"""
    task_id: str
    document_path: str
    document_type: DocumentType
    analysis_template: AnalysisTemplate
    user_requirements: str
    created_at: str
    status: str
    results: Dict[str, Any]

@dataclass
class KiloCodeTool:
    """KiloCode工具"""
    tool_id: str
    name: str
    description: str
    generated_code: str
    input_parameters: Dict[str, Any]
    output_format: str
    execution_count: int
    success_rate: float
    created_at: str

class LinuxClosedLoopSystem:
    """Linux環境閉環系統"""
    
    def __init__(self, base_dir: str = "/home/ubuntu/Powerauto.ai/linux_closed_loop"):
        self.base_dir = Path(base_dir)
        self.setup_system()
        
        # 初始化子系統
        self.log_manager = InteractionLogManager()
        self.rl_srt_engine = RLSRTLearningEngine(self.log_manager)
        
        # 系統狀態
        self.kilocode_tools = {}
        self.analysis_templates = {}
        self.execution_history = []
        self.learning_metrics = {}
        
    def setup_system(self):
        """設置系統"""
        directories = [
            "documents",
            "analysis_results",
            "kilocode_tools",
            "templates",
            "execution_logs",
            "learning_data",
            "performance_metrics",
            "closed_loop_reports"
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"✅ Linux閉環系統已設置: {self.base_dir}")
        
        # 初始化分析模板
        self.initialize_analysis_templates()
    
    def initialize_analysis_templates(self):
        """初始化分析模板"""
        templates = {
            AnalysisTemplate.BUSINESS_STRATEGY: {
                "name": "商業策略分析",
                "description": "分析商業計劃、市場策略、競爭優勢",
                "analysis_points": [
                    "市場機會評估",
                    "競爭優勢分析", 
                    "商業模式評估",
                    "風險因素識別",
                    "財務可行性",
                    "執行計劃評估"
                ],
                "output_format": "structured_report",
                "kilocode_tools": ["document_parser", "data_analyzer", "report_generator"]
            },
            AnalysisTemplate.TECHNICAL_REVIEW: {
                "name": "技術文檔審查",
                "description": "審查技術架構、代碼質量、系統設計",
                "analysis_points": [
                    "架構設計評估",
                    "技術選型分析",
                    "性能指標評估",
                    "安全性審查",
                    "可擴展性分析",
                    "維護性評估"
                ],
                "output_format": "technical_report",
                "kilocode_tools": ["code_analyzer", "architecture_reviewer", "security_scanner"]
            },
            AnalysisTemplate.FINANCIAL_ANALYSIS: {
                "name": "財務分析",
                "description": "分析財務報表、投資回報、成本效益",
                "analysis_points": [
                    "收入分析",
                    "成本結構分析",
                    "盈利能力評估",
                    "現金流分析",
                    "投資回報率",
                    "財務風險評估"
                ],
                "output_format": "financial_dashboard",
                "kilocode_tools": ["financial_calculator", "trend_analyzer", "risk_assessor"]
            }
        }
        
        for template_type, template_data in templates.items():
            template_file = self.base_dir / "templates" / f"{template_type.value}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        self.analysis_templates = templates
        self.logger.info(f"✅ 初始化了 {len(templates)} 個分析模板")
    
    def create_kilocode_tool(self, name: str, description: str, 
                           task_requirements: str) -> KiloCodeTool:
        """創建KiloCode工具"""
        tool_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:12]
        
        # 根據需求生成代碼
        generated_code = self.generate_tool_code(name, description, task_requirements)
        
        tool = KiloCodeTool(
            tool_id=tool_id,
            name=name,
            description=description,
            generated_code=generated_code,
            input_parameters=self.extract_input_parameters(generated_code),
            output_format="json",
            execution_count=0,
            success_rate=0.0,
            created_at=datetime.now().isoformat()
        )
        
        # 保存工具
        tool_file = self.base_dir / "kilocode_tools" / f"{tool_id}.py"
        with open(tool_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        # 保存工具元數據
        metadata_file = self.base_dir / "kilocode_tools" / f"{tool_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            tool_dict = asdict(tool)
            json.dump(tool_dict, f, indent=2, ensure_ascii=False)
        
        self.kilocode_tools[tool_id] = tool
        self.logger.info(f"✅ KiloCode工具已創建: {tool_id} - {name}")
        
        return tool
    
    def generate_tool_code(self, name: str, description: str, requirements: str) -> str:
        """生成工具代碼"""
        if "文檔分析" in description or "document" in description.lower():
            return self.generate_document_analyzer_code(name, requirements)
        elif "數據分析" in description or "data" in description.lower():
            return self.generate_data_analyzer_code(name, requirements)
        elif "報告生成" in description or "report" in description.lower():
            return self.generate_report_generator_code(name, requirements)
        else:
            return self.generate_generic_tool_code(name, description, requirements)
    
    def generate_document_analyzer_code(self, name: str, requirements: str) -> str:
        """生成文檔分析器代碼"""
        return f'''#!/usr/bin/env python3
"""
{name} - 自動生成的文檔分析工具
需求: {requirements}
"""

import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

def analyze_document(document_path: str, analysis_type: str = "general") -> dict:
    """分析文檔內容"""
    results = {{
        "tool_name": "{name}",
        "document_path": document_path,
        "analysis_type": analysis_type,
        "timestamp": datetime.now().isoformat(),
        "analysis_results": {{}},
        "success": False
    }}
    
    try:
        # 檢查文檔是否存在
        if not os.path.exists(document_path):
            results["error"] = "文檔不存在"
            return results
        
        # 獲取文檔基本信息
        file_info = os.stat(document_path)
        results["analysis_results"]["file_info"] = {{
            "size_mb": file_info.st_size / (1024 * 1024),
            "modified_time": datetime.fromtimestamp(file_info.st_mtime).isoformat(),
            "file_extension": Path(document_path).suffix
        }}
        
        # 根據文件類型進行分析
        file_ext = Path(document_path).suffix.lower()
        
        if file_ext in ['.txt', '.md']:
            results["analysis_results"]["content_analysis"] = analyze_text_content(document_path)
        elif file_ext in ['.json']:
            results["analysis_results"]["json_analysis"] = analyze_json_content(document_path)
        elif file_ext in ['.csv']:
            results["analysis_results"]["data_analysis"] = analyze_csv_content(document_path)
        else:
            results["analysis_results"]["general_info"] = "文檔類型已識別，但需要專門的解析器"
        
        results["success"] = True
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

def analyze_text_content(file_path: str) -> dict:
    """分析文本內容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {{
        "character_count": len(content),
        "word_count": len(content.split()),
        "line_count": len(content.split('\\n')),
        "has_chinese": any('\\u4e00' <= char <= '\\u9fff' for char in content),
        "sample_content": content[:200] + "..." if len(content) > 200 else content
    }}

def analyze_json_content(file_path: str) -> dict:
    """分析JSON內容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return {{
        "data_type": type(data).__name__,
        "keys_count": len(data.keys()) if isinstance(data, dict) else "N/A",
        "items_count": len(data) if isinstance(data, (list, dict)) else "N/A",
        "structure_sample": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
    }}

def analyze_csv_content(file_path: str) -> dict:
    """分析CSV內容"""
    df = pd.read_csv(file_path)
    
    return {{
        "rows_count": len(df),
        "columns_count": len(df.columns),
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.to_dict(),
        "sample_data": df.head().to_dict()
    }}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = analyze_document(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("使用方法: python {{}} <document_path>".format(sys.argv[0]))
'''
    
    def generate_data_analyzer_code(self, name: str, requirements: str) -> str:
        """生成數據分析器代碼"""
        return f'''#!/usr/bin/env python3
"""
{name} - 自動生成的數據分析工具
需求: {requirements}
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(data_source: str, analysis_type: str = "descriptive") -> dict:
    """分析數據"""
    results = {{
        "tool_name": "{name}",
        "data_source": data_source,
        "analysis_type": analysis_type,
        "timestamp": datetime.now().isoformat(),
        "analysis_results": {{}},
        "success": False
    }}
    
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
        results["analysis_results"]["basic_stats"] = {{
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }}
        
        # 數值列統計
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            results["analysis_results"]["numeric_analysis"] = {{
                "descriptive_stats": df[numeric_columns].describe().to_dict(),
                "correlation_matrix": df[numeric_columns].corr().to_dict()
            }}
        
        # 分類列分析
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            results["analysis_results"]["categorical_analysis"] = {{}}
            for col in categorical_columns[:5]:  # 限制前5列
                results["analysis_results"]["categorical_analysis"][col] = {{
                    "unique_count": df[col].nunique(),
                    "top_values": df[col].value_counts().head().to_dict()
                }}
        
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
        print("使用方法: python {{}} <data_file>".format(sys.argv[0]))
'''
    
    def generate_report_generator_code(self, name: str, requirements: str) -> str:
        """生成報告生成器代碼"""
        return f'''#!/usr/bin/env python3
"""
{name} - 自動生成的報告生成工具
需求: {requirements}
"""

import json
from datetime import datetime
from pathlib import Path

def generate_report(data: dict, report_type: str = "analysis", output_path: str = None) -> dict:
    """生成報告"""
    results = {{
        "tool_name": "{name}",
        "report_type": report_type,
        "timestamp": datetime.now().isoformat(),
        "success": False
    }}
    
    try:
        # 生成報告內容
        if report_type == "analysis":
            report_content = generate_analysis_report(data)
        elif report_type == "summary":
            report_content = generate_summary_report(data)
        else:
            report_content = generate_generic_report(data)
        
        # 保存報告
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            results["output_file"] = output_path
        
        results["report_content"] = report_content
        results["content_length"] = len(report_content)
        results["success"] = True
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

def generate_analysis_report(data: dict) -> str:
    """生成分析報告"""
    report = f"""# 分析報告

## 報告概況
- 生成時間: {{datetime.now().isoformat()}}
- 數據來源: {{data.get('source', 'Unknown')}}

## 分析結果

"""
    
    for key, value in data.items():
        if isinstance(value, dict):
            report += f"### {{key}}\\n"
            for sub_key, sub_value in value.items():
                report += f"- **{{sub_key}}**: {{sub_value}}\\n"
            report += "\\n"
        else:
            report += f"- **{{key}}**: {{value}}\\n"
    
    return report

def generate_summary_report(data: dict) -> str:
    """生成摘要報告"""
    return f"""# 摘要報告

**生成時間**: {{datetime.now().isoformat()}}

## 關鍵指標
{{json.dumps(data, indent=2, ensure_ascii=False)}}

---
*此報告由PowerAutomation自動生成*
"""

def generate_generic_report(data: dict) -> str:
    """生成通用報告"""
    return f"""# 通用報告

{{json.dumps(data, indent=2, ensure_ascii=False)}}
"""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
        result = generate_report(data, sys.argv[2] if len(sys.argv) > 2 else "analysis")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("使用方法: python {{}} <data_file> [report_type]".format(sys.argv[0]))
'''
    
    def generate_generic_tool_code(self, name: str, description: str, requirements: str) -> str:
        """生成通用工具代碼"""
        return f'''#!/usr/bin/env python3
"""
{name} - 自動生成的工具
描述: {description}
需求: {requirements}
"""

import json
from datetime import datetime

def execute_tool(input_data: dict) -> dict:
    """執行工具"""
    results = {{
        "tool_name": "{name}",
        "description": "{description}",
        "timestamp": datetime.now().isoformat(),
        "input_data": input_data,
        "success": False
    }}
    
    try:
        # 工具邏輯
        processed_data = process_input(input_data)
        results["output_data"] = processed_data
        results["success"] = True
        
    except Exception as e:
        results["error"] = str(e)
    
    return results

def process_input(data: dict) -> dict:
    """處理輸入數據"""
    # 基本處理邏輯
    return {{
        "processed": True,
        "original_keys": list(data.keys()),
        "processing_time": datetime.now().isoformat()
    }}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
        result = execute_tool(input_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("使用方法: python {{}} <input_file>".format(sys.argv[0]))
'''
    
    def extract_input_parameters(self, code: str) -> Dict[str, Any]:
        """提取輸入參數"""
        # 簡化的參數提取邏輯
        parameters = {}
        
        if "document_path" in code:
            parameters["document_path"] = {"type": "string", "description": "文檔路徑"}
        if "data_source" in code:
            parameters["data_source"] = {"type": "string", "description": "數據源路徑"}
        if "analysis_type" in code:
            parameters["analysis_type"] = {"type": "string", "description": "分析類型"}
        if "output_path" in code:
            parameters["output_path"] = {"type": "string", "description": "輸出路徑"}
        
        return parameters
    
    def execute_kilocode_tool(self, tool_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行KiloCode工具"""
        if tool_id not in self.kilocode_tools:
            return {"error": f"工具不存在: {tool_id}"}
        
        tool = self.kilocode_tools[tool_id]
        tool_file = self.base_dir / "kilocode_tools" / f"{tool_id}.py"
        
        execution_result = {
            "tool_id": tool_id,
            "tool_name": tool.name,
            "execution_time": None,
            "success": False,
            "output": {},
            "error": None
        }
        
        try:
            start_time = time.time()
            
            # 準備輸入文件
            input_file = self.base_dir / "execution_logs" / f"input_{tool_id}_{int(time.time())}.json"
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(input_data, f, indent=2, ensure_ascii=False)
            
            # 執行工具
            result = subprocess.run(
                ["python3", str(tool_file), str(input_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            execution_time = time.time() - start_time
            execution_result["execution_time"] = execution_time
            
            if result.returncode == 0:
                try:
                    output_data = json.loads(result.stdout)
                    execution_result["output"] = output_data
                    execution_result["success"] = True
                    
                    # 更新工具統計
                    tool.execution_count += 1
                    tool.success_rate = (tool.success_rate * (tool.execution_count - 1) + 1) / tool.execution_count
                    
                except json.JSONDecodeError:
                    execution_result["output"] = {"raw_output": result.stdout}
                    execution_result["success"] = True
            else:
                execution_result["error"] = result.stderr
                
                # 更新工具統計
                tool.execution_count += 1
                tool.success_rate = (tool.success_rate * (tool.execution_count - 1)) / tool.execution_count
            
        except subprocess.TimeoutExpired:
            execution_result["error"] = "執行超時"
        except Exception as e:
            execution_result["error"] = str(e)
        
        # 記錄執行歷史
        self.execution_history.append(execution_result)
        
        # 保存執行日誌
        log_file = self.base_dir / "execution_logs" / f"execution_{tool_id}_{int(time.time())}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(execution_result, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ 工具執行完成: {tool_id} - 成功: {execution_result['success']}")
        
        return execution_result
    
    def analyze_document_with_template(self, document_path: str, 
                                     document_type: DocumentType,
                                     analysis_template: AnalysisTemplate) -> DocumentAnalysisTask:
        """使用模板分析文檔"""
        task_id = hashlib.md5(f"{document_path}{time.time()}".encode()).hexdigest()[:12]
        
        task = DocumentAnalysisTask(
            task_id=task_id,
            document_path=document_path,
            document_type=document_type,
            analysis_template=analysis_template,
            user_requirements=f"使用{analysis_template.value}模板分析{document_type.value}文檔",
            created_at=datetime.now().isoformat(),
            status="processing",
            results={}
        )
        
        try:
            # 獲取分析模板
            template_data = self.analysis_templates.get(analysis_template, {})
            required_tools = template_data.get("kilocode_tools", [])
            
            # 為每個所需工具創建或獲取KiloCode工具
            analysis_results = {}
            
            for tool_name in required_tools:
                # 檢查是否已有相應工具
                existing_tool = self.find_tool_by_name(tool_name)
                
                if not existing_tool:
                    # 創建新工具
                    tool_description = f"{tool_name}用於{analysis_template.value}分析"
                    tool_requirements = f"分析{document_type.value}文檔的{tool_name}功能"
                    existing_tool = self.create_kilocode_tool(tool_name, tool_description, tool_requirements)
                
                # 執行工具
                input_data = {
                    "document_path": document_path,
                    "analysis_type": analysis_template.value,
                    "document_type": document_type.value
                }
                
                execution_result = self.execute_kilocode_tool(existing_tool.tool_id, input_data)
                analysis_results[tool_name] = execution_result
            
            task.results = analysis_results
            task.status = "completed"
            
        except Exception as e:
            task.status = "failed"
            task.results = {"error": str(e)}
        
        # 保存任務結果
        task_file = self.base_dir / "analysis_results" / f"{task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            task_dict = asdict(task)
            # 轉換枚舉為字符串
            task_dict['document_type'] = task.document_type.value
            task_dict['analysis_template'] = task.analysis_template.value
            json.dump(task_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ 文檔分析任務完成: {task_id} - 狀態: {task.status}")
        
        return task
    
    def find_tool_by_name(self, tool_name: str) -> Optional[KiloCodeTool]:
        """根據名稱查找工具"""
        for tool in self.kilocode_tools.values():
            if tool_name in tool.name or tool.name in tool_name:
                return tool
        return None
    
    def create_learning_experience_from_execution(self, execution_result: Dict[str, Any]) -> LearningExperience:
        """從執行結果創建學習經驗"""
        experience_id = hashlib.md5(f"{execution_result.get('tool_id', '')}{time.time()}".encode()).hexdigest()[:12]
        
        # 構建狀態
        state = {
            "tool_id": execution_result.get("tool_id", ""),
            "tool_name": execution_result.get("tool_name", ""),
            "input_complexity": len(str(execution_result.get("input_data", {}))),
            "execution_context": "linux_environment"
        }
        
        # 構建動作
        action = {
            "tool_execution": True,
            "execution_strategy": "kilocode_generated",
            "resource_usage": execution_result.get("execution_time", 0)
        }
        
        # 計算獎勵
        reward = 0.0
        if execution_result.get("success", False):
            reward += 0.5  # 基礎成功獎勵
            
            # 基於執行時間的效率獎勵
            exec_time = execution_result.get("execution_time", 0)
            if exec_time < 5:  # 5秒內完成
                reward += 0.3
            elif exec_time < 10:  # 10秒內完成
                reward += 0.2
            
            # 基於輸出質量的獎勵
            output = execution_result.get("output", {})
            if isinstance(output, dict) and len(output) > 0:
                reward += 0.2
        
        # 構建下一狀態
        next_state = {
            "execution_completed": execution_result.get("success", False),
            "output_quality": len(str(execution_result.get("output", {}))),
            "error_occurred": execution_result.get("error") is not None,
            "tool_performance": execution_result.get("success", False)
        }
        
        experience = LearningExperience(
            experience_id=experience_id,
            timestamp=datetime.now().isoformat(),
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            metadata={
                "source": "kilocode_execution",
                "tool_id": execution_result.get("tool_id", ""),
                "execution_time": execution_result.get("execution_time", 0)
            },
            learning_mode=LearningMode.SYNCHRONOUS
        )
        
        return experience
    
    def run_closed_loop_cycle(self, user_request: str, document_path: str = None) -> Dict[str, Any]:
        """運行閉環循環"""
        cycle_id = hashlib.md5(f"{user_request}{time.time()}".encode()).hexdigest()[:12]
        
        cycle_result = {
            "cycle_id": cycle_id,
            "user_request": user_request,
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "learning_experiences": [],
            "performance_metrics": {},
            "success": False
        }
        
        try:
            # Phase 1: Manus分析和理解
            self.logger.info(f"🧠 Phase 1: Manus分析用戶請求")
            manus_analysis = self.analyze_user_request(user_request, document_path)
            cycle_result["phases"]["manus_analysis"] = manus_analysis
            
            # Phase 2: KiloCode工具生成
            self.logger.info(f"🔧 Phase 2: KiloCode工具生成")
            required_tools = manus_analysis.get("required_tools", [])
            generated_tools = []
            
            for tool_spec in required_tools:
                tool = self.create_kilocode_tool(
                    tool_spec["name"],
                    tool_spec["description"],
                    tool_spec["requirements"]
                )
                generated_tools.append(tool)
            
            cycle_result["phases"]["tool_generation"] = {
                "tools_created": len(generated_tools),
                "tool_ids": [t.tool_id for t in generated_tools]
            }
            
            # Phase 3: Linux環境執行
            self.logger.info(f"⚡ Phase 3: Linux環境執行")
            execution_results = []
            
            for tool in generated_tools:
                input_data = manus_analysis.get("tool_inputs", {}).get(tool.name, {})
                if document_path:
                    input_data["document_path"] = document_path
                
                exec_result = self.execute_kilocode_tool(tool.tool_id, input_data)
                execution_results.append(exec_result)
                
                # 創建學習經驗
                learning_exp = self.create_learning_experience_from_execution(exec_result)
                cycle_result["learning_experiences"].append(learning_exp)
            
            cycle_result["phases"]["execution"] = {
                "total_executions": len(execution_results),
                "successful_executions": len([r for r in execution_results if r.get("success", False)]),
                "execution_results": execution_results
            }
            
            # Phase 4: RL-SRT學習
            self.logger.info(f"🧠 Phase 4: RL-SRT學習")
            if cycle_result["learning_experiences"]:
                learning_results = self.rl_srt_engine.synchronous_learning(cycle_result["learning_experiences"])
                cycle_result["phases"]["learning"] = learning_results
            
            # Phase 5: 性能評估和反饋
            self.logger.info(f"📊 Phase 5: 性能評估")
            performance_metrics = self.calculate_cycle_performance(cycle_result)
            cycle_result["performance_metrics"] = performance_metrics
            
            cycle_result["success"] = True
            
        except Exception as e:
            cycle_result["error"] = str(e)
            self.logger.error(f"❌ 閉環循環失敗: {e}")
        
        # 保存循環結果
        cycle_file = self.base_dir / "closed_loop_reports" / f"cycle_{cycle_id}.json"
        with open(cycle_file, 'w', encoding='utf-8') as f:
            # 處理不可序列化的對象
            serializable_result = self.make_serializable(cycle_result)
            json.dump(serializable_result, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ 閉環循環完成: {cycle_id} - 成功: {cycle_result['success']}")
        
        return cycle_result
    
    def analyze_user_request(self, user_request: str, document_path: str = None) -> Dict[str, Any]:
        """分析用戶請求"""
        analysis = {
            "request": user_request,
            "document_path": document_path,
            "intent": "unknown",
            "required_tools": [],
            "tool_inputs": {},
            "complexity": "medium"
        }
        
        # 簡化的意圖識別
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["分析", "analyze", "review"]):
            analysis["intent"] = "analysis"
            if document_path:
                analysis["required_tools"].append({
                    "name": "document_analyzer",
                    "description": "分析文檔內容",
                    "requirements": f"分析文檔: {user_request}"
                })
                analysis["tool_inputs"]["document_analyzer"] = {"document_path": document_path}
        
        if any(word in request_lower for word in ["報告", "report", "總結"]):
            analysis["intent"] = "reporting"
            analysis["required_tools"].append({
                "name": "report_generator",
                "description": "生成報告",
                "requirements": f"生成報告: {user_request}"
            })
        
        if any(word in request_lower for word in ["數據", "data", "統計"]):
            analysis["intent"] = "data_analysis"
            analysis["required_tools"].append({
                "name": "data_analyzer",
                "description": "數據分析",
                "requirements": f"數據分析: {user_request}"
            })
        
        # 如果沒有識別出特定意圖，創建通用工具
        if not analysis["required_tools"]:
            analysis["required_tools"].append({
                "name": "general_processor",
                "description": "通用處理工具",
                "requirements": user_request
            })
        
        return analysis
    
    def calculate_cycle_performance(self, cycle_result: Dict[str, Any]) -> Dict[str, Any]:
        """計算循環性能"""
        metrics = {
            "overall_success_rate": 0.0,
            "average_execution_time": 0.0,
            "tool_efficiency": 0.0,
            "learning_improvement": 0.0,
            "user_satisfaction_estimate": 0.0
        }
        
        # 計算整體成功率
        execution_phase = cycle_result.get("phases", {}).get("execution", {})
        total_executions = execution_phase.get("total_executions", 0)
        successful_executions = execution_phase.get("successful_executions", 0)
        
        if total_executions > 0:
            metrics["overall_success_rate"] = successful_executions / total_executions
        
        # 計算平均執行時間
        execution_results = execution_phase.get("execution_results", [])
        execution_times = [r.get("execution_time", 0) for r in execution_results if r.get("execution_time")]
        
        if execution_times:
            metrics["average_execution_time"] = np.mean(execution_times)
        
        # 計算工具效率
        if successful_executions > 0 and metrics["average_execution_time"] > 0:
            metrics["tool_efficiency"] = successful_executions / metrics["average_execution_time"]
        
        # 估算學習改進
        learning_phase = cycle_result.get("phases", {}).get("learning", {})
        metrics["learning_improvement"] = learning_phase.get("performance_improvement", 0)
        
        # 估算用戶滿意度
        if metrics["overall_success_rate"] > 0.8 and metrics["average_execution_time"] < 10:
            metrics["user_satisfaction_estimate"] = 0.9
        elif metrics["overall_success_rate"] > 0.6:
            metrics["user_satisfaction_estimate"] = 0.7
        else:
            metrics["user_satisfaction_estimate"] = 0.5
        
        return metrics
    
    def make_serializable(self, obj: Any) -> Any:
        """使對象可序列化"""
        if isinstance(obj, dict):
            return {k: self.make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self.make_serializable(obj.__dict__)
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    def generate_closed_loop_report(self, cycle_results: List[Dict[str, Any]]) -> str:
        """生成閉環報告"""
        report_content = f"""# PowerAutomation Linux環境閉環系統報告

## 📊 系統概況

- **報告生成時間**: {datetime.now().isoformat()}
- **總循環數**: {len(cycle_results)}
- **系統版本**: Linux閉環 v1.0

## 🔄 閉環性能分析

"""
        
        if cycle_results:
            # 計算總體指標
            total_success = len([c for c in cycle_results if c.get("success", False)])
            success_rate = (total_success / len(cycle_results)) * 100
            
            avg_tools_per_cycle = np.mean([
                c.get("phases", {}).get("tool_generation", {}).get("tools_created", 0) 
                for c in cycle_results
            ])
            
            avg_execution_time = np.mean([
                c.get("performance_metrics", {}).get("average_execution_time", 0)
                for c in cycle_results
            ])
            
            report_content += f"""### 總體指標
- **成功率**: {success_rate:.1f}%
- **平均每循環工具數**: {avg_tools_per_cycle:.1f}
- **平均執行時間**: {avg_execution_time:.2f} 秒

### 學習改進趨勢
"""
            
            for i, cycle in enumerate(cycle_results):
                metrics = cycle.get("performance_metrics", {})
                report_content += f"- **循環 {i+1}**: 成功率 {metrics.get('overall_success_rate', 0):.1%}, "
                report_content += f"用戶滿意度 {metrics.get('user_satisfaction_estimate', 0):.1%}\n"
        
        report_content += f"""
## 🔧 KiloCode工具統計

- **總工具數**: {len(self.kilocode_tools)}
- **工具類型**: 文檔分析器、數據分析器、報告生成器等

### 工具性能排行
"""
        
        # 工具性能排行
        sorted_tools = sorted(
            self.kilocode_tools.values(),
            key=lambda t: t.success_rate,
            reverse=True
        )
        
        for i, tool in enumerate(sorted_tools[:5]):
            report_content += f"{i+1}. **{tool.name}**: 成功率 {tool.success_rate:.1%}, 執行次數 {tool.execution_count}\n"
        
        report_content += f"""
## 🧠 RL-SRT學習洞察

### 學習效果
- **學習經驗總數**: {len(self.execution_history)}
- **平均獎勵**: {np.mean([h.get('reward', 0) for h in self.execution_history if 'reward' in h]):.3f}

### 改進建議
1. **工具優化**: 提升低成功率工具的穩定性
2. **學習加速**: 增加異步學習機制
3. **模板擴展**: 添加更多專業領域模板

## 💡 系統價值

### 閉環優勢
- ✅ **自我改進**: 每次執行都在學習
- ✅ **動態適應**: 根據需求生成工具
- ✅ **真實反饋**: 基於實際執行結果
- ✅ **持續優化**: RL-SRT持續改進性能

---

*報告生成時間: {datetime.now().isoformat()}*
"""
        
        return report_content

def main():
    """主函數 - 演示Linux閉環系統"""
    
    # 初始化系統
    closed_loop_system = LinuxClosedLoopSystem()
    
    print("🔄 PowerAutomation Linux閉環系統演示開始...")
    
    # 創建示例文檔
    sample_doc_path = closed_loop_system.base_dir / "documents" / "sample_business_plan.json"
    sample_data = {
        "company": "PowerAutomation",
        "market_size": "10B USD",
        "revenue_projection": [1000000, 5000000, 15000000],
        "key_features": ["KiloCode MCP", "RL-SRT Learning", "Cross-platform Testing"],
        "competitive_advantages": ["Dynamic tool creation", "Self-learning AI", "Real-time adaptation"]
    }
    
    with open(sample_doc_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 創建示例文檔: {sample_doc_path}")
    
    # 運行閉環循環
    cycle_results = []
    
    # 循環1: 商業計劃分析
    print("\n🔄 運行閉環循環 1: 商業計劃分析")
    cycle1 = closed_loop_system.run_closed_loop_cycle(
        "請分析這個商業計劃的可行性和競爭優勢",
        str(sample_doc_path)
    )
    cycle_results.append(cycle1)
    
    # 循環2: 數據分析
    print("\n🔄 運行閉環循環 2: 數據分析")
    cycle2 = closed_loop_system.run_closed_loop_cycle(
        "分析收入預測數據並生成趨勢報告",
        str(sample_doc_path)
    )
    cycle_results.append(cycle2)
    
    # 循環3: 競爭分析
    print("\n🔄 運行閉環循環 3: 競爭分析")
    cycle3 = closed_loop_system.run_closed_loop_cycle(
        "評估競爭優勢並提供改進建議"
    )
    cycle_results.append(cycle3)
    
    # 生成閉環報告
    print("\n📊 生成閉環系統報告...")
    report_content = closed_loop_system.generate_closed_loop_report(cycle_results)
    
    report_file = closed_loop_system.base_dir / "closed_loop_reports" / f"system_report_{int(time.time())}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 閉環系統報告已生成: {report_file}")
    
    # 顯示關鍵指標
    print(f"\n🎯 Linux閉環系統演示完成!")
    print(f"📁 系統目錄: {closed_loop_system.base_dir}")
    print(f"🔧 創建工具數: {len(closed_loop_system.kilocode_tools)}")
    print(f"⚡ 執行歷史數: {len(closed_loop_system.execution_history)}")
    print(f"🔄 閉環循環數: {len(cycle_results)}")
    print(f"📊 系統報告: {report_file}")
    
    # 顯示成功率
    successful_cycles = len([c for c in cycle_results if c.get("success", False)])
    success_rate = (successful_cycles / len(cycle_results)) * 100 if cycle_results else 0
    print(f"✅ 閉環成功率: {success_rate:.1f}%")
    
    return closed_loop_system, cycle_results, report_file

if __name__ == "__main__":
    main()

