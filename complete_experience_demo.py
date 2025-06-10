#!/usr/bin/env python3
"""
PowerAutomation 完整端側體驗 - 登錄後直接跳轉編碼器
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path
import os

async def create_complete_experience():
    """創建完整的端側體驗截圖"""
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # 1. 登錄頁面HTML（保持原有設計）
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
        .success-message {
            display: none;
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }
        .success-message.show {
            display: block;
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
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
                歡迎使用智能端雲協同系統，登錄後直接進入編碼器體驗
            </div>
            <div class="features">
                <div class="feature">
                    <i class="fas fa-code"></i>
                    VS Code級別編碼體驗
                </div>
                <div class="feature">
                    <i class="fas fa-brain"></i>
                    Qwen3本地+雲端8B模型
                </div>
                <div class="feature">
                    <i class="fas fa-users"></i>
                    Trae協作編程
                </div>
                <div class="feature">
                    <i class="fas fa-cloud"></i>
                    端雲協同智能路由
                </div>
                <div class="feature">
                    <i class="fas fa-chart-line"></i>
                    實時性能監控
                </div>
            </div>
        </div>
        
        <div class="login-right">
            <div class="device-info">
                <i class="fas fa-info-circle"></i>
                檢測到設備: <span>Windows 11</span> | 
                瀏覽器: <span>Chrome 120</span> |
                IP: <span>192.168.1.100</span>
            </div>
            
            <div class="success-message" id="successMessage">
                <i class="fas fa-check-circle"></i>
                登錄成功！正在跳轉到編碼器...
            </div>
            
            <div class="form-group">
                <label for="username">用戶名</label>
                <input type="text" id="username" name="username" placeholder="請輸入用戶名" value="admin">
            </div>
            
            <div class="form-group">
                <label for="password">密碼</label>
                <input type="password" id="password" name="password" placeholder="請輸入密碼" value="admin123">
            </div>
            
            <button type="button" class="login-btn" onclick="handleLogin()">
                <i class="fas fa-sign-in-alt"></i> 登錄並進入編碼器
            </button>
        </div>
    </div>

    <script>
        function handleLogin() {
            // 顯示成功消息
            document.getElementById('successMessage').classList.add('show');
            
            // 2秒後跳轉到編碼器
            setTimeout(() => {
                window.location.href = 'vscode_editor.html';
            }, 2000);
        }
    </script>
</body>
</html>
    '''
    
    # 2. VS Code風格編碼器HTML（基於用戶截圖設計）
    vscode_editor_html = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation - VS Code編碼器</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #cccccc;
            height: 100vh;
            overflow: hidden;
        }
        
        /* 頂部標題欄 */
        .title-bar {
            background: #323233;
            height: 35px;
            display: flex;
            align-items: center;
            padding: 0 15px;
            border-bottom: 1px solid #2d2d30;
        }
        .title-bar .traffic-lights {
            display: flex;
            gap: 8px;
            margin-right: 15px;
        }
        .traffic-light {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .traffic-light.red { background: #ff5f57; }
        .traffic-light.yellow { background: #ffbd2e; }
        .traffic-light.green { background: #28ca42; }
        .title-bar .title {
            flex: 1;
            font-size: 13px;
            color: #cccccc;
        }
        .title-bar .controls {
            display: flex;
            gap: 10px;
            font-size: 12px;
            color: #cccccc;
        }
        
        /* 主容器 */
        .main-container {
            display: flex;
            height: calc(100vh - 35px);
        }
        
        /* 左側活動欄 */
        .activity-bar {
            width: 48px;
            background: #333333;
            border-right: 1px solid #2d2d30;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px 0;
        }
        .activity-item {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
            cursor: pointer;
            border-radius: 4px;
            transition: background 0.2s ease;
        }
        .activity-item:hover {
            background: #2a2d2e;
        }
        .activity-item.active {
            background: #37373d;
            border-left: 2px solid #007acc;
        }
        .activity-item i {
            font-size: 16px;
            color: #cccccc;
        }
        
        /* 左側邊欄 */
        .sidebar {
            width: 300px;
            background: #252526;
            border-right: 1px solid #2d2d30;
            display: flex;
            flex-direction: column;
        }
        .sidebar-header {
            padding: 10px 15px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            color: #cccccc;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .sidebar-content {
            flex: 1;
            overflow-y: auto;
        }
        .file-tree {
            padding: 10px 0;
        }
        .file-item {
            padding: 4px 20px;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .file-item:hover {
            background: #2a2d2e;
        }
        .file-item i {
            font-size: 12px;
            color: #75beff;
        }
        .folder-item {
            padding: 4px 15px;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
        }
        .folder-item:hover {
            background: #2a2d2e;
        }
        .folder-item i {
            font-size: 12px;
            color: #cccccc;
        }
        
        /* 主編輯區域 */
        .editor-area {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .tab-bar {
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            align-items: center;
            min-height: 35px;
        }
        .tab {
            padding: 8px 16px;
            background: #2d2d30;
            border-right: 1px solid #3e3e42;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s ease;
        }
        .tab.active {
            background: #1e1e1e;
        }
        .tab:hover {
            background: #37373d;
        }
        .tab i {
            font-size: 12px;
        }
        .tab .close {
            margin-left: 8px;
            opacity: 0.7;
            font-size: 10px;
        }
        .tab .close:hover {
            opacity: 1;
        }
        
        /* 編輯器內容 */
        .editor-content {
            flex: 1;
            background: #1e1e1e;
            position: relative;
            display: flex;
        }
        .line-numbers {
            background: #1e1e1e;
            color: #858585;
            padding: 20px 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.5;
            text-align: right;
            user-select: none;
            border-right: 1px solid #2d2d30;
            min-width: 50px;
        }
        .code-area {
            flex: 1;
            padding: 20px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.5;
            overflow-y: auto;
        }
        .code-line {
            margin-bottom: 2px;
        }
        .keyword { color: #569cd6; }
        .string { color: #ce9178; }
        .comment { color: #6a9955; }
        .function { color: #dcdcaa; }
        .number { color: #b5cea8; }
        .operator { color: #d4d4d4; }
        
        /* 右側面板 */
        .right-panel {
            width: 350px;
            background: #252526;
            border-left: 1px solid #2d2d30;
            display: flex;
            flex-direction: column;
        }
        .panel-header {
            padding: 10px 15px;
            background: #2d2d30;
            border-bottom: 1px solid #3e3e42;
            font-size: 14px;
            font-weight: 600;
            color: #cccccc;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .panel-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .trae-section {
            margin-bottom: 25px;
        }
        .trae-title {
            font-size: 16px;
            font-weight: 600;
            color: #cccccc;
            margin-bottom: 15px;
            text-align: center;
        }
        .chat-area {
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            min-height: 200px;
        }
        .chat-input {
            background: #2d2d30;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 10px 15px;
            color: #cccccc;
            width: 100%;
            font-size: 13px;
            resize: none;
            min-height: 80px;
        }
        .chat-input:focus {
            outline: none;
            border-color: #007acc;
        }
        .chat-controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .chat-btn {
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
        }
        .chat-btn:hover {
            background: #1177bb;
        }
        .model-indicator {
            background: #2d2d30;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            color: #9cdcfe;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
        }
        .status-dot {
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
        
        /* 底部狀態欄 */
        .status-bar {
            background: #007acc;
            color: white;
            padding: 5px 15px;
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
    </style>
</head>
<body>
    <!-- 頂部標題欄 -->
    <div class="title-bar">
        <div class="traffic-lights">
            <div class="traffic-light red"></div>
            <div class="traffic-light yellow"></div>
            <div class="traffic-light green"></div>
        </div>
        <div class="title">
            <i class="fas fa-cube"></i> communitypowerauto
        </div>
        <div class="controls">
            <span><i class="fas fa-download"></i> 點擊重啟以更新</span>
        </div>
    </div>

    <div class="main-container">
        <!-- 左側活動欄 -->
        <div class="activity-bar">
            <div class="activity-item active">
                <i class="fas fa-folder"></i>
            </div>
            <div class="activity-item">
                <i class="fas fa-search"></i>
            </div>
            <div class="activity-item">
                <i class="fas fa-code-branch"></i>
            </div>
            <div class="activity-item">
                <i class="fas fa-play"></i>
            </div>
            <div class="activity-item">
                <i class="fas fa-bug"></i>
            </div>
            <div class="activity-item">
                <i class="fas fa-cube"></i>
            </div>
            <div class="activity-item">
                <i class="fas fa-user"></i>
            </div>
            <div class="activity-item">
                <i class="fas fa-cog"></i>
            </div>
        </div>

        <!-- 左側邊欄 -->
        <div class="sidebar">
            <div class="sidebar-header">
                資源管理器
                <i class="fas fa-ellipsis-h"></i>
            </div>
            <div class="sidebar-content">
                <div class="file-tree">
                    <div class="folder-item">
                        <i class="fas fa-chevron-right"></i>
                        文件
                    </div>
                    <div class="folder-item">
                        <i class="fas fa-chevron-right"></i>
                        大綱
                    </div>
                    <div class="folder-item">
                        <i class="fas fa-chevron-right"></i>
                        時間線
                    </div>
                </div>
            </div>
        </div>

        <!-- 主編輯區域 -->
        <div class="editor-area">
            <div class="tab-bar">
                <!-- 空的標籤欄，準備顯示文件 -->
            </div>
            <div class="editor-content">
                <div style="flex: 1; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #858585;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                            <button class="chat-btn" style="padding: 10px 20px; font-size: 14px;">
                                <i class="fas fa-comments"></i> 與 AI 對話
                                <span style="margin-left: 10px; background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px; font-size: 11px;">⌘ U</span>
                            </button>
                            <button class="chat-btn" style="padding: 10px 20px; font-size: 14px;">
                                <i class="fas fa-code"></i> Editor 內 AI 編碼
                                <span style="margin-left: 10px; background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px; font-size: 11px;">⌘ I</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 右側Trae協作面板 -->
        <div class="right-panel">
            <div class="panel-header">
                Trae
                <div style="display: flex; gap: 10px;">
                    <i class="fas fa-user"></i>
                    <i class="fas fa-clock"></i>
                    <i class="fas fa-cog"></i>
                    <i class="fas fa-times"></i>
                </div>
            </div>
            <div class="panel-content">
                <div class="trae-title">與 Trae 協作</div>
                
                <div class="model-indicator">
                    <div class="status-dot"></div>
                    <span><i class="fas fa-brain"></i> Claude-3.7-Sonnet</span>
                </div>
                
                <div class="chat-area">
                    <!-- 聊天內容區域 -->
                </div>
                
                <textarea class="chat-input" placeholder="⇧ ⏎ 切換歷史輸入，⏎ ⌘ ⏎ 執行"></textarea>
                
                <div class="chat-controls">
                    <button class="chat-btn">
                        <i class="fas fa-at"></i>
                    </button>
                    <button class="chat-btn">
                        <i class="fas fa-hashtag"></i>
                    </button>
                    <button class="chat-btn">
                        <i class="fas fa-paperclip"></i>
                    </button>
                    <button class="chat-btn" style="margin-left: auto;">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- 底部狀態欄 -->
    <div class="status-bar">
        <div class="status-left">
            <span><i class="fas fa-code"></i> Python</span>
            <span>UTF-8</span>
            <span>LF</span>
        </div>
        <div class="status-right">
            <span><i class="fas fa-bell"></i></span>
            <span><i class="fas fa-sync"></i></span>
            <span><i class="fas fa-wifi"></i> 已連接</span>
        </div>
    </div>
</body>
</html>
    '''
    
    # 保存HTML文件
    with open('login_to_editor.html', 'w', encoding='utf-8') as f:
        f.write(login_html)
    
    with open('vscode_editor.html', 'w', encoding='utf-8') as f:
        f.write(vscode_editor_html)
    
    print("🚀 開始創建完整端側體驗截圖...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            # 1. 登錄頁面截圖
            print("📸 截圖1: PowerAutomation 登錄頁面（優化版）")
            await page.goto(f'file://{os.path.abspath("login_to_editor.html")}')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=screenshots_dir / '01_login_optimized.png')
            
            # 2. 點擊登錄按鈕，顯示成功消息
            print("📸 截圖2: 登錄成功消息")
            await page.click('.login-btn')
            await asyncio.sleep(1)  # 等待成功消息顯示
            await page.screenshot(path=screenshots_dir / '02_login_success.png')
            
            # 3. VS Code風格編碼器截圖
            print("📸 截圖3: VS Code風格編碼器（基於用戶需求）")
            await page.goto(f'file://{os.path.abspath("vscode_editor.html")}')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=screenshots_dir / '03_vscode_editor.png')
            
            print("✅ 完整端側體驗截圖完成！")
            
        except Exception as e:
            print(f"❌ 截圖過程中發生錯誤: {e}")
        finally:
            await browser.close()
    
    # 清理臨時文件
    if os.path.exists('login_to_editor.html'):
        os.remove('login_to_editor.html')
    if os.path.exists('vscode_editor.html'):
        os.remove('vscode_editor.html')
    
    print(f"\n🎉 PowerAutomation 完整端側體驗截圖完成！")
    print(f"📁 截圖保存在: {screenshots_dir.absolute()}")
    
    # 顯示生成的截圖
    for screenshot in sorted(screenshots_dir.glob("*.png")):
        print(f"  📸 {screenshot.name}")

if __name__ == "__main__":
    asyncio.run(create_complete_experience())

