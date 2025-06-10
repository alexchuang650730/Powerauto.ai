#!/usr/bin/env python3
"""
PowerAutomation 智能環境檢測和Qwen模型選擇系統
自動檢測系統環境，智能選擇本地Qwen3或雲側Qwen8B API
"""

import asyncio
import json
import logging
import platform
import psutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import aiohttp
import GPUtil
import torch
import requests
from packaging import version

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QwenIntelligentSelector")

class SystemType(Enum):
    """系統類型"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"

class GPUType(Enum):
    """GPU類型"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    APPLE_SILICON = "apple_silicon"
    NONE = "none"

class ModelCapability(Enum):
    """模型能力級別"""
    HIGH_PERFORMANCE = "high_performance"    # 高性能GPU，可運行大模型
    MEDIUM_PERFORMANCE = "medium_performance" # 中等GPU，可運行小模型
    LOW_PERFORMANCE = "low_performance"      # 低性能或無GPU，使用雲端
    CLOUD_ONLY = "cloud_only"               # 僅雲端

@dataclass
class SystemEnvironment:
    """系統環境信息"""
    system_type: SystemType
    cpu_cores: int
    total_memory_gb: float
    available_memory_gb: float
    gpu_type: GPUType
    gpu_count: int
    gpu_memory_gb: float
    gpu_compute_capability: Optional[str]
    python_version: str
    torch_available: bool
    torch_cuda_available: bool
    torch_mps_available: bool
    model_capability: ModelCapability
    recommended_model: str
    performance_score: float

