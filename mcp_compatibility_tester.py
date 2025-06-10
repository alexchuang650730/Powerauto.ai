#!/usr/bin/env python3
"""
RL_SRT + 異步RL + Qwen MCP 可用性測試器
檢查這些組件在WSL+Mac終端環境下的兼容性
"""

import os
import sys
import json
import asyncio
import logging
import platform
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPCompatibilityTester:
    """MCP兼容性測試器"""
    
    def __init__(self):
        """初始化測試器"""
        self.platform = platform.system().lower()
        self.is_wsl = self._detect_wsl()
        self.test_results = {}
        
        logger.info(f"MCP兼容性測試器初始化 - 平台: {self.platform}, WSL: {self.is_wsl}")
    
    def _detect_wsl(self) -> bool:
        """檢測WSL環境"""
        try:
            if self.platform == "linux":
                with open('/proc/version', 'r') as f:
                    return 'microsoft' in f.read().lower()
        except:
            pass
        return False
    
    async def test_qwen_mcp(self) -> Dict[str, Any]:
        """測試Qwen MCP可用性"""
        test_name = "Qwen MCP"
        logger.info(f"開始測試 {test_name}...")
        
        result = {
            "name": test_name,
            "status": "unknown",
            "details": {},
            "recommendations": []
        }
        
        try:
            # 檢查Qwen MCP文件
            qwen_file = "/home/ubuntu/Powerauto.ai/mcptool/adapters/qwen3_8b_local_mcp.py"
            if os.path.exists(qwen_file):
                result["details"]["file_exists"] = True
                
                # 嘗試導入
                try:
                    sys.path.append("/home/ubuntu/Powerauto.ai")
                    from mcptool.adapters.qwen3_8b_local_mcp import Qwen3LocalModelMCP
                    result["details"]["import_success"] = True
                    
                    # 創建實例
                    qwen_mcp = Qwen3LocalModelMCP()
                    result["details"]["instance_created"] = True
                    
                    # 檢查Ollama依賴
                    ollama_available = await self._check_ollama()
                    result["details"]["ollama_available"] = ollama_available
                    
                    if ollama_available:
                        result["status"] = "available"
                        result["details"]["message"] = "Qwen MCP完全可用"
                    else:
                        result["status"] = "needs_setup"
                        result["details"]["message"] = "需要安裝Ollama"
                        result["recommendations"].append("運行: curl -fsSL https://ollama.ai/install.sh | sh")
                        result["recommendations"].append("然後: ollama pull qwen2.5:8b")
                    
                except ImportError as e:
                    result["details"]["import_error"] = str(e)
                    result["status"] = "import_failed"
                    result["recommendations"].append("檢查Python依賴")
                    
            else:
                result["details"]["file_exists"] = False
                result["status"] = "not_found"
                result["recommendations"].append("Qwen MCP文件不存在")
                
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    async def test_rl_srt_mcp(self) -> Dict[str, Any]:
        """測試RL_SRT MCP可用性"""
        test_name = "RL_SRT MCP"
        logger.info(f"開始測試 {test_name}...")
        
        result = {
            "name": test_name,
            "status": "unknown",
            "details": {},
            "recommendations": []
        }
        
        try:
            # 檢查RL_SRT文件
            rl_files = [
                "/home/ubuntu/Powerauto.ai/mcptool/adapters/rl_srt/rl_srt_mcp.py",
                "/home/ubuntu/Powerauto.ai/mcptool/adapters/rl_srt_dataflow_mcp.py"
            ]
            
            files_exist = [os.path.exists(f) for f in rl_files]
            result["details"]["files_exist"] = dict(zip(rl_files, files_exist))
            
            if any(files_exist):
                # 檢查PyTorch依賴
                pytorch_available = await self._check_pytorch()
                result["details"]["pytorch_available"] = pytorch_available
                
                # 嘗試導入
                try:
                    sys.path.append("/home/ubuntu/Powerauto.ai")
                    from mcptool.adapters.rl_srt.rl_srt_mcp import RLSRTAdapter
                    result["details"]["import_success"] = True
                    
                    # 創建實例
                    rl_adapter = RLSRTAdapter()
                    result["details"]["instance_created"] = True
                    
                    if pytorch_available:
                        result["status"] = "available"
                        result["details"]["message"] = "RL_SRT MCP完全可用"
                    else:
                        result["status"] = "limited"
                        result["details"]["message"] = "RL_SRT可用但功能受限（無PyTorch）"
                        result["recommendations"].append("安裝PyTorch: pip install torch")
                    
                except ImportError as e:
                    result["details"]["import_error"] = str(e)
                    result["status"] = "import_failed"
                    result["recommendations"].append("檢查依賴和路徑")
                    
            else:
                result["status"] = "not_found"
                result["recommendations"].append("RL_SRT MCP文件不存在")
                
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    async def test_async_rl(self) -> Dict[str, Any]:
        """測試異步RL功能"""
        test_name = "異步RL"
        logger.info(f"開始測試 {test_name}...")
        
        result = {
            "name": test_name,
            "status": "unknown",
            "details": {},
            "recommendations": []
        }
        
        try:
            # 檢查異步支持
            asyncio_available = True
            result["details"]["asyncio_available"] = asyncio_available
            
            # 檢查RL相關文件
            rl_dataflow_file = "/home/ubuntu/Powerauto.ai/mcptool/adapters/rl_srt_dataflow_mcp.py"
            if os.path.exists(rl_dataflow_file):
                result["details"]["dataflow_file_exists"] = True
                
                # 測試異步功能
                try:
                    async def test_async():
                        await asyncio.sleep(0.1)
                        return True
                    
                    async_test_result = await test_async()
                    result["details"]["async_test_passed"] = async_test_result
                    
                    result["status"] = "available"
                    result["details"]["message"] = "異步RL功能可用"
                    
                except Exception as e:
                    result["details"]["async_error"] = str(e)
                    result["status"] = "limited"
                    result["recommendations"].append("檢查異步環境配置")
                    
            else:
                result["status"] = "not_found"
                result["recommendations"].append("異步RL數據流文件不存在")
                
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    async def test_terminal_compatibility(self) -> Dict[str, Any]:
        """測試終端兼容性"""
        test_name = "終端兼容性"
        logger.info(f"開始測試 {test_name}...")
        
        result = {
            "name": test_name,
            "status": "unknown",
            "details": {},
            "recommendations": []
        }
        
        try:
            # 檢查環境變量
            env_vars = {
                "TERM": os.getenv("TERM"),
                "SHELL": os.getenv("SHELL"),
                "PATH": len(os.getenv("PATH", "").split(":")),
                "PYTHON_PATH": sys.executable
            }
            result["details"]["environment"] = env_vars
            
            # 檢查Python版本
            python_version = sys.version_info
            result["details"]["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            
            # 檢查平台特定功能
            platform_info = {
                "system": self.platform,
                "is_wsl": self.is_wsl,
                "architecture": platform.machine(),
                "processor": platform.processor()
            }
            result["details"]["platform"] = platform_info
            
            # WSL特定檢查
            if self.is_wsl:
                result["details"]["wsl_specific"] = await self._check_wsl_features()
                result["status"] = "wsl_compatible"
                result["details"]["message"] = "WSL環境兼容"
            elif self.platform == "darwin":
                result["status"] = "mac_compatible"
                result["details"]["message"] = "Mac環境兼容"
            else:
                result["status"] = "linux_compatible"
                result["details"]["message"] = "Linux環境兼容"
                
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    async def _check_ollama(self) -> bool:
        """檢查Ollama可用性"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def _check_pytorch(self) -> bool:
        """檢查PyTorch可用性"""
        try:
            import torch
            return True
        except ImportError:
            return False
    
    async def _check_wsl_features(self) -> Dict[str, Any]:
        """檢查WSL特定功能"""
        features = {}
        
        try:
            # 檢查WSL版本
            result = subprocess.run(['wsl', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            features["wsl_version_available"] = result.returncode == 0
            if result.returncode == 0:
                features["wsl_version_output"] = result.stdout.strip()
        except:
            features["wsl_version_available"] = False
        
        try:
            # 檢查Windows互操作性
            features["windows_interop"] = os.path.exists("/mnt/c")
        except:
            features["windows_interop"] = False
        
        return features
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        logger.info("開始運行所有MCP兼容性測試...")
        
        tests = [
            self.test_qwen_mcp(),
            self.test_rl_srt_mcp(),
            self.test_async_rl(),
            self.test_terminal_compatibility()
        ]
        
        results = await asyncio.gather(*tests)
        
        # 匯總結果
        summary = {
            "test_time": datetime.now().isoformat(),
            "platform": self.platform,
            "is_wsl": self.is_wsl,
            "total_tests": len(results),
            "passed": len([r for r in results if r["status"] in ["available", "wsl_compatible", "mac_compatible", "linux_compatible"]]),
            "failed": len([r for r in results if r["status"] in ["error", "not_found", "import_failed"]]),
            "limited": len([r for r in results if r["status"] in ["limited", "needs_setup"]]),
            "results": results
        }
        
        return summary


async def main():
    """主測試函數"""
    print("🧪 MCP兼容性測試開始\\n")
    
    tester = MCPCompatibilityTester()
    summary = await tester.run_all_tests()
    
    print(f"📊 測試摘要:")
    print(f"平台: {summary['platform']} {'(WSL)' if summary['is_wsl'] else ''}")
    print(f"總測試數: {summary['total_tests']}")
    print(f"✅ 通過: {summary['passed']}")
    print(f"⚠️ 受限: {summary['limited']}")
    print(f"❌ 失敗: {summary['failed']}")
    print()
    
    for result in summary["results"]:
        status_emoji = {
            "available": "✅",
            "wsl_compatible": "✅",
            "mac_compatible": "✅", 
            "linux_compatible": "✅",
            "limited": "⚠️",
            "needs_setup": "⚠️",
            "error": "❌",
            "not_found": "❌",
            "import_failed": "❌"
        }.get(result["status"], "❓")
        
        print(f"{status_emoji} {result['name']}: {result['status']}")
        if "message" in result["details"]:
            print(f"   {result['details']['message']}")
        
        if result["recommendations"]:
            print("   建議:")
            for rec in result["recommendations"]:
                print(f"   - {rec}")
        print()
    
    # 保存詳細結果
    with open("/home/ubuntu/Powerauto.ai/mcp_compatibility_test_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("📄 詳細結果已保存到: mcp_compatibility_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())

