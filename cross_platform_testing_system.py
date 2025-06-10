#!/usr/bin/env python3
"""
PowerAutomation 跨平台測試系統

整合Manus測試數據和Windows/Mac插件數據，支持遠程執行和截圖分析
包含文本描述轉代碼、加解密執行、數據收集分析等完整功能
"""

import os
import json
import time
import base64
import hashlib
import asyncio
import aiohttp
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import cv2
import numpy as np
from PIL import Image
import io
import re

class TestPlatform(Enum):
    """測試平台枚舉"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"

class TestType(Enum):
    """測試類型枚舉"""
    MANUS_INTERACTION = "manus_interaction"
    PLUGIN_EXECUTION = "plugin_execution"
    UI_AUTOMATION = "ui_automation"
    API_TESTING = "api_testing"
    SCREENSHOT_ANALYSIS = "screenshot_analysis"

class TestStatus(Enum):
    """測試狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class TestCase:
    """測試用例數據結構"""
    test_id: str
    name: str
    description: str
    platform: TestPlatform
    test_type: TestType
    text_description: str
    generated_code: str
    expected_result: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str

@dataclass
class TestExecution:
    """測試執行數據結構"""
    execution_id: str
    test_case_id: str
    platform: TestPlatform
    status: TestStatus
    start_time: str
    end_time: Optional[str]
    execution_time: Optional[float]
    result: Dict[str, Any]
    screenshots: List[str]
    logs: List[str]
    error_message: Optional[str]

@dataclass
class RemoteAgent:
    """遠程代理數據結構"""
    agent_id: str
    platform: TestPlatform
    endpoint: str
    api_key: str
    status: str
    capabilities: List[str]
    last_heartbeat: str

class EncryptionManager:
    """加解密管理器"""
    
    def __init__(self, password: str = "PowerAutomation2025"):
        self.password = password.encode()
        self.setup_encryption()
    
    def setup_encryption(self):
        """設置加密"""
        salt = b'PowerAutomation_Salt_2025'  # 實際使用中應該隨機生成
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        self.cipher = Fernet(key)
    
    def encrypt_data(self, data: Union[str, Dict]) -> str:
        """加密數據"""
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        
        encrypted_data = self.cipher.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> Union[str, Dict]:
        """解密數據"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(decoded_data).decode('utf-8')
            
            # 嘗試解析為JSON
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return decrypted_data
        except Exception as e:
            raise ValueError(f"解密失敗: {e}")

class TextToCodeGenerator:
    """文本描述轉代碼生成器"""
    
    def __init__(self):
        self.setup_templates()
    
    def setup_templates(self):
        """設置代碼模板"""
        self.playwright_template = """
from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime

def execute_test():
    results = {{
        'test_id': '{test_id}',
        'start_time': datetime.now().isoformat(),
        'steps': [],
        'screenshots': [],
        'success': False,
        'error': None
    }}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            # 測試步驟
{test_steps}
            
            results['success'] = True
            browser.close()
            
    except Exception as e:
        results['error'] = str(e)
        results['success'] = False
    
    results['end_time'] = datetime.now().isoformat()
    return results

if __name__ == "__main__":
    result = execute_test()
    print(json.dumps(result, indent=2, ensure_ascii=False))
"""
        
        self.api_test_template = """
import requests
import json
from datetime import datetime

def execute_api_test():
    results = {{
        'test_id': '{test_id}',
        'start_time': datetime.now().isoformat(),
        'api_calls': [],
        'success': False,
        'error': None
    }}
    
    try:
        # API測試步驟
{api_steps}
        
        results['success'] = True
        
    except Exception as e:
        results['error'] = str(e)
        results['success'] = False
    
    results['end_time'] = datetime.now().isoformat()
    return results

if __name__ == "__main__":
    result = execute_api_test()
    print(json.dumps(result, indent=2, ensure_ascii=False))