class SystemDetector:
    """系統環境檢測器"""
    
    def __init__(self):
        self.detection_cache = {}
        self.cache_expiry = timedelta(hours=1)
        self.last_detection = None
    
    def detect_system_environment(self) -> SystemEnvironment:
        """檢測系統環境"""
        # 檢查緩存
        if (self.last_detection and 
            datetime.now() - self.last_detection < self.cache_expiry and
            self.detection_cache):
            logger.info("使用緩存的環境檢測結果")
            return SystemEnvironment(**self.detection_cache)
        
        logger.info("開始檢測系統環境...")
        
        # 檢測系統類型
        system_type = self._detect_system_type()
        
        # 檢測CPU和內存
        cpu_cores = psutil.cpu_count(logical=True)
        memory_info = psutil.virtual_memory()
        total_memory_gb = memory_info.total / (1024**3)
        available_memory_gb = memory_info.available / (1024**3)
        
        # 檢測GPU
        gpu_info = self._detect_gpu()
        
        # 檢測Python和PyTorch
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        torch_info = self._detect_torch()
        
        # 評估模型能力
        model_capability, recommended_model, performance_score = self._evaluate_model_capability(
            system_type, cpu_cores, total_memory_gb, gpu_info, torch_info
        )
        
        # 創建環境對象
        environment = SystemEnvironment(
            system_type=system_type,
            cpu_cores=cpu_cores,
            total_memory_gb=total_memory_gb,
            available_memory_gb=available_memory_gb,
            gpu_type=gpu_info['type'],
            gpu_count=gpu_info['count'],
            gpu_memory_gb=gpu_info['memory_gb'],
            gpu_compute_capability=gpu_info['compute_capability'],
            python_version=python_version,
            torch_available=torch_info['available'],
            torch_cuda_available=torch_info['cuda_available'],
            torch_mps_available=torch_info['mps_available'],
            model_capability=model_capability,
            recommended_model=recommended_model,
            performance_score=performance_score
        )
        
        # 緩存結果
        self.detection_cache = asdict(environment)
        self.last_detection = datetime.now()
        
        logger.info(f"環境檢測完成: {recommended_model} (性能評分: {performance_score:.2f})")
        return environment
    
    def _detect_system_type(self) -> SystemType:
        """檢測系統類型"""
        system = platform.system().lower()
        
        if system == "windows":
            return SystemType.WINDOWS
        elif system == "darwin":
            return SystemType.MACOS
        elif system == "linux":
            return SystemType.LINUX
        else:
            return SystemType.UNKNOWN
    
    def _detect_gpu(self) -> Dict[str, Any]:
        """檢測GPU信息"""
        gpu_info = {
            'type': GPUType.NONE,
            'count': 0,
            'memory_gb': 0.0,
            'compute_capability': None
        }
        
        try:
            # 檢測NVIDIA GPU
            nvidia_gpus = GPUtil.getGPUs()
            if nvidia_gpus:
                gpu_info['type'] = GPUType.NVIDIA
                gpu_info['count'] = len(nvidia_gpus)
                gpu_info['memory_gb'] = sum(gpu.memoryTotal for gpu in nvidia_gpus) / 1024
                
                # 獲取計算能力
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=compute_cap', '--format=csv,noheader,nounits'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        gpu_info['compute_capability'] = result.stdout.strip().split('\n')[0]
                except:
                    pass
                
                return gpu_info
        except:
            pass
        
        # 檢測Apple Silicon
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                      capture_output=True, text=True, timeout=10)
                if "Apple M" in result.stdout:
                    gpu_info['type'] = GPUType.APPLE_SILICON
                    gpu_info['count'] = 1
                    
                    # 估算Apple Silicon GPU內存（統一內存架構）
                    memory_info = psutil.virtual_memory()
                    gpu_info['memory_gb'] = memory_info.total / (1024**3) * 0.6  # 假設60%可用於GPU
                    
                    return gpu_info
            except:
                pass
        
        # 檢測AMD GPU (簡化檢測)
        try:
            if platform.system() == "Linux":
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=10)
                if "AMD" in result.stdout and ("Radeon" in result.stdout or "RDNA" in result.stdout):
                    gpu_info['type'] = GPUType.AMD
                    gpu_info['count'] = 1
                    gpu_info['memory_gb'] = 8.0  # 估算值
        except:
            pass
        
        return gpu_info
    
    def _detect_torch(self) -> Dict[str, bool]:
        """檢測PyTorch環境"""
        torch_info = {
            'available': False,
            'cuda_available': False,
            'mps_available': False
        }
        
        try:
            import torch
            torch_info['available'] = True
            torch_info['cuda_available'] = torch.cuda.is_available()
            
            # 檢測MPS (Apple Silicon)
            if hasattr(torch.backends, 'mps'):
                torch_info['mps_available'] = torch.backends.mps.is_available()
                
        except ImportError:
            pass
        
        return torch_info
    
    def _evaluate_model_capability(self, system_type: SystemType, cpu_cores: int, 
                                 total_memory_gb: float, gpu_info: Dict[str, Any], 
                                 torch_info: Dict[str, bool]) -> Tuple[ModelCapability, str, float]:
        """評估模型運行能力"""
        performance_score = 0.0
        
        # CPU評分 (0-20分)
        cpu_score = min(cpu_cores * 2, 20)
        performance_score += cpu_score
        
        # 內存評分 (0-20分)
        memory_score = min(total_memory_gb * 2, 20)
        performance_score += memory_score
        
        # GPU評分 (0-60分)
        gpu_score = 0
        if gpu_info['type'] == GPUType.NVIDIA:
            gpu_score = min(gpu_info['memory_gb'] * 5, 50)
            if gpu_info['compute_capability']:
                try:
                    compute_cap = float(gpu_info['compute_capability'])
                    if compute_cap >= 8.0:  # RTX 30/40系列
                        gpu_score += 10
                    elif compute_cap >= 7.0:  # RTX 20系列
                        gpu_score += 5
                except:
                    pass
        elif gpu_info['type'] == GPUType.APPLE_SILICON:
            gpu_score = min(gpu_info['memory_gb'] * 3, 40)
        elif gpu_info['type'] == GPUType.AMD:
            gpu_score = min(gpu_info['memory_gb'] * 2, 30)
        
        performance_score += gpu_score
        
        # PyTorch環境評分 (0-10分)
        if torch_info['available']:
            performance_score += 5
            if torch_info['cuda_available'] or torch_info['mps_available']:
                performance_score += 5
        
        # 根據評分確定能力級別和推薦模型
        if performance_score >= 80:
            return ModelCapability.HIGH_PERFORMANCE, "local_qwen3_7b", performance_score
        elif performance_score >= 60:
            return ModelCapability.MEDIUM_PERFORMANCE, "local_qwen3_3b", performance_score
        elif performance_score >= 40:
            return ModelCapability.LOW_PERFORMANCE, "hybrid_qwen3_1.5b", performance_score
        else:
            return ModelCapability.CLOUD_ONLY, "cloud_qwen8b", performance_score

