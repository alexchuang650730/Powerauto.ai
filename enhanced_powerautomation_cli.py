#!/usr/bin/env python3
"""
PowerAutomation Enhanced CLI with Secure Release Management
集成安全發布管理的增強版CLI系統
"""

import os
import sys
import json
import argparse
import asyncio
import logging
import readline
import cmd
import shlex
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import signal
import threading
import time

# 添加項目路徑
sys.path.append('/home/ubuntu/Powerauto.ai')

# 導入增強版Release Manager
try:
    from mcptool.core.development_tools.enhanced_release_manager import EnhancedReleaseManager
except ImportError as e:
    logging.warning(f"導入Enhanced Release Manager失敗: {e}")
    EnhancedReleaseManager = None

# 導入ZIP加密管理器
try:
    from zip_encrypted_token_manager import ZipEncryptedTokenManager, SecureGitAuthManager
except ImportError as e:
    logging.warning(f"導入ZIP加密管理器失敗: {e}")
    ZipEncryptedTokenManager = None
    SecureGitAuthManager = None

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced_powerautomation_cli")

class EnhancedPowerAutomationCLI(cmd.Cmd):
    """集成安全發布管理的增強版PowerAutomation CLI"""
    
    intro = '''
🚀 PowerAutomation Enhanced CLI v0.4
=====================================
✨ 安全發布 | ZIP加密 | 智能部署 | 敏感信息保護
輸入 'help' 查看可用命令
輸入 'release --help' 查看發布管理命令
輸入 'quit' 或 'exit' 退出系統
'''
    prompt = '(PowerAutomation-Enhanced) > '
    
    def __init__(self):
        super().__init__()
        
        # 初始化增強版Release Manager
        self.release_manager = None
        if EnhancedReleaseManager:
            try:
                self.release_manager = EnhancedReleaseManager('/home/ubuntu/Powerauto.ai')
                logger.info("Enhanced Release Manager初始化成功")
            except Exception as e:
                logger.error(f"Enhanced Release Manager初始化失敗: {e}")
        
        # 初始化ZIP加密管理器
        self.zip_token_manager = None
        self.secure_git_auth = None
        if ZipEncryptedTokenManager and SecureGitAuthManager:
            try:
                self.zip_token_manager = ZipEncryptedTokenManager()
                self.secure_git_auth = SecureGitAuthManager()
                logger.info("ZIP加密管理器初始化成功")
            except Exception as e:
                logger.error(f"ZIP加密管理器初始化失敗: {e}")
        
        # CLI狀態
        self.current_release = None
        self.batch_mode = False
        self.auto_confirm = False
        
        # 命令歷史
        self.command_history = []
        self.max_history = 100
        
        logger.info("Enhanced PowerAutomation CLI初始化完成")
    
    def do_release(self, args):
        """安全發布管理
        用法: 
          release create <version> [--notes "發布說明"] [--type minor|major|patch] [--auto-upload]
          release status [release_id]
          release list
          release rollback <release_id> [--reason "回滾原因"]
          release cleanup
        """
        try:
            if not self.release_manager:
                print("❌ Enhanced Release Manager未初始化")
                return
            
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定發布操作")
                print("可用操作: create, status, list, rollback, cleanup")
                return
            
            operation = args_list[0]
            
            if operation == "create":
                self._handle_release_create(args_list[1:])
            elif operation == "status":
                self._handle_release_status(args_list[1:])
            elif operation == "list":
                self._handle_release_list()
            elif operation == "rollback":
                self._handle_release_rollback(args_list[1:])
            elif operation == "cleanup":
                self._handle_release_cleanup()
            else:
                print(f"❌ 未知的發布操作: {operation}")
                
        except Exception as e:
            print(f"❌ 發布操作失敗: {str(e)}")
            logger.error(f"Release operation failed: {e}")
    
    def _handle_release_create(self, args: List[str]):
        """處理創建發布"""
        if not args:
            print("❌ 請指定版本號")
            print("用法: release create <version> [--notes \"發布說明\"] [--type minor|major|patch] [--auto-upload]")
            return
        
        version = args[0]
        release_notes = ""
        release_type = "minor"
        auto_upload = False
        
        # 解析參數
        i = 1
        while i < len(args):
            if args[i] == "--notes" and i + 1 < len(args):
                release_notes = args[i + 1]
                i += 2
            elif args[i] == "--type" and i + 1 < len(args):
                release_type = args[i + 1]
                i += 2
            elif args[i] == "--auto-upload":
                auto_upload = True
                i += 1
            else:
                i += 1
        
        print(f"🚀 創建安全發布: {version}")
        print(f"   類型: {release_type}")
        print(f"   說明: {release_notes or '無'}")
        print(f"   自動上傳: {'是' if auto_upload else '否'}")
        
        if not self.auto_confirm:
            confirm = input("\n確認創建發布? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 發布創建已取消")
                return
        
        try:
            # 創建安全發布
            release = self.release_manager.create_secure_release(
                version=version,
                release_notes=release_notes,
                release_type=release_type,
                auto_upload=auto_upload
            )
            
            self.current_release = release
            
            print(f"\n✅ 安全發布創建成功!")
            print(f"   發布ID: {release['id']}")
            print(f"   版本: {release['version']}")
            print(f"   狀態: {release['status']}")
            print(f"   安全狀態: {release['security_status']}")
            
            if auto_upload and 'pipeline_results' in release:
                self._display_pipeline_results(release['pipeline_results'])
            
        except Exception as e:
            print(f"❌ 創建發布失敗: {e}")
    
    def _handle_release_status(self, args: List[str]):
        """處理發布狀態查詢"""
        release_id = None
        if args:
            try:
                release_id = int(args[0])
            except ValueError:
                print("❌ 無效的發布ID")
                return
        
        try:
            status = self.release_manager.get_release_status(release_id)
            
            if 'error' in status:
                print(f"❌ {status['error']}")
                return
            
            if release_id:
                # 顯示特定發布的詳細狀態
                self._display_release_details(status)
            else:
                # 顯示總體狀態
                self._display_overall_status(status)
                
        except Exception as e:
            print(f"❌ 獲取發布狀態失敗: {e}")
    
    def _handle_release_list(self):
        """處理發布列表"""
        try:
            status = self.release_manager.get_release_status()
            releases = status.get('recent_releases', [])
            
            if not releases:
                print("📋 暫無發布記錄")
                return
            
            print("📋 最近的發布:")
            print("=" * 80)
            print(f"{'ID':<4} {'版本':<12} {'類型':<8} {'狀態':<12} {'安全狀態':<12} {'創建時間':<20}")
            print("-" * 80)
            
            for release in releases:
                created_at = datetime.fromisoformat(release['created_at']).strftime('%Y-%m-%d %H:%M')
                print(f"{release['id']:<4} {release['version']:<12} {release['release_type']:<8} "
                      f"{release['status']:<12} {release['security_status']:<12} {created_at:<20}")
            
        except Exception as e:
            print(f"❌ 獲取發布列表失敗: {e}")
    
    def _handle_release_rollback(self, args: List[str]):
        """處理發布回滾"""
        if not args:
            print("❌ 請指定要回滾的發布ID")
            print("用法: release rollback <release_id> [--reason \"回滾原因\"]")
            return
        
        try:
            release_id = int(args[0])
        except ValueError:
            print("❌ 無效的發布ID")
            return
        
        reason = "Manual rollback"
        
        # 解析回滾原因
        i = 1
        while i < len(args):
            if args[i] == "--reason" and i + 1 < len(args):
                reason = args[i + 1]
                i += 2
            else:
                i += 1
        
        print(f"⚠️  準備回滾發布 {release_id}")
        print(f"   原因: {reason}")
        
        if not self.auto_confirm:
            confirm = input("\n確認執行緊急回滾? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 回滾操作已取消")
                return
        
        try:
            result = self.release_manager.emergency_rollback(release_id, reason)
            
            if 'error' in result:
                print(f"❌ {result['error']}")
                return
            
            print(f"\n🔄 回滾執行結果:")
            print(f"   回滾ID: {result['rollback_id']}")
            print(f"   狀態: {result['status']}")
            
            if result['status'] == 'completed':
                print("✅ 緊急回滾成功完成")
            else:
                print(f"❌ 回滾失敗: {result.get('error', '未知錯誤')}")
                
        except Exception as e:
            print(f"❌ 執行回滾失敗: {e}")
    
    def _handle_release_cleanup(self):
        """處理發布清理"""
        print("🧹 執行發布環境清理...")
        
        try:
            # 清理臨時文件
            temp_files_cleaned = 0
            
            # 清理Git狀態
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd='/home/ubuntu/Powerauto.ai',
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                print("⚠️  發現未提交的更改:")
                print(result.stdout)
                
                if not self.auto_confirm:
                    confirm = input("是否重置到最後提交狀態? (y/N): ").strip().lower()
                    if confirm == 'y':
                        subprocess.run(['git', 'reset', '--hard'], 
                                     cwd='/home/ubuntu/Powerauto.ai', check=True)
                        print("✅ Git狀態已重置")
            else:
                print("✅ Git狀態乾淨")
            
            print(f"✅ 清理完成，清理了 {temp_files_cleaned} 個臨時文件")
            
        except Exception as e:
            print(f"❌ 清理失敗: {e}")
    
    def _display_pipeline_results(self, pipeline_results: Dict[str, Any]):
        """顯示流水線結果"""
        print(f"\n🔄 安全發布流水線結果:")
        print(f"   總體狀態: {pipeline_results['overall_status']}")
        
        if 'steps' in pipeline_results:
            print("\n   執行步驟:")
            for step in pipeline_results['steps']:
                status_icon = "✅" if step['status'] == 'completed' else "❌" if step['status'] == 'failed' else "🔄"
                print(f"   {status_icon} {step['step']}: {step['status']}")
                
                if step['status'] == 'failed' and 'error' in step:
                    print(f"      錯誤: {step['error']}")
    
    def _display_release_details(self, release: Dict[str, Any]):
        """顯示發布詳細信息"""
        print(f"\n📋 發布詳細信息:")
        print(f"   ID: {release['id']}")
        print(f"   版本: {release['version']}")
        print(f"   類型: {release['release_type']}")
        print(f"   狀態: {release['status']}")
        print(f"   安全狀態: {release['security_status']}")
        print(f"   創建時間: {release['created_at']}")
        print(f"   更新時間: {release['updated_at']}")
        
        if release.get('release_notes'):
            print(f"   發布說明: {release['release_notes']}")
        
        if release.get('sensitive_files_cleaned'):
            print(f"\n🔐 敏感信息清理:")
            for file_info in release['sensitive_files_cleaned']:
                print(f"   - {file_info['file']}: {file_info['items_cleaned']} 項")
        
        if 'pipeline_results' in release:
            self._display_pipeline_results(release['pipeline_results'])
    
    def _display_overall_status(self, status: Dict[str, Any]):
        """顯示總體狀態"""
        print(f"\n📊 發布管理總體狀態:")
        print(f"   總發布數: {status['total_releases']}")
        
        if status['current_release']:
            current = status['current_release']
            print(f"   當前發布: {current['version']} ({current['status']})")
        else:
            print("   當前發布: 無")
    
    def do_zip(self, args):
        """ZIP加密管理
        用法:
          zip store-token <service> <token>
          zip get-token <service>
          zip list-tokens
          zip test-auth
        """
        try:
            if not self.zip_token_manager:
                print("❌ ZIP加密管理器未初始化")
                return
            
            args_list = shlex.split(args) if args else []
            
            if not args_list:
                print("❌ 請指定ZIP操作")
                print("可用操作: store-token, get-token, list-tokens, test-auth")
                return
            
            operation = args_list[0]
            
            if operation == "store-token":
                if len(args_list) < 3:
                    print("❌ 用法: zip store-token <service> <token>")
                    return
                
                service = args_list[1]
                token = args_list[2]
                
                success = self.zip_token_manager.store_token(service, token)
                if success:
                    print(f"✅ Token已安全存儲: {service}")
                else:
                    print(f"❌ Token存儲失敗: {service}")
            
            elif operation == "get-token":
                if len(args_list) < 2:
                    print("❌ 用法: zip get-token <service>")
                    return
                
                service = args_list[1]
                token = self.zip_token_manager.get_token(service)
                
                if token:
                    print(f"✅ Token: {token[:8]}...{token[-8:]}")
                else:
                    print(f"❌ 未找到Token: {service}")
            
            elif operation == "list-tokens":
                tokens = self.zip_token_manager.list_stored_tokens()
                
                if not tokens:
                    print("📋 暫無存儲的Token")
                    return
                
                print("📋 已存儲的Token:")
                for service, info in tokens.items():
                    print(f"   {service}: {info['stored_at']} (hash: {info['hash_preview']})")
            
            elif operation == "test-auth":
                if not self.secure_git_auth:
                    print("❌ 安全Git認證管理器未初始化")
                    return
                
                print("🔍 測試ZIP加密認證...")
                success = self.secure_git_auth.auto_retry_git_push()
                
                if success:
                    print("✅ ZIP加密認證測試成功")
                else:
                    print("❌ ZIP加密認證測試失敗")
            
            else:
                print(f"❌ 未知的ZIP操作: {operation}")
                
        except Exception as e:
            print(f"❌ ZIP操作失敗: {str(e)}")
    
    def do_status(self, args):
        """顯示系統狀態"""
        print("\n🎯 PowerAutomation Enhanced CLI 系統狀態:")
        print("=" * 50)
        
        # Release Manager狀態
        if self.release_manager:
            print("✅ Enhanced Release Manager: 已初始化")
            try:
                status = self.release_manager.get_release_status()
                print(f"   總發布數: {status['total_releases']}")
                if status['current_release']:
                    print(f"   當前發布: {status['current_release']['version']}")
            except:
                print("   狀態: 獲取失敗")
        else:
            print("❌ Enhanced Release Manager: 未初始化")
        
        # ZIP加密管理器狀態
        if self.zip_token_manager:
            print("✅ ZIP加密管理器: 已初始化")
            try:
                tokens = self.zip_token_manager.list_stored_tokens()
                print(f"   存儲Token數: {len(tokens)}")
            except:
                print("   狀態: 獲取失敗")
        else:
            print("❌ ZIP加密管理器: 未初始化")
        
        # Git狀態
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd='/home/ubuntu/Powerauto.ai',
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                print("⚠️  Git狀態: 有未提交更改")
            else:
                print("✅ Git狀態: 乾淨")
        except:
            print("❌ Git狀態: 檢查失敗")
    
    def do_quit(self, args):
        """退出CLI"""
        print("\n👋 感謝使用PowerAutomation Enhanced CLI!")
        return True
    
    def do_exit(self, args):
        """退出CLI"""
        return self.do_quit(args)
    
    def do_EOF(self, args):
        """處理Ctrl+D"""
        print()
        return self.do_quit(args)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='PowerAutomation Enhanced CLI')
    parser.add_argument('--batch', action='store_true', help='批處理模式')
    parser.add_argument('--auto-confirm', action='store_true', help='自動確認操作')
    parser.add_argument('--command', help='執行單個命令後退出')
    
    args = parser.parse_args()
    
    cli = EnhancedPowerAutomationCLI()
    cli.batch_mode = args.batch
    cli.auto_confirm = args.auto_confirm
    
    if args.command:
        # 執行單個命令
        cli.onecmd(args.command)
    else:
        # 進入交互模式
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            print("\n\n👋 感謝使用PowerAutomation Enhanced CLI!")
        except Exception as e:
            logger.error(f"CLI運行錯誤: {e}")
            print(f"❌ CLI運行錯誤: {e}")

if __name__ == '__main__':
    main()

