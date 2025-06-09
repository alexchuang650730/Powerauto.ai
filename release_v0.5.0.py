#!/usr/bin/env python3
"""
PowerAutomation v0.5.0 Release Script
使用Enhanced Release Manager進行安全發布
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加項目路徑
sys.path.append('/home/ubuntu/Powerauto.ai')

try:
    from mcptool.core.development_tools.enhanced_release_manager import EnhancedReleaseManager
except ImportError as e:
    print(f"❌ 無法導入Enhanced Release Manager: {e}")
    sys.exit(1)

def main():
    """執行PowerAutomation v0.5.0發布"""
    
    print("🚀 PowerAutomation v0.5.0 Release Manager")
    print("=" * 50)
    
    # 初始化Release Manager
    try:
        rm = EnhancedReleaseManager('/home/ubuntu/Powerauto.ai')
        print("✅ Enhanced Release Manager初始化成功")
    except Exception as e:
        print(f"❌ Release Manager初始化失敗: {e}")
        return False
    
    # 創建v0.5.0發布配置
    release_config = {
        "version": "v0.5.0",
        "name": "PowerAutomation v0.5.0 - Enterprise Testing Framework",
        "description": """
PowerAutomation v0.5.0 重大更新：

🎯 核心新功能：
- Level 6: 企業級安全測試框架 (RBAC、合規驗證)
- Level 9: 競對比較分析框架 (基準測試比較)
- Level 10: 增強GAIA CLI框架 (標準基準測試)
- 意圖驅動智能引擎架構設計
- 開源營收模式分析 (200M目標)

📊 技術指標：
- 新增代碼: 293,116行
- 新增文件: 35個
- 測試框架: 3個完整層級
- 文檔體系: 14個分析文檔

🏆 企業級能力：
- 企業級安全框架
- 標準基準測試集成
- 競爭分析和市場定位
- 多智能體協作優化

🔧 技術突破：
- 意圖驅動的智能化架構
- 統一前端複雜性處理
- 後端標準化流程
- L4級別智能體協作能力
        """.strip(),
        "branch": "feature/v0.5.0-upgrade",
        "target_branch": "main",
        "release_type": "minor",
        "security_level": "enterprise",
        "changelog": [
            "feat: Add Level 6/9/10 testing frameworks",
            "feat: Implement intent-driven intelligent engine architecture", 
            "feat: Add enterprise-grade security testing framework",
            "feat: Add competitor analysis and benchmark comparison",
            "feat: Add enhanced GAIA CLI framework with standard benchmarks",
            "docs: Add comprehensive v0.5.0 planning and analysis documents",
            "docs: Add open source revenue model analysis",
            "tools: Add v0.5.0 maintenance tools and utilities"
        ],
        "breaking_changes": [],
        "migration_notes": "No breaking changes. All new features are additive.",
        "created_at": datetime.now().isoformat(),
        "created_by": "PowerAutomation Team"
    }
    
    print(f"\n📋 發布配置:")
    print(f"   版本: {release_config['version']}")
    print(f"   名稱: {release_config['name']}")
    print(f"   分支: {release_config['branch']}")
    print(f"   目標分支: {release_config['target_branch']}")
    print(f"   發布類型: {release_config['release_type']}")
    print(f"   安全級別: {release_config['security_level']}")
    
    # 執行安全發布
    print(f"\n🔐 開始執行安全發布流程...")
    
    try:
        # 創建安全發布
        pipeline_results = rm.create_secure_release(release_config)
        
        print(f"\n📊 發布流程結果:")
        print(f"   整體狀態: {pipeline_results['overall_status']}")
        print(f"   開始時間: {pipeline_results['started_at']}")
        
        if pipeline_results['overall_status'] == 'completed':
            print(f"   完成時間: {pipeline_results.get('completed_at', 'N/A')}")
            print(f"\n✅ PowerAutomation v0.5.0 發布成功！")
            
            # 顯示各步驟結果
            print(f"\n📋 發布步驟詳情:")
            for i, step in enumerate(pipeline_results['steps'], 1):
                status_icon = "✅" if step['status'] == 'success' else "❌"
                print(f"   {i}. {step['name']}: {status_icon} {step['status']}")
                if step.get('details'):
                    print(f"      詳情: {step['details']}")
            
            return True
            
        elif pipeline_results['overall_status'] == 'failed':
            print(f"   失敗時間: {pipeline_results.get('failed_at', 'N/A')}")
            print(f"   錯誤信息: {pipeline_results.get('error', 'Unknown error')}")
            print(f"\n❌ PowerAutomation v0.5.0 發布失敗！")
            
            # 顯示失敗步驟
            print(f"\n📋 發布步驟詳情:")
            for i, step in enumerate(pipeline_results['steps'], 1):
                status_icon = "✅" if step['status'] == 'success' else "❌"
                print(f"   {i}. {step['name']}: {status_icon} {step['status']}")
                if step.get('error'):
                    print(f"      錯誤: {step['error']}")
            
            return False
        
        else:
            print(f"\n⏳ 發布流程仍在進行中...")
            return False
            
    except Exception as e:
        print(f"\n❌ 發布過程中發生錯誤: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

