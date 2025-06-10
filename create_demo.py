#!/usr/bin/env python3
import subprocess
import time
import os

def create_simple_demo():
    """創建簡單的演示截圖"""
    
    # 創建演示HTML文件
    demo_html = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 統一藍色系演示</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3b82f6 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .demo-container {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(15px);
            border-radius: 24px;
            box-shadow: 0 25px 50px rgba(30, 60, 114, 0.2);
            overflow: hidden;
            width: 100%;
            max-width: 1200px;
            min-height: 700px;
            display: flex;
            border: 1px solid rgba(59, 130, 246, 0.1);
        }
        .status-sidebar {
            width: 280px;
            background: linear-gradient(180deg, #1e40af 0%, #1d4ed8 50%, #2563eb 100%);
            color: white;
            padding: 30px 25px;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }
        .platform-badge {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            text-align: center;
            margin-bottom: 30px;
        }
        .platform-type {
            font-size: 14px;
            font-weight: 600;
            color: #e0f2fe;
            margin-bottom: 4px;
        }
        .platform-name {
            font-size: 18px;
            font-weight: 700;
            color: white;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        .status-card h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #e0f2fe;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .model-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .credit-amount {
            font-size: 28px;
            font-weight: 700;
            color: #fbbf24;
            margin-bottom: 8px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        .savings-percentage {
            font-size: 20px;
            font-weight: 700;
            color: #10b981;
            text-align: center;
            margin-top: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        .main-content {
            flex: 1;
            padding: 60px 50px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        }
        .demo-header {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 20px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
            font-size: 36px;
            color: white;
        }
        .demo-title {
            font-size: 32px;
            font-weight: 700;
            color: #1e40af;
            margin-bottom: 8px;
        }
        .demo-subtitle {
            font-size: 16px;
            color: #64748b;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 30px;
        }
        .feature-card {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        .feature-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
        }
        .feature-icon {
            font-size: 24px;
            color: #3b82f6;
            margin-bottom: 10px;
        }
        .feature-title {
            font-size: 16px;
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 5px;
        }
        .feature-desc {
            font-size: 14px;
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="demo-container">
        <!-- 左側狀態區域 -->
        <div class="status-sidebar">
            <!-- 平台標識 -->
            <div class="platform-badge">
                <div class="platform-type">端側系統</div>
                <div class="platform-name">PowerAutomation</div>
            </div>

            <!-- 當前模型狀態 -->
            <div class="status-card">
                <h3>🧠 當前模型</h3>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <div class="model-indicator"></div>
                    <div>
                        <div style="font-size: 15px; font-weight: 600; color: white;">Qwen3 本地</div>
                        <div style="font-size: 12px; color: #bfdbfe; background: rgba(255, 255, 255, 0.1); padding: 2px 8px; border-radius: 6px; display: inline-block;">本地推理</div>
                    </div>
                </div>
                <div style="font-size: 12px; color: #bfdbfe;">⚡ 響應時間: 1.2s</div>
            </div>

            <!-- 積分狀態 -->
            <div class="status-card">
                <h3>💰 積分餘額</h3>
                <div class="credit-amount">2,580</div>
                <div style="font-size: 12px; color: #bfdbfe;">可用積分</div>
                <div style="font-size: 12px; color: #bfdbfe; margin-top: 8px;">🔄 最後同步: 剛剛</div>
            </div>

            <!-- Token節省統計 -->
            <div class="status-card">
                <h3>📊 節省統計</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 13px; color: #bfdbfe;">本地處理</span>
                    <span style="font-size: 15px; font-weight: 600; color: #10b981;">73%</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 13px; color: #bfdbfe;">雲端處理</span>
                    <span style="font-size: 15px; font-weight: 600; color: #10b981;">27%</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-size: 13px; color: #bfdbfe;">今日節省</span>
                    <span style="font-size: 15px; font-weight: 600; color: #10b981;">1,240 tokens</span>
                </div>
                <div class="savings-percentage">45% 節省</div>
            </div>

            <!-- 連接狀態 -->
            <div style="margin-top: auto; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; align-items: center; gap: 8px; font-size: 12px; color: #bfdbfe;">
                    <div style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></div>
                    <span>端雲協同已連接</span>
                </div>
            </div>
        </div>

        <!-- 右側主內容區域 -->
        <div class="main-content">
            <div class="demo-header">
                <div class="logo">🤖</div>
                <h1 class="demo-title">PowerAutomation</h1>
                <p class="demo-subtitle">統一藍色系智能端雲協同系統</p>
            </div>

            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">🎨</div>
                    <div class="feature-title">統一設計系統</div>
                    <div class="feature-desc">三平台一致的藍色系設計語言</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">智能模型切換</div>
                    <div class="feature-desc">Qwen3本地 ↔ Qwen8B雲端</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💰</div>
                    <div class="feature-title">實時積分同步</div>
                    <div class="feature-desc">端雲協同積分管理系統</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">Token節省統計</div>
                    <div class="feature-desc">實時顯示端雲協同效率</div>
                </div>
            </div>

            <div style="text-align: center; margin-top: 40px;">
                <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 16px 32px; border-radius: 12px; display: inline-block; font-weight: 600; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);">
                    🚀 PowerAutomation v0.5.2 統一體驗演示
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open('/home/ubuntu/Powerauto.ai/demo.html', 'w', encoding='utf-8') as f:
        f.write(demo_html)
    
    print("演示文件已創建: /home/ubuntu/Powerauto.ai/demo.html")

if __name__ == '__main__':
    create_simple_demo()