class QwenModelManager:
    """Qwen模型管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detector = SystemDetector()
        self.environment = None
        self.current_model = None
        self.model_cache = {}
        
        # 雲端API配置
        self.cloud_api_endpoint = config.get('cloud_api_endpoint', 'https://api.powerauto.ai/qwen')
        self.cloud_api_key = config.get('cloud_api_key', '')
        
        # 本地模型配置
        self.local_model_path = config.get('local_model_path', './models')
        self.model_configs = {
            'local_qwen3_7b': {
                'model_name': 'Qwen/Qwen2.5-7B-Instruct',
                'memory_requirement': 14,  # GB
                'context_length': 32768
            },
            'local_qwen3_3b': {
                'model_name': 'Qwen/Qwen2.5-3B-Instruct', 
                'memory_requirement': 6,   # GB
                'context_length': 32768
            },
            'hybrid_qwen3_1.5b': {
                'model_name': 'Qwen/Qwen2.5-1.5B-Instruct',
                'memory_requirement': 3,   # GB
                'context_length': 32768
            },
            'cloud_qwen8b': {
                'model_name': 'qwen-plus',
                'context_length': 131072
            }
        }
    
    async def initialize(self):
        """初始化模型管理器"""
        logger.info("初始化Qwen模型管理器...")
        
        # 檢測系統環境
        self.environment = self.detector.detect_system_environment()
        
        # 根據環境選擇模型
        await self._select_optimal_model()
        
        logger.info(f"模型管理器初始化完成，當前模型: {self.current_model}")
    
    async def _select_optimal_model(self):
        """選擇最優模型"""
        recommended_model = self.environment.recommended_model
        
        # 檢查本地模型可用性
        if recommended_model.startswith('local_') or recommended_model.startswith('hybrid_'):
            if await self._check_local_model_availability(recommended_model):
                self.current_model = recommended_model
                logger.info(f"選擇本地模型: {recommended_model}")
            else:
                # 降級到雲端模型
                self.current_model = 'cloud_qwen8b'
                logger.info(f"本地模型不可用，降級到雲端模型: {self.current_model}")
        else:
            self.current_model = recommended_model
            logger.info(f"選擇雲端模型: {recommended_model}")
    
    async def _check_local_model_availability(self, model_key: str) -> bool:
        """檢查本地模型可用性"""
        try:
            model_config = self.model_configs[model_key]
            
            # 檢查內存需求
            if self.environment.available_memory_gb < model_config['memory_requirement']:
                logger.warning(f"內存不足，需要 {model_config['memory_requirement']}GB，可用 {self.environment.available_memory_gb:.1f}GB")
                return False
            
            # 檢查PyTorch環境
            if not self.environment.torch_available:
                logger.warning("PyTorch未安裝，無法運行本地模型")
                return False
            
            # 檢查模型文件（簡化檢查）
            model_path = Path(self.local_model_path) / model_config['model_name']
            if not model_path.exists():
                logger.info(f"本地模型文件不存在: {model_path}")
                # 這裡可以添加自動下載邏輯
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"檢查本地模型可用性失敗: {e}")
            return False
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成響應"""
        start_time = time.time()
        
        try:
            if self.current_model == 'cloud_qwen8b':
                response = await self._generate_cloud_response(prompt, **kwargs)
            else:
                response = await self._generate_local_response(prompt, **kwargs)
            
            # 添加性能統計
            response['generation_time'] = time.time() - start_time
            response['model_used'] = self.current_model
            response['tokens_saved'] = self._calculate_tokens_saved(response)
            
            return response
            
        except Exception as e:
            logger.error(f"生成響應失敗: {e}")
            
            # 故障轉移到雲端
            if self.current_model != 'cloud_qwen8b':
                logger.info("本地模型失敗，轉移到雲端模型")
                return await self._generate_cloud_response(prompt, **kwargs)
            else:
                return {
                    'success': False,
                    'error': str(e),
                    'model_used': self.current_model
                }
    
    async def _generate_cloud_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用雲端API生成響應"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'model': 'qwen-plus',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': kwargs.get('max_tokens', 2048),
                    'temperature': kwargs.get('temperature', 0.7)
                }
                
                headers = {
                    'Authorization': f'Bearer {self.cloud_api_key}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(self.cloud_api_endpoint, 
                                      json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'content': result['choices'][0]['message']['content'],
                            'tokens_used': result['usage']['total_tokens'],
                            'model_used': 'cloud_qwen8b'
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'API錯誤: {response.status} - {error_text}',
                            'model_used': 'cloud_qwen8b'
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'error': f'雲端API調用失敗: {e}',
                'model_used': 'cloud_qwen8b'
            }
    
    async def _generate_local_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用本地模型生成響應"""
        try:
            # 這裡應該實現實際的本地模型推理
            # 暫時返回模擬響應
            await asyncio.sleep(0.5)  # 模擬推理時間
            
            return {
                'success': True,
                'content': f'[本地模型響應] 這是對 "{prompt[:50]}..." 的回應',
                'tokens_used': len(prompt.split()) * 2,  # 估算
                'model_used': self.current_model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'本地模型推理失敗: {e}',
                'model_used': self.current_model
            }
    
    def _calculate_tokens_saved(self, response: Dict[str, Any]) -> int:
        """計算節省的token數量"""
        if response['model_used'] == 'cloud_qwen8b':
            return 0
        
        # 估算如果使用雲端模型會消耗的token數
        estimated_cloud_tokens = response.get('tokens_used', 0) * 1.2  # 雲端模型通常更大
        actual_tokens = response.get('tokens_used', 0)
        
        return max(0, int(estimated_cloud_tokens - actual_tokens))
    
    def get_model_status(self) -> Dict[str, Any]:
        """獲取模型狀態"""
        return {
            'current_model': self.current_model,
            'environment': asdict(self.environment) if self.environment else None,
            'model_configs': self.model_configs,
            'performance_score': self.environment.performance_score if self.environment else 0
        }
    
    async def switch_model(self, target_model: str) -> Dict[str, Any]:
        """手動切換模型"""
        if target_model not in self.model_configs:
            return {
                'success': False,
                'error': f'未知模型: {target_model}'
            }
        
        # 檢查目標模型可用性
        if target_model.startswith('local_') or target_model.startswith('hybrid_'):
            if not await self._check_local_model_availability(target_model):
                return {
                    'success': False,
                    'error': f'模型 {target_model} 不可用'
                }
        
        old_model = self.current_model
        self.current_model = target_model
        
        logger.info(f"模型切換: {old_model} -> {target_model}")
        
        return {
            'success': True,
            'old_model': old_model,
            'new_model': target_model
        }

class IntelligentQwenMCP:
    """智能Qwen MCP適配器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_manager = QwenModelManager(config)
        self.request_history = []
        self.performance_stats = {
            'total_requests': 0,
            'local_requests': 0,
            'cloud_requests': 0,
            'total_tokens_saved': 0,
            'average_response_time': 0.0
        }
    
    async def initialize(self):
        """初始化MCP適配器"""
        logger.info("初始化智能Qwen MCP適配器...")
        await self.model_manager.initialize()
        logger.info("智能Qwen MCP適配器初始化完成")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理請求"""
        start_time = time.time()
        
        try:
            prompt = request_data.get('prompt', '')
            user_id = request_data.get('user_id', 'anonymous')
            
            # 生成響應
            response = await self.model_manager.generate_response(
                prompt,
                max_tokens=request_data.get('max_tokens', 2048),
                temperature=request_data.get('temperature', 0.7)
            )
            
            # 更新統計
            self._update_statistics(response, time.time() - start_time)
            
            # 記錄請求歷史
            self.request_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'model_used': response.get('model_used'),
                'tokens_used': response.get('tokens_used', 0),
                'tokens_saved': response.get('tokens_saved', 0),
                'response_time': response.get('generation_time', 0)
            })
            
            # 保持歷史記錄在合理範圍內
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-500:]
            
            return response
            
        except Exception as e:
            logger.error(f"處理請求失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_statistics(self, response: Dict[str, Any], response_time: float):
        """更新性能統計"""
        self.performance_stats['total_requests'] += 1
        
        if response.get('model_used', '').startswith('local_') or response.get('model_used', '').startswith('hybrid_'):
            self.performance_stats['local_requests'] += 1
        else:
            self.performance_stats['cloud_requests'] += 1
        
        self.performance_stats['total_tokens_saved'] += response.get('tokens_saved', 0)
        
        # 更新平均響應時間
        total_time = self.performance_stats['average_response_time'] * (self.performance_stats['total_requests'] - 1)
        self.performance_stats['average_response_time'] = (total_time + response_time) / self.performance_stats['total_requests']
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計信息"""
        local_ratio = 0
        if self.performance_stats['total_requests'] > 0:
            local_ratio = self.performance_stats['local_requests'] / self.performance_stats['total_requests']
        
        return {
            **self.performance_stats,
            'local_processing_ratio': local_ratio,
            'model_status': self.model_manager.get_model_status(),
            'recent_requests': self.request_history[-10:] if self.request_history else []
        }

