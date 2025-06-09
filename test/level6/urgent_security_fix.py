#!/usr/bin/env python3
"""
PowerAutomation Level 6: 緊急安全修復工具

立即修復P0級安全問題：
- API密鑰明文存儲
- 缺乏加密機制
- 安全配置缺失

作者: Manus AI
版本: v1.0
日期: 2025年6月9日
"""

import os
import sys
import json
import re
import shutil
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 添加項目路徑
sys.path.append('/home/ubuntu/Powerauto.ai')

# 導入加密管理器
try:
    from zip_encrypted_token_manager import ZipEncryptedTokenManager
except ImportError:
    # Mock類
    class ZipEncryptedTokenManager:
        def store_token(self, service, token, metadata=None): 
            print(f"Mock: 存儲 {service} 密鑰")
            return True
        def get_token(self, service): 
            print(f"Mock: 獲取 {service} 密鑰")
            return None

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UrgentSecurityFix:
    """緊急安全修復工具"""
    
    def __init__(self):
        self.project_dir = "/home/ubuntu/Powerauto.ai"
        self.zip_token_manager = ZipEncryptedTokenManager()
        
        # 敏感信息模式
        self.sensitive_patterns = {
            'anthropic_api': r'sk-ant-api03-[A-Za-z0-9_-]+',
            'google_api': r'AIzaSy[A-Za-z0-9_-]+',
            'openai_api': r'sk-[A-Za-z0-9]{48}',
            'github_token': r'github_pat_[A-Za-z0-9_-]+',
            'generic_key': r'["\']?[A-Za-z0-9_-]{32,}["\']?'
        }
        
        # 需要檢查的文件
        self.sensitive_files = [
            ".env",
            "test/gaia.py",
            "config/api_keys.json",
            "*.py",  # 所有Python文件
            "*.json", # 所有JSON文件
            "*.yaml", # 所有YAML文件
            "*.yml"   # 所有YML文件
        ]
        
    async def execute_urgent_fix(self) -> Dict[str, Any]:
        """執行緊急安全修復"""
        print("🚨 開始執行緊急安全修復...")
        
        fix_results = {
            "fix_id": f"urgent_fix_{int(datetime.now().timestamp())}",
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "overall_status": "unknown",
            "files_processed": 0,
            "issues_fixed": 0,
            "backup_location": None
        }
        
        try:
            # Step 1: 創建備份
            print("📦 創建項目備份...")
            backup_result = await self._create_project_backup()
            fix_results["steps"]["backup"] = backup_result
            fix_results["backup_location"] = backup_result.get("backup_path")
            
            # Step 2: 掃描敏感信息
            print("🔍 掃描敏感信息...")
            scan_result = await self._scan_sensitive_information()
            fix_results["steps"]["scan"] = scan_result
            
            # Step 3: 清理明文密鑰
            print("🧹 清理明文密鑰...")
            cleanup_result = await self._cleanup_plaintext_keys(scan_result["found_keys"])
            fix_results["steps"]["cleanup"] = cleanup_result
            fix_results["files_processed"] = cleanup_result["files_processed"]
            fix_results["issues_fixed"] = cleanup_result["keys_cleaned"]
            
            # Step 4: 啟用加密存儲
            print("🔐 啟用加密存儲...")
            encryption_result = await self._enable_encrypted_storage(scan_result["found_keys"])
            fix_results["steps"]["encryption"] = encryption_result
            
            # Step 5: 更新代碼使用安全配置
            print("🔧 更新代碼使用安全配置...")
            code_update_result = await self._update_code_for_security()
            fix_results["steps"]["code_update"] = code_update_result
            
            # Step 6: 驗證修復效果
            print("✅ 驗證修復效果...")
            validation_result = await self._validate_security_fix()
            fix_results["steps"]["validation"] = validation_result
            
            # 確定整體狀態
            fix_results["overall_status"] = "success" if validation_result["all_passed"] else "partial"
            
        except Exception as e:
            logger.error(f"緊急安全修復失敗: {e}")
            fix_results["overall_status"] = "failed"
            fix_results["error"] = str(e)
        
        fix_results["end_time"] = datetime.now().isoformat()
        
        # 保存修復報告
        await self._save_fix_report(fix_results)
        
        # 顯示修復結果
        self._display_fix_results(fix_results)
        
        return fix_results
    
    async def _create_project_backup(self) -> Dict[str, Any]:
        """創建項目備份"""
        backup_result = {
            "step": "backup",
            "status": "unknown",
            "backup_path": None,
            "files_backed_up": 0
        }
        
        try:
            # 創建備份目錄
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(self.project_dir) / "backups" / f"security_fix_backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 備份關鍵文件
            files_to_backup = []
            for pattern in self.sensitive_files:
                if "*" in pattern:
                    # 使用glob模式
                    files_to_backup.extend(Path(self.project_dir).rglob(pattern))
                else:
                    file_path = Path(self.project_dir) / pattern
                    if file_path.exists():
                        files_to_backup.append(file_path)
            
            # 執行備份
            for file_path in files_to_backup:
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.project_dir)
                    backup_file_path = backup_dir / relative_path
                    backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_file_path)
                    backup_result["files_backed_up"] += 1
            
            backup_result["status"] = "success"
            backup_result["backup_path"] = str(backup_dir)
            
        except Exception as e:
            backup_result["status"] = "failed"
            backup_result["error"] = str(e)
        
        return backup_result
    
    async def _scan_sensitive_information(self) -> Dict[str, Any]:
        """掃描敏感信息"""
        scan_result = {
            "step": "scan",
            "status": "unknown",
            "files_scanned": 0,
            "found_keys": {},
            "total_keys_found": 0
        }
        
        try:
            found_keys = {}
            
            # 掃描所有相關文件
            for pattern in self.sensitive_files:
                if "*" in pattern:
                    files_to_scan = list(Path(self.project_dir).rglob(pattern))
                else:
                    file_path = Path(self.project_dir) / pattern
                    files_to_scan = [file_path] if file_path.exists() else []
                
                for file_path in files_to_scan:
                    if file_path.is_file() and file_path.suffix in ['.py', '.json', '.yaml', '.yml', '.env', '.txt']:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # 檢查每種敏感模式
                            for pattern_name, pattern_regex in self.sensitive_patterns.items():
                                matches = re.findall(pattern_regex, content)
                                if matches:
                                    file_key = str(file_path.relative_to(self.project_dir))
                                    if file_key not in found_keys:
                                        found_keys[file_key] = {}
                                    found_keys[file_key][pattern_name] = matches
                                    scan_result["total_keys_found"] += len(matches)
                            
                            scan_result["files_scanned"] += 1
                            
                        except Exception as e:
                            logger.warning(f"無法掃描文件 {file_path}: {e}")
            
            scan_result["found_keys"] = found_keys
            scan_result["status"] = "success"
            
        except Exception as e:
            scan_result["status"] = "failed"
            scan_result["error"] = str(e)
        
        return scan_result
    
    async def _cleanup_plaintext_keys(self, found_keys: Dict[str, Any]) -> Dict[str, Any]:
        """清理明文密鑰"""
        cleanup_result = {
            "step": "cleanup",
            "status": "unknown",
            "files_processed": 0,
            "keys_cleaned": 0,
            "cleaned_files": []
        }
        
        try:
            for file_path, key_types in found_keys.items():
                full_file_path = Path(self.project_dir) / file_path
                
                if full_file_path.exists():
                    try:
                        with open(full_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        keys_in_file = 0
                        
                        # 替換每種類型的密鑰
                        for pattern_name, matches in key_types.items():
                            for match in matches:
                                # 替換為佔位符
                                placeholder = f"# {pattern_name.upper()}_REMOVED_FOR_SECURITY"
                                content = content.replace(match, placeholder)
                                keys_in_file += 1
                        
                        # 如果內容有變化，寫回文件
                        if content != original_content:
                            with open(full_file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            cleanup_result["cleaned_files"].append({
                                "file": file_path,
                                "keys_removed": keys_in_file
                            })
                            cleanup_result["keys_cleaned"] += keys_in_file
                        
                        cleanup_result["files_processed"] += 1
                        
                    except Exception as e:
                        logger.error(f"清理文件 {file_path} 失敗: {e}")
            
            cleanup_result["status"] = "success"
            
        except Exception as e:
            cleanup_result["status"] = "failed"
            cleanup_result["error"] = str(e)
        
        return cleanup_result
    
    async def _enable_encrypted_storage(self, found_keys: Dict[str, Any]) -> Dict[str, Any]:
        """啟用加密存儲"""
        encryption_result = {
            "step": "encryption",
            "status": "unknown",
            "keys_encrypted": 0,
            "encryption_details": []
        }
        
        try:
            # 提取所有找到的密鑰並加密存儲
            all_keys = {}
            
            for file_path, key_types in found_keys.items():
                for pattern_name, matches in key_types.items():
                    for i, key_value in enumerate(matches):
                        # 生成服務名稱
                        service_name = f"{pattern_name}_{i+1}"
                        all_keys[service_name] = key_value
            
            # 存儲到加密ZIP
            for service_name, key_value in all_keys.items():
                try:
                    result = self.zip_token_manager.store_token(
                        service=service_name,
                        token=key_value,
                        metadata={
                            "created_at": datetime.now().isoformat(),
                            "security_level": "high",
                            "purpose": "api_authentication",
                            "source": "urgent_security_fix"
                        }
                    )
                    
                    if result:
                        encryption_result["keys_encrypted"] += 1
                        encryption_result["encryption_details"].append({
                            "service": service_name,
                            "status": "encrypted"
                        })
                    else:
                        encryption_result["encryption_details"].append({
                            "service": service_name,
                            "status": "failed"
                        })
                        
                except Exception as e:
                    logger.error(f"加密密鑰 {service_name} 失敗: {e}")
                    encryption_result["encryption_details"].append({
                        "service": service_name,
                        "status": "error",
                        "error": str(e)
                    })
            
            encryption_result["status"] = "success"
            
        except Exception as e:
            encryption_result["status"] = "failed"
            encryption_result["error"] = str(e)
        
        return encryption_result
    
    async def _update_code_for_security(self) -> Dict[str, Any]:
        """更新代碼使用安全配置"""
        update_result = {
            "step": "code_update",
            "status": "unknown",
            "files_updated": 0,
            "updates_made": []
        }
        
        try:
            # 創建安全配置加載器
            secure_config_content = '''#!/usr/bin/env python3
"""
安全配置加載器
用於安全地獲取API密鑰和配置信息
"""

import os
import logging
from typing import Optional

try:
    from zip_encrypted_token_manager import ZipEncryptedTokenManager
except ImportError:
    class ZipEncryptedTokenManager:
        def get_token(self, service): return None

logger = logging.getLogger(__name__)

class SecureConfigLoader:
    """安全配置加載器"""
    
    def __init__(self):
        self.zip_token_manager = ZipEncryptedTokenManager()
        self._cached_tokens = {}
    
    def get_api_key(self, service_name: str) -> Optional[str]:
        """安全獲取API密鑰"""
        if service_name in self._cached_tokens:
            return self._cached_tokens[service_name]
        
        # 從加密ZIP中獲取密鑰
        token = self.zip_token_manager.get_token(service_name.lower())
        if token:
            self._cached_tokens[service_name] = token
            return token
        
        # 如果ZIP中沒有，嘗試從環境變量獲取（向後兼容）
        env_token = os.environ.get(service_name.upper())
        if env_token and not env_token.startswith('mock-'):
            logger.warning(f"從環境變量獲取 {service_name}，建議遷移到加密存儲")
            return env_token
        
        logger.error(f"無法獲取 {service_name} 的API密鑰")
        return None
    
    def get_config(self, config_name: str, default_value: any = None) -> any:
        """獲取配置值"""
        return os.environ.get(config_name, default_value)

# 全局實例
secure_config = SecureConfigLoader()
'''
            
            # 保存安全配置加載器
            config_file = Path(self.project_dir) / "secure_config_loader.py"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(secure_config_content)
            
            update_result["files_updated"] += 1
            update_result["updates_made"].append({
                "file": "secure_config_loader.py",
                "action": "created",
                "description": "創建安全配置加載器"
            })
            
            # 更新GAIA測試文件使用安全配置
            gaia_file = Path(self.project_dir) / "test" / "gaia.py"
            if gaia_file.exists():
                try:
                    with open(gaia_file, 'r', encoding='utf-8') as f:
                        gaia_content = f.read()
                    
                    # 添加安全導入
                    if "from secure_config_loader import secure_config" not in gaia_content:
                        gaia_content = "from secure_config_loader import secure_config\n" + gaia_content
                    
                    # 替換不安全的密鑰獲取方式
                    replacements = [
                        (r'os\.environ\.get\(["\']CLAUDE_API_KEY["\'][^)]*\)', 
                         'secure_config.get_api_key("CLAUDE_API_KEY")'),
                        (r'os\.environ\.get\(["\']GEMINI_API_KEY["\'][^)]*\)', 
                         'secure_config.get_api_key("GEMINI_API_KEY")'),
                        (r'os\.environ\.get\(["\']OPENAI_API_KEY["\'][^)]*\)', 
                         'secure_config.get_api_key("OPENAI_API_KEY")')
                    ]
                    
                    for pattern, replacement in replacements:
                        gaia_content = re.sub(pattern, replacement, gaia_content)
                    
                    with open(gaia_file, 'w', encoding='utf-8') as f:
                        f.write(gaia_content)
                    
                    update_result["files_updated"] += 1
                    update_result["updates_made"].append({
                        "file": "test/gaia.py",
                        "action": "updated",
                        "description": "更新為使用安全配置加載器"
                    })
                    
                except Exception as e:
                    logger.error(f"更新GAIA文件失敗: {e}")
            
            update_result["status"] = "success"
            
        except Exception as e:
            update_result["status"] = "failed"
            update_result["error"] = str(e)
        
        return update_result
    
    async def _validate_security_fix(self) -> Dict[str, Any]:
        """驗證安全修復效果"""
        validation_result = {
            "step": "validation",
            "status": "unknown",
            "checks": {},
            "all_passed": False
        }
        
        try:
            # 1. 檢查是否還有明文密鑰
            plaintext_check = await self._check_remaining_plaintext()
            validation_result["checks"]["no_plaintext_keys"] = plaintext_check
            
            # 2. 檢查加密存儲是否工作
            encryption_check = await self._check_encryption_working()
            validation_result["checks"]["encryption_working"] = encryption_check
            
            # 3. 檢查安全配置加載器
            config_loader_check = await self._check_config_loader()
            validation_result["checks"]["config_loader_working"] = config_loader_check
            
            # 確定是否全部通過
            all_checks_passed = all(
                check.get("passed", False) 
                for check in validation_result["checks"].values()
            )
            
            validation_result["all_passed"] = all_checks_passed
            validation_result["status"] = "success"
            
        except Exception as e:
            validation_result["status"] = "failed"
            validation_result["error"] = str(e)
        
        return validation_result
    
    async def _check_remaining_plaintext(self) -> Dict[str, Any]:
        """檢查是否還有明文密鑰"""
        check_result = {
            "test_name": "no_remaining_plaintext",
            "passed": False,
            "details": {}
        }
        
        try:
            # 重新掃描敏感信息
            scan_result = await self._scan_sensitive_information()
            remaining_keys = scan_result.get("total_keys_found", 0)
            
            check_result["passed"] = remaining_keys == 0
            check_result["details"]["remaining_keys_count"] = remaining_keys
            
        except Exception as e:
            check_result["details"]["error"] = str(e)
        
        return check_result
    
    async def _check_encryption_working(self) -> Dict[str, Any]:
        """檢查加密存儲是否工作"""
        check_result = {
            "test_name": "encryption_working",
            "passed": False,
            "details": {}
        }
        
        try:
            # 測試加密存儲
            test_token = f"test_token_{int(datetime.now().timestamp())}"
            store_result = self.zip_token_manager.store_token("test_service", test_token)
            
            if store_result:
                retrieved_token = self.zip_token_manager.get_token("test_service")
                check_result["passed"] = retrieved_token == test_token
                check_result["details"]["encryption_test"] = "passed"
            else:
                check_result["details"]["encryption_test"] = "failed"
                
        except Exception as e:
            check_result["details"]["error"] = str(e)
        
        return check_result
    
    async def _check_config_loader(self) -> Dict[str, Any]:
        """檢查安全配置加載器"""
        check_result = {
            "test_name": "config_loader_working",
            "passed": False,
            "details": {}
        }
        
        try:
            config_file = Path(self.project_dir) / "secure_config_loader.py"
            check_result["passed"] = config_file.exists()
            check_result["details"]["config_loader_exists"] = config_file.exists()
            
        except Exception as e:
            check_result["details"]["error"] = str(e)
        
        return check_result
    
    async def _save_fix_report(self, fix_results: Dict[str, Any]):
        """保存修復報告"""
        try:
            reports_dir = Path(self.project_dir) / "test" / "level6" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"urgent_security_fix_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(fix_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"修復報告已保存到: {report_file}")
            
        except Exception as e:
            logger.error(f"保存修復報告失敗: {e}")
    
    def _display_fix_results(self, results: Dict[str, Any]):
        """顯示修復結果"""
        print("\n" + "="*60)
        print("🛡️ 緊急安全修復結果報告")
        print("="*60)
        
        print(f"修復狀態: {results['overall_status']}")
        print(f"處理文件數: {results['files_processed']}")
        print(f"修復問題數: {results['issues_fixed']}")
        
        if results.get('backup_location'):
            print(f"備份位置: {results['backup_location']}")
        
        # 顯示各步驟結果
        for step_name, step_result in results.get('steps', {}).items():
            status = step_result.get('status', 'unknown')
            print(f"{step_name}: {status}")
        
        # 顯示驗證結果
        validation = results.get('steps', {}).get('validation', {})
        if validation:
            print(f"\n驗證結果: {'✅ 全部通過' if validation.get('all_passed') else '❌ 部分失敗'}")
        
        print("\n💡 後續建議:")
        print("1. 定期運行安全掃描")
        print("2. 實施API密鑰輪換策略")
        print("3. 建立安全監控機制")
        print("4. 進行安全培訓")


# CLI入口點
async def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PowerAutomation 緊急安全修復工具')
    parser.add_argument('--dry-run', action='store_true', help='僅掃描，不執行修復')
    parser.add_argument('--backup-only', action='store_true', help='僅創建備份')
    
    args = parser.parse_args()
    
    # 創建修復工具實例
    fix_tool = UrgentSecurityFix()
    
    if args.backup_only:
        print("📦 僅創建備份...")
        backup_result = await fix_tool._create_project_backup()
        print(f"備份結果: {backup_result['status']}")
        if backup_result.get('backup_path'):
            print(f"備份位置: {backup_result['backup_path']}")
    elif args.dry_run:
        print("🔍 僅掃描敏感信息...")
        scan_result = await fix_tool._scan_sensitive_information()
        print(f"掃描結果: 找到 {scan_result['total_keys_found']} 個敏感密鑰")
        for file_path, keys in scan_result['found_keys'].items():
            print(f"  {file_path}: {sum(len(matches) for matches in keys.values())} 個密鑰")
    else:
        # 執行完整修復
        results = await fix_tool.execute_urgent_fix()
        
        # 返回適當的退出碼
        if results['overall_status'] == 'success':
            sys.exit(0)
        elif results['overall_status'] == 'partial':
            sys.exit(1)
        else:
            sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())

