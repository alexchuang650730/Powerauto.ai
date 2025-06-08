"""
Enhanced Release Manager with ZIP Encryption Integration
集成ZIP加密機制的增強版Release Manager
"""

import os
import json
import logging
import subprocess
import tempfile
import shutil
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# 導入ZIP加密管理器
try:
    from zip_encrypted_token_manager import ZipEncryptedTokenManager, SecureGitAuthManager
except ImportError:
    # 如果導入失敗，創建Mock類
    class ZipEncryptedTokenManager:
        def get_token(self, service): return None
        def store_token(self, service, token, metadata=None): return True
    
    class SecureGitAuthManager:
        def auto_retry_git_push(self, repo_url=None): return False

logger = logging.getLogger(__name__)

class EnhancedReleaseManager:
    """集成ZIP加密的增強版Release Manager"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.releases = []
        self.current_release = None
        self.release_history = []
        
        # 初始化ZIP加密管理器
        self.zip_token_manager = ZipEncryptedTokenManager()
        self.secure_git_auth = SecureGitAuthManager()
        
        # 敏感信息模式
        self.sensitive_patterns = [
            r'sk-ant-api03-[A-Za-z0-9_-]+',  # Anthropic API Key
            r'github_pat_[A-Za-z0-9_-]+',    # GitHub Token
            r'AIzaSy[A-Za-z0-9_-]+',         # Google API Key
            r'sk-[A-Za-z0-9]{48}',           # OpenAI API Key
        ]
        
        # 發布配置
        self.release_config = {
            "auto_cleanup_sensitive": True,
            "use_zip_auth": True,
            "backup_before_push": True,
            "verify_after_push": True,
            "create_github_release": True
        }
        
        logger.info(f"Enhanced ReleaseManager初始化完成，項目目錄: {project_dir}")
    
    def create_secure_release(self, version: str, release_notes: str = "", 
                            release_type: str = "minor", 
                            auto_upload: bool = True) -> Dict[str, Any]:
        """創建安全發布（集成ZIP加密）"""
        
        release = {
            'id': len(self.releases) + 1,
            'version': version,
            'release_type': release_type,
            'release_notes': release_notes,
            'stage': 'planning',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'draft',
            'security_status': 'pending',
            'artifacts': [],
            'tests': [],
            'approvals': [],
            'sensitive_files_cleaned': [],
            'zip_auth_configured': False,
            'github_push_status': 'pending',
            'deployment_config': self._create_secure_deployment_config(),
            'security_checklist': self._create_security_checklist()
        }
        
        self.releases.append(release)
        self.current_release = release
        
        # 自動執行安全檢查
        if auto_upload:
            self._execute_secure_release_pipeline(release)
        
        self._log_release_event(release['id'], 'created', 
                               f"安全發布 {version} 已創建")
        
        return release
    
    def _execute_secure_release_pipeline(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """執行安全發布流水線"""
        pipeline_results = {
            'steps': [],
            'overall_status': 'running',
            'started_at': datetime.now().isoformat()
        }
        
        try:
            # 步驟1: 安全檢查和敏感信息清理
            step1 = self._cleanup_sensitive_information(release)
            pipeline_results['steps'].append(step1)
            
            # 步驟2: 配置ZIP加密認證
            step2 = self._configure_zip_authentication(release)
            pipeline_results['steps'].append(step2)
            
            # 步驟3: 執行安全Git推送
            step3 = self._execute_secure_git_push(release)
            pipeline_results['steps'].append(step3)
            
            # 步驟4: 創建GitHub Release
            step4 = self._create_github_release(release)
            pipeline_results['steps'].append(step4)
            
            # 步驟5: 驗證發布
            step5 = self._verify_release_integrity(release)
            pipeline_results['steps'].append(step5)
            
            pipeline_results['overall_status'] = 'completed'
            pipeline_results['completed_at'] = datetime.now().isoformat()
            
            release['status'] = 'released'
            release['security_status'] = 'verified'
            
        except Exception as e:
            pipeline_results['overall_status'] = 'failed'
            pipeline_results['error'] = str(e)
            pipeline_results['failed_at'] = datetime.now().isoformat()
            
            release['status'] = 'failed'
            release['security_status'] = 'compromised'
            
            logger.error(f"安全發布流水線失敗: {e}")
        
        release['pipeline_results'] = pipeline_results
        release['updated_at'] = datetime.now().isoformat()
        
        return pipeline_results
    
    def _cleanup_sensitive_information(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """清理敏感信息"""
        step_result = {
            'step': 'cleanup_sensitive_info',
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'files_processed': [],
            'sensitive_items_found': 0,
            'sensitive_items_cleaned': 0
        }
        
        try:
            sensitive_files = []
            
            # 掃描項目文件
            for file_path in self.project_dir.rglob('*'):
                if file_path.is_file() and self._should_scan_file(file_path):
                    cleaned_count = self._clean_file_sensitive_content(file_path)
                    if cleaned_count > 0:
                        sensitive_files.append({
                            'file': str(file_path.relative_to(self.project_dir)),
                            'items_cleaned': cleaned_count
                        })
                        step_result['sensitive_items_cleaned'] += cleaned_count
            
            step_result['files_processed'] = sensitive_files
            step_result['status'] = 'completed'
            step_result['completed_at'] = datetime.now().isoformat()
            
            release['sensitive_files_cleaned'] = sensitive_files
            
            logger.info(f"敏感信息清理完成: {step_result['sensitive_items_cleaned']} 項")
            
        except Exception as e:
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
            step_result['failed_at'] = datetime.now().isoformat()
            
        return step_result
    
    def _configure_zip_authentication(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """配置ZIP加密認證"""
        step_result = {
            'step': 'configure_zip_auth',
            'status': 'running',
            'started_at': datetime.now().isoformat()
        }
        
        try:
            # 檢查ZIP中是否有GitHub token
            github_token = self.zip_token_manager.get_token("github")
            
            if github_token:
                step_result['auth_status'] = 'token_found'
                step_result['token_preview'] = f"{github_token[:8]}...{github_token[-8:]}"
                release['zip_auth_configured'] = True
            else:
                step_result['auth_status'] = 'token_missing'
                step_result['warning'] = 'GitHub token not found in ZIP'
                release['zip_auth_configured'] = False
            
            step_result['status'] = 'completed'
            step_result['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
            step_result['failed_at'] = datetime.now().isoformat()
            
        return step_result
    
    def _execute_secure_git_push(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """執行安全Git推送"""
        step_result = {
            'step': 'secure_git_push',
            'status': 'running',
            'started_at': datetime.now().isoformat()
        }
        
        try:
            # 添加所有文件到Git
            subprocess.run(['git', 'add', '.'], cwd=self.project_dir, check=True)
            
            # 創建提交
            commit_message = f"🚀 {release['version']} - Secure Release\n\n{release['release_notes']}"
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd=self.project_dir, check=True)
            
            # 使用ZIP加密認證推送
            push_success = self.secure_git_auth.auto_retry_git_push()
            
            if push_success:
                step_result['status'] = 'completed'
                step_result['push_status'] = 'success'
                release['github_push_status'] = 'success'
            else:
                step_result['status'] = 'failed'
                step_result['push_status'] = 'failed'
                release['github_push_status'] = 'failed'
            
            step_result['completed_at'] = datetime.now().isoformat()
            
        except subprocess.CalledProcessError as e:
            step_result['status'] = 'failed'
            step_result['error'] = f"Git操作失敗: {e}"
            step_result['failed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
            step_result['failed_at'] = datetime.now().isoformat()
            
        return step_result
    
    def _create_github_release(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """創建GitHub Release"""
        step_result = {
            'step': 'create_github_release',
            'status': 'running',
            'started_at': datetime.now().isoformat()
        }
        
        try:
            # 創建Git標籤
            subprocess.run(['git', 'tag', '-a', release['version'], 
                          '-m', f"Release {release['version']}"], 
                         cwd=self.project_dir, check=True)
            
            # 推送標籤
            push_success = self.secure_git_auth.auto_retry_git_push()
            
            if push_success:
                step_result['status'] = 'completed'
                step_result['tag_created'] = release['version']
                step_result['release_url'] = f"https://github.com/alexchuang650730/Powerauto.ai/releases/tag/{release['version']}"
            else:
                step_result['status'] = 'failed'
                step_result['error'] = 'Failed to push tags'
            
            step_result['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
            step_result['failed_at'] = datetime.now().isoformat()
            
        return step_result
    
    def _verify_release_integrity(self, release: Dict[str, Any]) -> Dict[str, Any]:
        """驗證發布完整性"""
        step_result = {
            'step': 'verify_integrity',
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'checks': []
        }
        
        try:
            # 檢查1: Git狀態
            git_status = subprocess.run(['git', 'status', '--porcelain'], 
                                      cwd=self.project_dir, 
                                      capture_output=True, text=True)
            
            step_result['checks'].append({
                'name': 'git_status',
                'status': 'clean' if not git_status.stdout.strip() else 'dirty',
                'details': git_status.stdout.strip()
            })
            
            # 檢查2: 敏感信息掃描
            sensitive_found = self._scan_for_remaining_sensitive_info()
            step_result['checks'].append({
                'name': 'sensitive_scan',
                'status': 'clean' if not sensitive_found else 'found_sensitive',
                'details': f"Found {len(sensitive_found)} sensitive items" if sensitive_found else "No sensitive information found"
            })
            
            # 檢查3: ZIP認證狀態
            step_result['checks'].append({
                'name': 'zip_auth',
                'status': 'configured' if release['zip_auth_configured'] else 'not_configured',
                'details': 'ZIP authentication ready' if release['zip_auth_configured'] else 'ZIP authentication not configured'
            })
            
            # 總體狀態
            all_checks_passed = all(check['status'] in ['clean', 'configured'] for check in step_result['checks'])
            step_result['status'] = 'completed' if all_checks_passed else 'warning'
            step_result['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
            step_result['failed_at'] = datetime.now().isoformat()
            
        return step_result
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """判斷是否應該掃描文件"""
        # 跳過的目錄和文件
        skip_patterns = [
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.env', '*.pyc', '*.log', '*.zip'
        ]
        
        file_str = str(file_path)
        return not any(pattern in file_str for pattern in skip_patterns)
    
    def _clean_file_sensitive_content(self, file_path: Path) -> int:
        """清理文件中的敏感內容"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            cleaned_count = 0
            
            # 替換敏感信息
            for pattern in self.sensitive_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if 'github_pat_' in match:
                        replacement = 'your_github_token_here'
                    elif 'sk-ant-api03-' in match:
                        replacement = 'your_claude_api_key_here'
                    elif 'AIzaSy' in match:
                        replacement = 'your_gemini_api_key_here'
                    else:
                        replacement = 'your_api_key_here'
                    
                    content = content.replace(match, replacement)
                    cleaned_count += 1
            
            # 如果有修改，寫回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return cleaned_count
            
        except Exception as e:
            logger.warning(f"清理文件失敗 {file_path}: {e}")
            return 0
    
    def _scan_for_remaining_sensitive_info(self) -> List[Dict[str, Any]]:
        """掃描剩餘的敏感信息"""
        sensitive_items = []
        
        for file_path in self.project_dir.rglob('*'):
            if file_path.is_file() and self._should_scan_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in self.sensitive_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            sensitive_items.append({
                                'file': str(file_path.relative_to(self.project_dir)),
                                'pattern': pattern,
                                'preview': f"{match[:8]}...{match[-8:]}"
                            })
                except:
                    continue
        
        return sensitive_items
    
    def _create_secure_deployment_config(self) -> Dict[str, Any]:
        """創建安全部署配置"""
        return {
            'strategy': 'secure_blue_green',
            'security_checks': [
                'sensitive_info_scan',
                'zip_auth_verification',
                'github_secret_protection',
                'api_key_encryption'
            ],
            'health_checks': ['api_health', 'database_connection', 'service_status'],
            'timeout': 300,
            'rollback_threshold': 0.05,
            'monitoring_duration': 1800,
            'zip_encryption': True,
            'auto_cleanup_sensitive': True
        }
    
    def _create_security_checklist(self) -> List[Dict[str, Any]]:
        """創建安全檢查清單"""
        return [
            {
                'item': '敏感信息清理',
                'description': '掃描並清理所有敏感API密鑰和Token',
                'status': 'pending',
                'critical': True
            },
            {
                'item': 'ZIP加密認證',
                'description': '配置ZIP加密的GitHub認證',
                'status': 'pending',
                'critical': True
            },
            {
                'item': 'GitHub Secret Protection',
                'description': '確保不觸發GitHub Secret Scanning',
                'status': 'pending',
                'critical': True
            },
            {
                'item': '發布完整性驗證',
                'description': '驗證發布內容的完整性和安全性',
                'status': 'pending',
                'critical': False
            }
        ]
    
    def _log_release_event(self, release_id: int, event_type: str, message: str):
        """記錄發布事件"""
        event = {
            'release_id': release_id,
            'event_type': event_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.release_history.append(event)
    
    def get_release_status(self, release_id: int = None) -> Dict[str, Any]:
        """獲取發布狀態"""
        if release_id:
            release = next((r for r in self.releases if r['id'] == release_id), None)
            if not release:
                return {'error': f'Release {release_id} not found'}
            return release
        else:
            return {
                'current_release': self.current_release,
                'total_releases': len(self.releases),
                'recent_releases': self.releases[-5:] if self.releases else []
            }
    
    def emergency_rollback(self, release_id: int, reason: str = "Emergency rollback") -> Dict[str, Any]:
        """緊急回滾"""
        release = next((r for r in self.releases if r['id'] == release_id), None)
        if not release:
            return {'error': f'Release {release_id} not found'}
        
        rollback_result = {
            'rollback_id': f"emergency_{release_id}_{int(datetime.now().timestamp())}",
            'release_id': release_id,
            'reason': reason,
            'started_at': datetime.now().isoformat(),
            'status': 'executing'
        }
        
        try:
            # 執行緊急回滾步驟
            subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], 
                         cwd=self.project_dir, check=True)
            
            # 強制推送回滾
            push_success = self.secure_git_auth.auto_retry_git_push()
            
            if push_success:
                rollback_result['status'] = 'completed'
                release['status'] = 'rolled_back'
            else:
                rollback_result['status'] = 'failed'
                rollback_result['error'] = 'Failed to push rollback'
            
            rollback_result['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            rollback_result['status'] = 'failed'
            rollback_result['error'] = str(e)
            rollback_result['failed_at'] = datetime.now().isoformat()
        
        self._log_release_event(release_id, 'emergency_rollback', reason)
        return rollback_result