# 使用示例
async def main():
    """主函數示例"""
    config = {
        'cloud_api_endpoint': 'https://api.powerauto.ai/qwen',
        'cloud_api_key': 'your_api_key_here',
        'local_model_path': './models'
    }
    
    # 初始化智能Qwen MCP
    qwen_mcp = IntelligentQwenMCP(config)
    await qwen_mcp.initialize()
    
    print("=== PowerAutomation 智能Qwen MCP 系統 ===")
    
    # 顯示環境信息
    stats = qwen_mcp.get_statistics()
    model_status = stats['model_status']
    
    print(f"系統類型: {model_status['environment']['system_type']}")
    print(f"GPU類型: {model_status['environment']['gpu_type']}")
    print(f"性能評分: {model_status['performance_score']:.2f}")
    print(f"推薦模型: {model_status['current_model']}")
    
    # 測試請求
    test_requests = [
        "請幫我寫一個Python函數來計算斐波那契數列",
        "解釋一下什麼是機器學習",
        "如何優化深度學習模型的性能？"
    ]
    
    for i, prompt in enumerate(test_requests, 1):
        print(f"\n--- 測試請求 {i} ---")
        print(f"提示: {prompt}")
        
        response = await qwen_mcp.process_request({
            'prompt': prompt,
            'user_id': 'test_user',
            'max_tokens': 1024
        })
        
        if response['success']:
            print(f"模型: {response['model_used']}")
            print(f"響應時間: {response.get('generation_time', 0):.2f}秒")
            print(f"Token節省: {response.get('tokens_saved', 0)}")
            print(f"響應: {response['content'][:100]}...")
        else:
            print(f"錯誤: {response['error']}")
    
    # 顯示最終統計
    final_stats = qwen_mcp.get_statistics()
    print(f"\n=== 最終統計 ===")
    print(f"總請求數: {final_stats['total_requests']}")
    print(f"本地處理比例: {final_stats['local_processing_ratio']:.2%}")
    print(f"總Token節省: {final_stats['total_tokens_saved']}")
    print(f"平均響應時間: {final_stats['average_response_time']:.2f}秒")

if __name__ == "__main__":
    asyncio.run(main())

