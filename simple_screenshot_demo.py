#!/usr/bin/env python3
"""
簡化版Playwright截圖演示
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import subprocess
import time
import os

async def create_simple_demo():
    """創建簡化的演示截圖"""
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # 創建簡單的HTML文件用於截圖
    login_html = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 登錄</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            width: 100%;
            max-width: 1000px;
            min-height: 600px;
            display: flex;
        }
        .login-left {
            flex: 1;
            background: linear-gradient(45deg, #2c3e50, #3498db);
            color: white;
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .logo {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .logo i {
            color: #f39c12;
            margin-right: 10px;
        }
        .welcome-text {
            font-size: 1.2em;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        .features {
            list-style: none;
        }
        .feature {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            font-size: 1em;
        }
        .feature i {
            color: #f39c12;
            margin-right: 15px;
            width: 20px;
        }
        .login-right {
            flex: 1;
            padding: 60px 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .login-tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #ecf0f1;
        }
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        .tab.active {
            border-bottom-color: #3498db;
            color: #3498db;
        }
        .form-group {
            margin-bottom: 25px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #2c3e50;
        }
        .form-group input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #ecf0f1;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }
        .form-group input:focus {
            outline: none;
            border-color: #3498db;
            background: white;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        .login-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        }
        .device-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-left">
            <div class="logo">
                <i class="fas fa-robot"></i>
                PowerAutomation
            </div>
            <div class="welcome-text">
                歡迎使用智能端雲協同系統，體驗下一代AI驅動的自動化平台
            </div>
            <div class="features">
                <div class="feature">
                    <i class="fas fa-cloud"></i>
                    端雲協同智能路由
                </div>
                <div class="feature">
                    <i class="fas fa-brain"></i>
                    Qwen3本地+雲端8B模型
                </div>
                <div class="feature">
                    <i class="fas fa-code"></i>
                    智能代碼編輯器協同
                </div>
                <div class="feature">
                    <i class="fas fa-shield-alt"></i>
                    企業級安全保護
                </div>
                <div class="feature">
                    <i class="fas fa-chart-line"></i>
                    實時性能監控
                </div>
            </div>
        </div>
        
        <div class="login-right">
            <div class="login-tabs">
                <div class="tab active">
                    <i class="fas fa-key"></i> 密碼登錄
                </div>
                <div class="tab">
                    <i class="fas fa-qrcode"></i> QR碼登錄
                </div>
                <div class="tab">
                    <i class="fas fa-ticket-alt"></i> Token登錄
                </div>
            </div>

            <div class="device-info">
                <i class="fas fa-info-circle"></i>
                檢測到設備: <span>Windows 11</span> | 
                瀏覽器: <span>Chrome 120</span> |
                IP: <span>192.168.1.100</span>
            </div>
            
            <div class="form-group">
                <label for="username">用戶名</label>
                <input type="text" id="username" name="username" placeholder="請輸入用戶名" value="admin">
            </div>
            
            <div class="form-group">
                <label for="password">密碼</label>
                <input type="password" id="password" name="password" placeholder="請輸入密碼" value="admin123">
            </div>
            
            <button type="button" class="login-btn">
                <i class="fas fa-sign-in-alt"></i> 登錄
            </button>
        </div>
    </div>
</body>
</html>
    '''
    
    editor_html = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 智能代碼編輯器</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            overflow: hidden;
        }
        .editor-container {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 300px;
            background: #252526;
            border-right: 1px solid #3e3e42;
            display: flex;
            flex-direction: column;
        }
        .sidebar-header {
            padding: 15px 20px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .sidebar-title {
            font-weight: 600;
            color: #cccccc;
        }
        .ai-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
        }
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4caf50;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .ai-panel {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .ai-section {
            margin-bottom: 25px;
        }
        .ai-section h3 {
            color: #569cd6;
            margin-bottom: 12px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .model-selector {
            background: #3c3c3c;
            border: 1px solid #464647;
            border-radius: 6px;
            padding: 8px 12px;
            color: #cccccc;
            width: 100%;
            margin-bottom: 15px;
        }
        .suggestion-item {
            background: #2d2d30;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .suggestion-item:hover {
            background: #37373d;
            border-color: #569cd6;
        }
        .suggestion-code {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            background: #1e1e1e;
            padding: 8px;
            border-radius: 4px;
            margin: 8px 0;
            overflow-x: auto;
        }
        .suggestion-desc {
            font-size: 12px;
            color: #9cdcfe;
            margin-bottom: 5px;
        }
        .confidence-bar {
            height: 3px;
            background: #3e3e42;
            border-radius: 2px;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #f44336, #ff9800, #4caf50);
            transition: width 0.3s ease;
        }
        .main-editor {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .editor-toolbar {
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .file-tabs {
            display: flex;
            gap: 2px;
        }
        .file-tab {
            background: #3c3c3c;
            border: 1px solid #464647;
            border-bottom: none;
            padding: 8px 16px;
            border-radius: 6px 6px 0 0;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .file-tab.active {
            background: #1e1e1e;
            border-color: #569cd6;
        }
        .editor-actions {
            display: flex;
            gap: 10px;
        }
        .action-btn {
            background: #0e639c;
            border: none;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: background 0.2s ease;
        }
        .action-btn:hover {
            background: #1177bb;
        }
        .editor-content {
            flex: 1;
            position: relative;
            background: #1e1e1e;
            padding: 20px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.5;
            overflow-y: auto;
        }
        .code-line {
            margin-bottom: 2px;
            padding: 2px 0;
        }
        .line-number {
            color: #858585;
            margin-right: 20px;
            user-select: none;
        }
        .keyword { color: #569cd6; }
        .string { color: #ce9178; }
        .comment { color: #6a9955; }
        .function { color: #dcdcaa; }
        .status-bar {
            background: #007acc;
            color: white;
            padding: 5px 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .status-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .status-right {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .performance-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
        }
        .perf-good { color: #4caf50; }
    </style>
</head>
<body>
    <div class="editor-container">
        <!-- 左側AI助手面板 -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">
                    <i class="fas fa-robot"></i> AI 代碼助手
                </div>
                <div class="ai-status">
                    <div class="status-indicator"></div>
                    <span>Qwen3 本地</span>
                </div>
            </div>
            
            <div class="ai-panel">
                <!-- 模型選擇 -->
                <div class="ai-section">
                    <h3><i class="fas fa-brain"></i> 模型選擇</h3>
                    <select class="model-selector">
                        <option value="qwen3-local" selected>Qwen3 本地模型 (推薦)</option>
                        <option value="qwen8b-cloud">Qwen8B 雲端模型</option>
                        <option value="auto">智能自動選擇</option>
                    </select>
                </div>

                <!-- 實時建議 -->
                <div class="ai-section">
                    <h3><i class="fas fa-lightbulb"></i> 實時建議</h3>
                    <div>
                        <div class="suggestion-item">
                            <div class="suggestion-desc">函數定義建議</div>
                            <div class="suggestion-code">def process_data(data):</div>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 85%;"></div>
                            </div>
                        </div>
                        
                        <div class="suggestion-item">
                            <div class="suggestion-desc">導入語句</div>
                            <div class="suggestion-code">import pandas as pd</div>
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 92%;"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 性能統計 -->
                <div class="ai-section">
                    <h3><i class="fas fa-chart-line"></i> 性能統計</h3>
                    <div style="font-size: 12px; color: #9cdcfe;">
                        <div style="margin-bottom: 8px;">
                            <span>本地處理: </span>
                            <span style="color: #4caf50;">73%</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <span>雲端處理: </span>
                            <span style="color: #2196f3;">27%</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <span>Token節省: </span>
                            <span style="color: #ff9800;">45%</span>
                        </div>
                        <div>
                            <span>響應時間: </span>
                            <span style="color: #4caf50;">1.2s</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 主編輯器區域 -->
        <div class="main-editor">
            <div class="editor-toolbar">
                <div class="file-tabs">
                    <div class="file-tab active">
                        <i class="fab fa-python"></i>
                        main.py
                    </div>
                    <div class="file-tab">
                        <i class="fab fa-js"></i>
                        script.js
                    </div>
                </div>
                
                <div class="editor-actions">
                    <button class="action-btn">
                        <i class="fas fa-question-circle"></i> 解釋代碼
                    </button>
                    <button class="action-btn">
                        <i class="fas fa-magic"></i> 優化代碼
                    </button>
                </div>
            </div>
            
            <div class="editor-content">
                <div class="code-line">
                    <span class="line-number">1</span>
                    <span class="comment"># PowerAutomation 智能代碼示例</span>
                </div>
                <div class="code-line">
                    <span class="line-number">2</span>
                    <span class="keyword">import</span> <span>pandas</span> <span class="keyword">as</span> <span>pd</span>
                </div>
                <div class="code-line">
                    <span class="line-number">3</span>
                    <span class="keyword">import</span> <span>numpy</span> <span class="keyword">as</span> <span>np</span>
                </div>
                <div class="code-line">
                    <span class="line-number">4</span>
                    <span class="keyword">from</span> <span>typing</span> <span class="keyword">import</span> <span>List, Dict, Any</span>
                </div>
                <div class="code-line">
                    <span class="line-number">5</span>
                </div>
                <div class="code-line">
                    <span class="line-number">6</span>
                    <span class="keyword">def</span> <span class="function">process_data</span><span>(file_path: </span><span class="keyword">str</span><span>) -> pd.DataFrame:</span>
                </div>
                <div class="code-line">
                    <span class="line-number">7</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="string">"""處理CSV數據文件"""</span>
                </div>
                <div class="code-line">
                    <span class="line-number">8</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="keyword">try</span><span>:</span>
                </div>
                <div class="code-line">
                    <span class="line-number">9</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span>df = pd.read_csv(file_path)</span>
                </div>
                <div class="code-line">
                    <span class="line-number">10</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="keyword">return</span> <span>df</span>
                </div>
                <div class="code-line">
                    <span class="line-number">11</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="keyword">except</span> <span>Exception</span> <span class="keyword">as</span> <span>e</span><span>:</span>
                </div>
                <div class="code-line">
                    <span class="line-number">12</span>
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="function">print</span><span>(</span><span class="string">f"錯誤: {e}"</span><span>)</span>
                </div>
            </div>
        </div>
    </div>

    <!-- 狀態欄 -->
    <div class="status-bar">
        <div class="status-left">
            <span><i class="fas fa-code"></i> Python</span>
            <span>UTF-8</span>
            <span>第 12 行，第 23 列</span>
        </div>
        <div class="status-right">
            <div class="performance-indicator perf-good">
                <i class="fas fa-tachometer-alt"></i>
                <span>性能: 優秀</span>
            </div>
            <div class="performance-indicator perf-good">
                <i class="fas fa-wifi"></i>
                <span>連接: 正常</span>
            </div>
            <span>Qwen3 本地模型</span>
        </div>
    </div>
</body>
</html>
    '''
    
    # 保存HTML文件
    with open('login_demo.html', 'w', encoding='utf-8') as f:
        f.write(login_html)
    
    with open('editor_demo.html', 'w', encoding='utf-8') as f:
        f.write(editor_html)
    
    print("🚀 開始截圖演示...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # 1. 登錄頁面截圖
            print("📸 截圖1: PowerAutomation 登錄頁面")
            await page.goto(f'file://{os.path.abspath("login_demo.html")}')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=screenshots_dir / '01_powerauto_login.png')
            
            # 2. 代碼編輯器截圖
            print("📸 截圖2: PowerAutomation 智能代碼編輯器")
            await page.goto(f'file://{os.path.abspath("editor_demo.html")}')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=screenshots_dir / '02_powerauto_code_editor.png')
            
            print("✅ 截圖完成！")
            
        except Exception as e:
            print(f"❌ 截圖過程中發生錯誤: {e}")
        finally:
            await browser.close()
    
    # 清理臨時文件
    if os.path.exists('login_demo.html'):
        os.remove('login_demo.html')
    if os.path.exists('editor_demo.html'):
        os.remove('editor_demo.html')
    
    print(f"\n🎉 PowerAutomation UI 截圖演示完成！")
    print(f"📁 截圖保存在: {screenshots_dir.absolute()}")
    
    # 顯示生成的截圖
    for screenshot in sorted(screenshots_dir.glob("*.png")):
        print(f"  📸 {screenshot.name}")

if __name__ == "__main__":
    asyncio.run(create_simple_demo())

