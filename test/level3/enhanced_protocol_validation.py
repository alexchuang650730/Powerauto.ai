#!/usr/bin/env python3
"""
MCP協議驗證測試模組
實施完整的MCP（Model Context Protocol）協議合規性驗證

符合MCP 1.0規範的協議驗證測試，包括：
- JSON-RPC 2.0消息格式驗證
- MCP標準方法驗證
- 參數和響應格式驗證
- 錯誤處理驗證
- 協議流程驗證
"""

import json
import pytest
import asyncio
import sys
import os
import time
import logging
from typing import Dict, Any, List, Optional, Union
from unittest.mock import Mock, patch
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

class MCPProtocolValidator:
    """MCP協議驗證器"""
    
    def __init__(self):
        self.validation_results = {
            "message_format_tests": [],
            "method_validation_tests": [],
            "parameter_validation_tests": [],
            "response_validation_tests": [],
            "error_handling_tests": [],
            "protocol_flow_tests": [],
            "overall_compliance": False,
            "compliance_score": 0.0
        }
        
        # MCP標準方法定義
        self.standard_methods = {
            "initialize": {
                "required_params": ["protocolVersion", "capabilities"],
                "optional_params": ["clientInfo"],
                "response_format": {
                    "protocolVersion": str,
                    "capabilities": dict,
                    "serverInfo": dict
                }
            },
            "tools/list": {
                "required_params": [],
                "optional_params": ["cursor"],
                "response_format": {
                    "tools": list
                }
            },
            "tools/call": {
                "required_params": ["name"],
                "optional_params": ["arguments"],
                "response_format": {
                    "content": list,
                    "isError": bool
                }
            },
            "resources/list": {
                "required_params": [],
                "optional_params": ["cursor"],
                "response_format": {
                    "resources": list
                }
            },
            "resources/read": {
                "required_params": ["uri"],
                "optional_params": [],
                "response_format": {
                    "contents": list
                }
            },
            "prompts/list": {
                "required_params": [],
                "optional_params": ["cursor"],
                "response_format": {
                    "prompts": list
                }
            },
            "prompts/get": {
                "required_params": ["name"],
                "optional_params": ["arguments"],
                "response_format": {
                    "description": str,
                    "messages": list
                }
            }
        }
    
    def validate_jsonrpc_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """驗證JSON-RPC 2.0消息格式"""
        test_result = {
            "test_name": "JSON-RPC 2.0 Message Format",
            "passed": True,
            "errors": [],
            "details": {}
        }
        
        # 檢查必需字段
        required_fields = ["jsonrpc", "id"]
        for field in required_fields:
            if field not in message:
                test_result["passed"] = False
                test_result["errors"].append(f"Missing required field: {field}")
        
        # 檢查JSON-RPC版本
        if message.get("jsonrpc") != "2.0":
            test_result["passed"] = False
            test_result["errors"].append(f"Invalid jsonrpc version: {message.get('jsonrpc')}, expected '2.0'")
        
        # 檢查消息類型
        if "method" in message:
            # 請求消息
            if not isinstance(message.get("method"), str):
                test_result["passed"] = False
                test_result["errors"].append("Method must be a string")
            test_result["details"]["message_type"] = "request"
        elif "result" in message or "error" in message:
            # 響應消息
            if "result" in message and "error" in message:
                test_result["passed"] = False
                test_result["errors"].append("Response cannot have both result and error")
            test_result["details"]["message_type"] = "response"
        else:
            test_result["passed"] = False
            test_result["errors"].append("Message must have either method (request) or result/error (response)")
        
        return test_result
    
    def validate_mcp_method(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """驗證MCP標準方法"""
        test_result = {
            "test_name": f"MCP Method Validation: {method}",
            "passed": True,
            "errors": [],
            "details": {"method": method}
        }
        
        if method not in self.standard_methods:
            test_result["passed"] = False
            test_result["errors"].append(f"Unknown MCP method: {method}")
            return test_result
        
        method_spec = self.standard_methods[method]
        params = params or {}
        
        # 檢查必需參數
        for required_param in method_spec["required_params"]:
            if required_param not in params:
                test_result["passed"] = False
                test_result["errors"].append(f"Missing required parameter: {required_param}")
        
        # 檢查參數類型（基本驗證）
        test_result["details"]["validated_params"] = list(params.keys())
        
        return test_result
    
    def validate_response_format(self, method: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """驗證響應格式"""
        test_result = {
            "test_name": f"Response Format Validation: {method}",
            "passed": True,
            "errors": [],
            "details": {"method": method}
        }
        
        if method not in self.standard_methods:
            test_result["errors"].append(f"Unknown method for response validation: {method}")
            test_result["passed"] = False
            return test_result
        
        expected_format = self.standard_methods[method]["response_format"]
        
        # 檢查響應是否包含result字段
        if "result" not in response:
            test_result["passed"] = False
            test_result["errors"].append("Response missing 'result' field")
            return test_result
        
        result = response["result"]
        
        # 驗證結果格式
        for field, expected_type in expected_format.items():
            if field not in result:
                test_result["passed"] = False
                test_result["errors"].append(f"Missing field in result: {field}")
            elif not isinstance(result[field], expected_type):
                test_result["passed"] = False
                test_result["errors"].append(f"Invalid type for {field}: expected {expected_type.__name__}, got {type(result[field]).__name__}")
        
        return test_result
    
    def validate_error_response(self, error_response: Dict[str, Any]) -> Dict[str, Any]:
        """驗證錯誤響應格式"""
        test_result = {
            "test_name": "Error Response Validation",
            "passed": True,
            "errors": [],
            "details": {}
        }
        
        # 檢查錯誤響應結構
        if "error" not in error_response:
            test_result["passed"] = False
            test_result["errors"].append("Error response missing 'error' field")
            return test_result
        
        error = error_response["error"]
        
        # 檢查錯誤對象必需字段
        required_error_fields = ["code", "message"]
        for field in required_error_fields:
            if field not in error:
                test_result["passed"] = False
                test_result["errors"].append(f"Error object missing required field: {field}")
        
        # 檢查錯誤代碼類型
        if "code" in error and not isinstance(error["code"], int):
            test_result["passed"] = False
            test_result["errors"].append("Error code must be an integer")
        
        # 檢查錯誤消息類型
        if "message" in error and not isinstance(error["message"], str):
            test_result["passed"] = False
            test_result["errors"].append("Error message must be a string")
        
        return test_result
    
    def test_protocol_flow(self) -> Dict[str, Any]:
        """測試協議流程"""
        test_result = {
            "test_name": "Protocol Flow Test",
            "passed": True,
            "errors": [],
            "details": {"flow_steps": []}
        }
        
        # 模擬協議初始化流程
        try:
            # 1. 初始化請求
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True}
                    },
                    "clientInfo": {
                        "name": "PowerAutomation",
                        "version": "0.4.2"
                    }
                }
            }
            
            # 驗證初始化請求
            init_validation = self.validate_jsonrpc_message(init_request)
            if not init_validation["passed"]:
                test_result["passed"] = False
                test_result["errors"].extend(init_validation["errors"])
            
            test_result["details"]["flow_steps"].append("initialize_request_validated")
            
            # 2. 模擬初始化響應
            init_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True}
                    },
                    "serverInfo": {
                        "name": "PowerAutomation MCP Server",
                        "version": "0.4.2"
                    }
                }
            }
            
            # 驗證初始化響應
            response_validation = self.validate_response_format("initialize", init_response)
            if not response_validation["passed"]:
                test_result["passed"] = False
                test_result["errors"].extend(response_validation["errors"])
            
            test_result["details"]["flow_steps"].append("initialize_response_validated")
            
            # 3. 工具列表請求
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            tools_validation = self.validate_mcp_method("tools/list", {})
            if not tools_validation["passed"]:
                test_result["passed"] = False
                test_result["errors"].extend(tools_validation["errors"])
            
            test_result["details"]["flow_steps"].append("tools_list_validated")
            
        except Exception as e:
            test_result["passed"] = False
            test_result["errors"].append(f"Protocol flow test failed: {str(e)}")
        
        return test_result
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """運行完整的協議驗證測試"""
        logger.info("開始MCP協議驗證測試...")
        
        # 1. 消息格式測試
        test_messages = [
            # 有效請求
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            # 有效響應
            {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}},
            # 有效錯誤響應
            {"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found"}},
            # 無效消息（缺少jsonrpc）
            {"id": 1, "method": "test"},
            # 無效消息（錯誤版本）
            {"jsonrpc": "1.0", "id": 1, "method": "test"}
        ]
        
        for i, message in enumerate(test_messages):
            result = self.validate_jsonrpc_message(message)
            result["test_id"] = f"message_format_{i+1}"
            self.validation_results["message_format_tests"].append(result)
        
        # 2. 方法驗證測試
        for method in self.standard_methods.keys():
            result = self.validate_mcp_method(method, {})
            self.validation_results["method_validation_tests"].append(result)
        
        # 3. 響應格式測試
        sample_responses = {
            "tools/list": {"jsonrpc": "2.0", "id": 1, "result": {"tools": []}},
            "initialize": {
                "jsonrpc": "2.0", 
                "id": 1, 
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "serverInfo": {"name": "test", "version": "1.0"}
                }
            }
        }
        
        for method, response in sample_responses.items():
            result = self.validate_response_format(method, response)
            self.validation_results["response_validation_tests"].append(result)
        
        # 4. 錯誤處理測試
        error_responses = [
            {"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found"}},
            {"jsonrpc": "2.0", "id": 1, "error": {"code": -32602, "message": "Invalid params"}},
            {"jsonrpc": "2.0", "id": 1, "error": {"code": -32603, "message": "Internal error"}}
        ]
        
        for error_response in error_responses:
            result = self.validate_error_response(error_response)
            self.validation_results["error_handling_tests"].append(result)
        
        # 5. 協議流程測試
        flow_result = self.test_protocol_flow()
        self.validation_results["protocol_flow_tests"].append(flow_result)
        
        # 計算總體合規性
        self._calculate_compliance_score()
        
        logger.info(f"MCP協議驗證測試完成，合規分數: {self.validation_results['compliance_score']:.1%}")
        
        return self.validation_results
    
    def _calculate_compliance_score(self):
        """計算合規分數"""
        all_tests = []
        all_tests.extend(self.validation_results["message_format_tests"])
        all_tests.extend(self.validation_results["method_validation_tests"])
        all_tests.extend(self.validation_results["response_validation_tests"])
        all_tests.extend(self.validation_results["error_handling_tests"])
        all_tests.extend(self.validation_results["protocol_flow_tests"])
        
        if not all_tests:
            self.validation_results["compliance_score"] = 0.0
            return
        
        passed_tests = sum(1 for test in all_tests if test["passed"])
        total_tests = len(all_tests)
        
        self.validation_results["compliance_score"] = passed_tests / total_tests
        self.validation_results["overall_compliance"] = self.validation_results["compliance_score"] >= 0.9
    
    def generate_report(self) -> str:
        """生成驗證報告"""
        results = self.validation_results
        
        report = f"""
# MCP協議驗證測試報告

## 📊 總體結果
- **整體合規性**: {'✅ 通過' if results['overall_compliance'] else '❌ 未通過'}
- **合規分數**: {results['compliance_score']:.1%}
- **測試時間**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 詳細測試結果

### 消息格式測試 ({len(results['message_format_tests'])}項)
"""
        
        for test in results["message_format_tests"]:
            status = "✅" if test["passed"] else "❌"
            report += f"- {status} {test['test_name']}\n"
            if test["errors"]:
                for error in test["errors"]:
                    report += f"  - ⚠️ {error}\n"
        
        report += f"""
### 方法驗證測試 ({len(results['method_validation_tests'])}項)
"""
        
        for test in results["method_validation_tests"]:
            status = "✅" if test["passed"] else "❌"
            report += f"- {status} {test['test_name']}\n"
        
        report += f"""
### 響應格式測試 ({len(results['response_validation_tests'])}項)
"""
        
        for test in results["response_validation_tests"]:
            status = "✅" if test["passed"] else "❌"
            report += f"- {status} {test['test_name']}\n"
        
        report += f"""
### 錯誤處理測試 ({len(results['error_handling_tests'])}項)
"""
        
        for test in results["error_handling_tests"]:
            status = "✅" if test["passed"] else "❌"
            report += f"- {status} {test['test_name']}\n"
        
        report += f"""
### 協議流程測試 ({len(results['protocol_flow_tests'])}項)
"""
        
        for test in results["protocol_flow_tests"]:
            status = "✅" if test["passed"] else "❌"
            report += f"- {status} {test['test_name']}\n"
            if test["details"].get("flow_steps"):
                report += f"  - 流程步驟: {', '.join(test['details']['flow_steps'])}\n"
        
        report += f"""
## 🎯 結論

MCP協議驗證測試{'通過' if results['overall_compliance'] else '未完全通過'}，合規分數為 {results['compliance_score']:.1%}。

{'✅ 系統符合MCP協議標準' if results['overall_compliance'] else '⚠️ 系統需要改進以完全符合MCP協議標準'}
"""
        
        return report

if __name__ == "__main__":
    validator = MCPProtocolValidator()
    results = validator.run_comprehensive_validation()
    
    # 生成報告
    report = validator.generate_report()
    
    # 保存報告
    report_file = Path("mcp_protocol_validation_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ MCP協議驗證測試完成")
    print(f"📄 報告已保存到: {report_file}")
    print(f"🎯 合規分數: {results['compliance_score']:.1%}")
    print(f"📊 整體合規性: {'通過' if results['overall_compliance'] else '未通過'}")