"""
    
    def generate_playwright_code(self, test_case: TestCase) -> str:
        """生成Playwright測試代碼"""
        description = test_case.text_description
        test_steps = self.parse_description_to_playwright_steps(description)
        
        code = self.playwright_template.format(
            test_id=test_case.test_id,
            test_steps=test_steps
        )
        
        return code
    
    def generate_api_test_code(self, test_case: TestCase) -> str:
        """生成API測試代碼"""
        description = test_case.text_description
        api_steps = self.parse_description_to_api_steps(description)
        
        code = self.api_test_template.format(
            test_id=test_case.test_id,
            api_steps=api_steps
        )
        
        return code
    
    def parse_description_to_playwright_steps(self, description: str) -> str:
        """解析文本描述為Playwright步驟"""
        steps = []
        lines = description.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 解析常見操作
            if '打開' in line or 'open' in line.lower():
                url = self.extract_url(line)
                if url:
                    steps.append(f"            page.goto('{url}')")
                    steps.append(f"            page.screenshot(path='screenshot_open.png')")
                    steps.append(f"            results['screenshots'].append('screenshot_open.png')")
            
            elif '點擊' in line or 'click' in line.lower():
                element = self.extract_element(line)
                steps.append(f"            page.click('{element}')")
                steps.append(f"            page.screenshot(path='screenshot_click.png')")
                steps.append(f"            results['screenshots'].append('screenshot_click.png')")
            
            elif '輸入' in line or 'input' in line.lower() or 'type' in line.lower():
                element, text = self.extract_input_info(line)
                steps.append(f"            page.fill('{element}', '{text}')")
                steps.append(f"            page.screenshot(path='screenshot_input.png')")
                steps.append(f"            results['screenshots'].append('screenshot_input.png')")
            
            elif '等待' in line or 'wait' in line.lower():
                wait_time = self.extract_wait_time(line)
                steps.append(f"            time.sleep({wait_time})")
            
            elif '驗證' in line or 'verify' in line.lower() or 'check' in line.lower():
                element = self.extract_element(line)
                steps.append(f"            assert page.is_visible('{element}'), '元素不可見'")
                steps.append(f"            page.screenshot(path='screenshot_verify.png')")
                steps.append(f"            results['screenshots'].append('screenshot_verify.png')")
        
        if not steps:
            # 默認步驟
            steps = [
                "            page.goto('https://example.com')",
                "            page.screenshot(path='screenshot_default.png')",
                "            results['screenshots'].append('screenshot_default.png')"
            ]
        
        return '\n'.join(steps)
    
    def parse_description_to_api_steps(self, description: str) -> str:
        """解析文本描述為API測試步驟"""
        steps = []
        lines = description.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'GET' in line.upper():
                url = self.extract_url(line)
                steps.append(f"        response = requests.get('{url}')")
                steps.append(f"        results['api_calls'].append({{'method': 'GET', 'url': '{url}', 'status': response.status_code}})")
            
            elif 'POST' in line.upper():
                url = self.extract_url(line)
                steps.append(f"        response = requests.post('{url}', json={{}})")
                steps.append(f"        results['api_calls'].append({{'method': 'POST', 'url': '{url}', 'status': response.status_code}})")
        
        if not steps:
            steps = [
                "        response = requests.get('https://api.example.com/health')",
                "        results['api_calls'].append({'method': 'GET', 'url': 'https://api.example.com/health', 'status': response.status_code})"
            ]
        
        return '\n'.join(steps)
    
    def extract_url(self, text: str) -> str:
        """提取URL"""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, text)
        if match:
            return match.group()
        
        # 如果沒有找到完整URL，嘗試提取域名
        if 'example.com' in text:
            return 'https://example.com'
        
        return 'https://example.com'
    
    def extract_element(self, text: str) -> str:
        """提取元素選擇器"""
        # 簡化的元素提取邏輯
        if '按鈕' in text or 'button' in text.lower():
            return 'button'
        elif '輸入框' in text or 'input' in text.lower():
            return 'input'
        elif '連結' in text or 'link' in text.lower():
            return 'a'
        else:
            return '[data-testid="element"]'
    
    def extract_input_info(self, text: str) -> Tuple[str, str]:
        """提取輸入信息"""
        element = self.extract_element(text)
        
        # 簡化的文本提取
        if '"' in text:
            parts = text.split('"')
            if len(parts) >= 2:
                return element, parts[1]
        
        return element, 'test input'
    
    def extract_wait_time(self, text: str) -> int:
        """提取等待時間"""
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return 2

class ScreenshotAnalyzer:
    """截圖分析器"""
    
    def __init__(self):
        self.setup_analyzer()
    
    def setup_analyzer(self):
        """設置分析器"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_screenshot(self, screenshot_path: str) -> Dict[str, Any]:
        """分析截圖"""
        try:
            # 讀取圖像
            image = cv2.imread(screenshot_path)
            if image is None:
                return {'error': '無法讀取截圖文件'}
            
            analysis_result = {
                'file_path': screenshot_path,
                'timestamp': datetime.now().isoformat(),
                'image_info': self.get_image_info(image),
                'ui_elements': self.detect_ui_elements(image),
                'text_content': self.extract_text(image),
                'color_analysis': self.analyze_colors(image),
                'anomaly_detection': self.detect_anomalies(image)
            }
            
            return analysis_result
            
        except Exception as e:
            return {'error': f'截圖分析失敗: {str(e)}'}
    
    def get_image_info(self, image: np.ndarray) -> Dict[str, Any]:
        """獲取圖像基本信息"""
        height, width, channels = image.shape
        return {
            'width': width,
            'height': height,
            'channels': channels,
            'size_mb': (height * width * channels) / (1024 * 1024)
        }
    
    def detect_ui_elements(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """檢測UI元素"""
        elements = []
        
        # 轉換為灰度圖
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 檢測矩形（可能是按鈕或輸入框）
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # 過濾小的噪聲
                x, y, w, h = cv2.boundingRect(contour)
                elements.append({
                    'type': 'rectangle',
                    'position': {'x': int(x), 'y': int(y)},
                    'size': {'width': int(w), 'height': int(h)},
                    'area': int(area)
                })
        
        return elements[:10]  # 限制返回數量
    
    def extract_text(self, image: np.ndarray) -> List[str]:
        """提取文本內容"""
        # 簡化的文本提取（實際使用中可以集成OCR）
        try:
            # 這裡可以集成pytesseract或其他OCR工具
            # import pytesseract
            # text = pytesseract.image_to_string(image)
            # return text.split('\n')
            
            # 暫時返回模擬結果
            return ['模擬提取的文本內容', '按鈕文字', '標題文字']
        except:
            return []
    
    def analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """分析顏色"""
        # 計算主要顏色
        pixels = image.reshape(-1, 3)
        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
        
        # 獲取最常見的顏色
        top_color_idx = np.argmax(counts)
        dominant_color = unique_colors[top_color_idx].tolist()
        
        return {
            'dominant_color': dominant_color,
            'total_unique_colors': len(unique_colors),
            'brightness': float(np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
        }
    
    def detect_anomalies(self, image: np.ndarray) -> List[str]:
        """檢測異常"""
        anomalies = []
        
        # 檢測是否有錯誤對話框（紅色區域）
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        red_mask = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
        red_area = cv2.countNonZero(red_mask)
        
        if red_area > 1000:
            anomalies.append('檢測到可能的錯誤對話框')
        
        # 檢測是否圖像過暗或過亮
        brightness = np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        if brightness < 50:
            anomalies.append('圖像過暗')
        elif brightness > 200:
            anomalies.append('圖像過亮')
        
        return anomalies

class RemoteExecutionAPI:
    """遠程執行API"""
    
    def __init__(self, base_dir: str = "/home/ubuntu/Powerauto.ai/cross_platform_testing"):
        self.base_dir = Path(base_dir)
        self.setup_api()
        self.encryption_manager = EncryptionManager()
        self.text_to_code = TextToCodeGenerator()
        self.screenshot_analyzer = ScreenshotAnalyzer()
        self.remote_agents = {}
        
    def setup_api(self):
        """設置API"""
        directories = [
            "test_cases",
            "executions",
            "screenshots",
            "generated_code",
            "results",
            "agents",
            "encrypted_data"
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"✅ 跨平台測試系統已設置: {self.base_dir}")
    
    def register_remote_agent(self, platform: TestPlatform, endpoint: str, 
                            api_key: str, capabilities: List[str]) -> str:
        """註冊遠程代理"""
        agent_id = hashlib.md5(f"{platform.value}{endpoint}{time.time()}".encode()).hexdigest()[:12]
        
        agent = RemoteAgent(
            agent_id=agent_id,
            platform=platform,
            endpoint=endpoint,
            api_key=api_key,
            status="active",
            capabilities=capabilities,
            last_heartbeat=datetime.now().isoformat()
        )
        
        self.remote_agents[agent_id] = agent
        
        # 保存代理信息
        agent_file = self.base_dir / "agents" / f"{agent_id}.json"
        with open(agent_file, 'w', encoding='utf-8') as f:
            agent_dict = asdict(agent)
            # 轉換枚舉為字符串
            agent_dict['platform'] = agent.platform.value
            json.dump(agent_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ 遠程代理已註冊: {agent_id} ({platform.value})")
        return agent_id
    
    def create_test_case(self, name: str, description: str, platform: TestPlatform,
                        test_type: TestType, text_description: str,
                        expected_result: Dict[str, Any] = None) -> TestCase:
        """創建測試用例"""
        test_id = hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:12]
        
        # 生成測試代碼
        test_case = TestCase(
            test_id=test_id,
            name=name,
            description=description,
            platform=platform,
            test_type=test_type,
            text_description=text_description,
            generated_code="",  # 稍後生成
            expected_result=expected_result or {},
            metadata={
                'created_by': 'PowerAutomation',
                'version': '1.0'
            },
            created_at=datetime.now().isoformat()
        )
        
        # 根據測試類型生成代碼
        if test_type == TestType.UI_AUTOMATION:
            test_case.generated_code = self.text_to_code.generate_playwright_code(test_case)
        elif test_type == TestType.API_TESTING:
            test_case.generated_code = self.text_to_code.generate_api_test_code(test_case)
        
        # 保存測試用例
        test_case_file = self.base_dir / "test_cases" / f"{test_id}.json"
        with open(test_case_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(test_case), f, indent=2, ensure_ascii=False)
        
        # 保存生成的代碼
        if test_case.generated_code:
            code_file = self.base_dir / "generated_code" / f"{test_id}.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(test_case.generated_code)
        
        self.logger.info(f"✅ 測試用例已創建: {test_id}")
        return test_case
    
    async def execute_test_remote(self, test_case: TestCase, agent_id: str) -> TestExecution:
        """遠程執行測試"""
        execution_id = hashlib.md5(f"{test_case.test_id}{agent_id}{time.time()}".encode()).hexdigest()[:12]
        
        execution = TestExecution(
            execution_id=execution_id,
            test_case_id=test_case.test_id,
            platform=test_case.platform,
            status=TestStatus.PENDING,
            start_time=datetime.now().isoformat(),
            end_time=None,
            execution_time=None,
            result={},
            screenshots=[],
            logs=[],
            error_message=None
        )
        
        try:
            agent = self.remote_agents.get(agent_id)
            if not agent:
                raise ValueError(f"找不到代理: {agent_id}")
            
            execution.status = TestStatus.RUNNING
            
            # 加密測試代碼
            encrypted_code = self.encryption_manager.encrypt_data(test_case.generated_code)
            
            # 準備遠程執行請求
            request_data = {
                'execution_id': execution_id,
                'test_case_id': test_case.test_id,
                'encrypted_code': encrypted_code,
                'test_type': test_case.test_type.value,
                'expected_result': test_case.expected_result
            }
            
            # 發送到遠程代理
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{agent.endpoint}/execute",
                    json=request_data,
                    headers={'Authorization': f'Bearer {agent.api_key}'},
                    timeout=aiohttp.ClientTimeout(total=300)  # 5分鐘超時
                ) as response:
                    if response.status == 200:
                        result_data = await response.json()
                        execution.result = result_data.get('result', {})
                        execution.screenshots = result_data.get('screenshots', [])
                        execution.logs = result_data.get('logs', [])
                        execution.status = TestStatus.COMPLETED
                    else:
                        execution.error_message = f"遠程執行失敗: HTTP {response.status}"
                        execution.status = TestStatus.FAILED
            
        except asyncio.TimeoutError:
            execution.error_message = "執行超時"
            execution.status = TestStatus.TIMEOUT
        except Exception as e:
            execution.error_message = str(e)
            execution.status = TestStatus.FAILED
        
        execution.end_time = datetime.now().isoformat()
        if execution.start_time and execution.end_time:
            start = datetime.fromisoformat(execution.start_time)
            end = datetime.fromisoformat(execution.end_time)
            execution.execution_time = (end - start).total_seconds()
        
        # 保存執行結果
        execution_file = self.base_dir / "executions" / f"{execution_id}.json"
        with open(execution_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(execution), f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ 測試執行完成: {execution_id} ({execution.status.value})")
        return execution
    
    def analyze_execution_screenshots(self, execution: TestExecution) -> Dict[str, Any]:
        """分析執行截圖"""
        analysis_results = {
            'execution_id': execution.execution_id,
            'total_screenshots': len(execution.screenshots),
            'screenshot_analyses': [],
            'summary': {}
        }
        
        for screenshot_path in execution.screenshots:
            # 假設截圖已經下載到本地
            local_screenshot_path = self.base_dir / "screenshots" / Path(screenshot_path).name
            
            if local_screenshot_path.exists():
                analysis = self.screenshot_analyzer.analyze_screenshot(str(local_screenshot_path))
                analysis_results['screenshot_analyses'].append(analysis)
        
        # 生成摘要
        if analysis_results['screenshot_analyses']:
            analysis_results['summary'] = {
                'total_ui_elements': sum(len(a.get('ui_elements', [])) for a in analysis_results['screenshot_analyses']),
                'anomalies_detected': sum(len(a.get('anomaly_detection', [])) for a in analysis_results['screenshot_analyses']),
                'avg_brightness': np.mean([a.get('color_analysis', {}).get('brightness', 0) for a in analysis_results['screenshot_analyses']])
            }
        
        return analysis_results
    
    def generate_test_report(self, executions: List[TestExecution]) -> str:
        """生成測試報告"""
        report_content = f"""# 跨平台測試執行報告

## 📊 測試概況

- **報告生成時間**: {datetime.now().isoformat()}
- **總測試數**: {len(executions)}
- **成功測試**: {len([e for e in executions if e.status == TestStatus.COMPLETED])}
- **失敗測試**: {len([e for e in executions if e.status == TestStatus.FAILED])}
- **超時測試**: {len([e for e in executions if e.status == TestStatus.TIMEOUT])}

## 📈 平台分布

"""
        
        # 統計平台分布
        platform_stats = {}
        for execution in executions:
            platform = execution.platform.value
            if platform not in platform_stats:
                platform_stats[platform] = {'total': 0, 'success': 0, 'failed': 0}
            
            platform_stats[platform]['total'] += 1
            if execution.status == TestStatus.COMPLETED:
                platform_stats[platform]['success'] += 1
            elif execution.status == TestStatus.FAILED:
                platform_stats[platform]['failed'] += 1
        
        for platform, stats in platform_stats.items():
            success_rate = (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
            report_content += f"- **{platform.upper()}**: {stats['total']} 測試, 成功率 {success_rate:.1f}%\n"
        
        report_content += f"""
## 🔍 詳細執行結果

| 執行ID | 測試用例 | 平台 | 狀態 | 執行時間 | 截圖數 |
|--------|----------|------|------|----------|--------|
"""
        
        for execution in executions:
            status_emoji = "✅" if execution.status == TestStatus.COMPLETED else "❌"
            execution_time = f"{execution.execution_time:.2f}s" if execution.execution_time else "N/A"
            
            report_content += f"| {execution.execution_id} | {execution.test_case_id} | {execution.platform.value} | {status_emoji} {execution.status.value} | {execution_time} | {len(execution.screenshots)} |\n"
        
        report_content += f"""
## 💡 關鍵洞察

### 性能分析
- **平均執行時間**: {np.mean([e.execution_time for e in executions if e.execution_time]):.2f} 秒
- **最快執行**: {min([e.execution_time for e in executions if e.execution_time], default=0):.2f} 秒
- **最慢執行**: {max([e.execution_time for e in executions if e.execution_time], default=0):.2f} 秒

### 錯誤分析
"""
        
        # 錯誤統計
        error_types = {}
        for execution in executions:
            if execution.error_message:
                error_type = execution.error_message.split(':')[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            report_content += f"- **{error_type}**: {count} 次\n"
        
        report_content += f"""
---

*報告生成時間: {datetime.now().isoformat()}*
"""
        
        return report_content

def main():
    """主函數 - 演示跨平台測試系統"""
    
    # 初始化系統
    api = RemoteExecutionAPI()
    
    print("🌐 跨平台測試系統演示開始...")
    
    # 1. 註冊遠程代理（模擬）
    print("📡 註冊遠程代理...")
    windows_agent = api.register_remote_agent(
        platform=TestPlatform.WINDOWS,
        endpoint="http://windows-agent:8080",
        api_key="windows_api_key_123",
        capabilities=["playwright", "screenshot", "plugin_execution"]
    )
    
    mac_agent = api.register_remote_agent(
        platform=TestPlatform.MACOS,
        endpoint="http://mac-agent:8080",
        api_key="mac_api_key_456",
        capabilities=["playwright", "screenshot", "plugin_execution"]
    )
    
    # 2. 創建測試用例
    print("📋 創建測試用例...")
    
    # UI自動化測試用例
    ui_test_case = api.create_test_case(
        name="PowerAutomation插件測試",
        description="測試PowerAutomation插件在Windows環境的執行",
        platform=TestPlatform.WINDOWS,
        test_type=TestType.UI_AUTOMATION,
        text_description="""
        1. 打開PowerAutomation應用程序
        2. 點擊"新建任務"按鈕
        3. 輸入任務描述"測試任務"
        4. 點擊"執行"按鈕
        5. 等待3秒
        6. 驗證任務執行成功
        """,
        expected_result={"task_created": True, "execution_success": True}
    )
    
    # API測試用例
    api_test_case = api.create_test_case(
        name="PowerAutomation API測試",
        description="測試PowerAutomation API端點",
        platform=TestPlatform.LINUX,
        test_type=TestType.API_TESTING,
        text_description="""
        1. GET /api/health - 檢查健康狀態
        2. POST /api/tasks - 創建新任務
        3. GET /api/tasks - 獲取任務列表
        """,
        expected_result={"health_check": True, "task_creation": True}
    )
    
    print(f"✅ 創建了 2 個測試用例")
    
    # 3. 模擬執行測試（實際環境中會是異步執行）
    print("⚡ 模擬測試執行...")
    
    # 創建模擬執行結果
    executions = []
    
    # Windows UI測試執行
    ui_execution = TestExecution(
        execution_id="exec_ui_001",
        test_case_id=ui_test_case.test_id,
        platform=TestPlatform.WINDOWS,
        status=TestStatus.COMPLETED,
        start_time=datetime.now().isoformat(),
        end_time=(datetime.now()).isoformat(),
        execution_time=15.5,
        result={"task_created": True, "execution_success": True},
        screenshots=["screenshot_1.png", "screenshot_2.png", "screenshot_3.png"],
        logs=["應用程序啟動", "任務創建成功", "執行完成"],
        error_message=None
    )
    executions.append(ui_execution)
    
    # API測試執行
    api_execution = TestExecution(
        execution_id="exec_api_001",
        test_case_id=api_test_case.test_id,
        platform=TestPlatform.LINUX,
        status=TestStatus.COMPLETED,
        start_time=datetime.now().isoformat(),
        end_time=(datetime.now()).isoformat(),
        execution_time=2.3,
        result={"health_check": True, "task_creation": True},
        screenshots=[],
        logs=["API健康檢查通過", "任務創建API調用成功"],
        error_message=None
    )
    executions.append(api_execution)
    
    # 4. 生成測試報告
    print("📊 生成測試報告...")
    report_content = api.generate_test_report(executions)
    
    # 保存報告
    report_file = api.base_dir / "results" / f"test_report_{int(time.time())}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 測試報告已生成: {report_file}")
    
    # 5. 演示加解密功能
    print("🔐 演示加解密功能...")
    test_data = {"test": "PowerAutomation加密測試", "timestamp": datetime.now().isoformat()}
    encrypted = api.encryption_manager.encrypt_data(test_data)
    decrypted = api.encryption_manager.decrypt_data(encrypted)
    print(f"原始數據: {test_data}")
    print(f"解密數據: {decrypted}")
    print(f"加解密成功: {test_data == decrypted}")
    
    print("\n🎯 跨平台測試系統演示完成!")
    print(f"📁 系統目錄: {api.base_dir}")
    print(f"📊 測試報告: {report_file}")
    print(f"🤖 註冊代理: Windows({windows_agent}), Mac({mac_agent})")
    
    return api, executions, report_file

if __name__ == "__main__":
    main()

