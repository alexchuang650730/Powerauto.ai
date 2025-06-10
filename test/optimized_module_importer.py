#!/usr/bin/env python3
"""
優化模組導入機制
提供安全、可靠的模組導入和依賴管理

主要功能：
- 安全的模組導入
- 依賴關係管理
- 導入錯誤處理
- 模組緩存機制
- 動態模組發現
"""

import sys
import os
import importlib
import importlib.util
import inspect
import logging
from typing import Dict, Any, List, Optional, Union, Type, Callable
from pathlib import Path
from dataclasses import dataclass
from contextlib import contextmanager
import traceback
import warnings

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class ModuleInfo:
    """模組信息"""
    name: str
    module: Any
    path: str
    imported: bool
    error: Optional[str]
    dependencies: List[str]

@dataclass
class ImportResult:
    """導入結果"""
    success: bool
    module: Optional[Any]
    error: Optional[str]
    warnings: List[str]

class SafeModuleImporter:
    """安全模組導入器"""
    
    def __init__(self):
        self._module_cache: Dict[str, ModuleInfo] = {}
        self._import_errors: Dict[str, str] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
        
        # 配置警告過濾
        self._setup_warning_filters()
    
    def _setup_warning_filters(self):
        """設置警告過濾器"""
        # 忽略常見的無害警告
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
        warnings.filterwarnings("ignore", message=".*pkg_resources.*")
    
    @contextmanager
    def safe_import_context(self):
        """安全導入上下文管理器"""
        old_path = sys.path.copy()
        captured_warnings = []
        
        def warning_handler(message, category, filename, lineno, file=None, line=None):
            captured_warnings.append(f"{category.__name__}: {message}")
        
        old_showwarning = warnings.showwarning
        warnings.showwarning = warning_handler
        
        try:
            yield captured_warnings
        finally:
            sys.path = old_path
            warnings.showwarning = old_showwarning
    
    def safe_import(self, module_name: str, package: Optional[str] = None) -> ImportResult:
        """安全導入模組"""
        # 檢查緩存
        if module_name in self._module_cache:
            cached_info = self._module_cache[module_name]
            if cached_info.imported:
                return ImportResult(
                    success=True,
                    module=cached_info.module,
                    error=None,
                    warnings=[]
                )
            else:
                return ImportResult(
                    success=False,
                    module=None,
                    error=cached_info.error,
                    warnings=[]
                )
        
        with self.safe_import_context() as captured_warnings:
            try:
                # 嘗試導入模組
                if package:
                    module = importlib.import_module(module_name, package)
                else:
                    module = importlib.import_module(module_name)
                
                # 記錄成功導入
                module_info = ModuleInfo(
                    name=module_name,
                    module=module,
                    path=getattr(module, '__file__', ''),
                    imported=True,
                    error=None,
                    dependencies=self._extract_dependencies(module)
                )
                
                self._module_cache[module_name] = module_info
                
                return ImportResult(
                    success=True,
                    module=module,
                    error=None,
                    warnings=captured_warnings
                )
                
            except ImportError as e:
                error_msg = f"ImportError: {str(e)}"
                self._import_errors[module_name] = error_msg
                
                # 記錄失敗導入
                module_info = ModuleInfo(
                    name=module_name,
                    module=None,
                    path='',
                    imported=False,
                    error=error_msg,
                    dependencies=[]
                )
                
                self._module_cache[module_name] = module_info
                
                return ImportResult(
                    success=False,
                    module=None,
                    error=error_msg,
                    warnings=captured_warnings
                )
                
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self._import_errors[module_name] = error_msg
                
                module_info = ModuleInfo(
                    name=module_name,
                    module=None,
                    path='',
                    imported=False,
                    error=error_msg,
                    dependencies=[]
                )
                
                self._module_cache[module_name] = module_info
                
                return ImportResult(
                    success=False,
                    module=None,
                    error=error_msg,
                    warnings=captured_warnings
                )
    
    def _extract_dependencies(self, module: Any) -> List[str]:
        """提取模組依賴"""
        dependencies = []
        
        try:
            # 檢查模組的__all__屬性
            if hasattr(module, '__all__'):
                dependencies.extend(module.__all__)
            
            # 檢查導入語句（簡單分析）
            if hasattr(module, '__file__') and module.__file__:
                try:
                    with open(module.__file__, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 簡單的import語句提取
                        import re
                        imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
                        for imp in imports:
                            dep = imp[0] if imp[0] else imp[1]
                            if dep and not dep.startswith('.'):
                                dependencies.append(dep.split('.')[0])
                except:
                    pass
        except:
            pass
        
        return list(set(dependencies))
    
    def import_from_path(self, module_name: str, file_path: str) -> ImportResult:
        """從文件路徑導入模組"""
        with self.safe_import_context() as captured_warnings:
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None:
                    return ImportResult(
                        success=False,
                        module=None,
                        error=f"無法創建模組規範: {file_path}",
                        warnings=captured_warnings
                    )
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 記錄成功導入
                module_info = ModuleInfo(
                    name=module_name,
                    module=module,
                    path=file_path,
                    imported=True,
                    error=None,
                    dependencies=self._extract_dependencies(module)
                )
                
                self._module_cache[module_name] = module_info
                
                return ImportResult(
                    success=True,
                    module=module,
                    error=None,
                    warnings=captured_warnings
                )
                
            except Exception as e:
                error_msg = f"從路徑導入失敗 {file_path}: {str(e)}"
                
                return ImportResult(
                    success=False,
                    module=None,
                    error=error_msg,
                    warnings=captured_warnings
                )
    
    def discover_modules(self, directory: str, pattern: str = "*.py") -> List[str]:
        """發現目錄中的模組"""
        discovered_modules = []
        
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return discovered_modules
            
            for file_path in dir_path.glob(pattern):
                if file_path.name.startswith("__"):
                    continue
                
                module_name = file_path.stem
                discovered_modules.append(module_name)
                
        except Exception as e:
            logger.warning(f"發現模組時出錯 {directory}: {e}")
        
        return discovered_modules
    
    def batch_import(self, module_names: List[str], continue_on_error: bool = True) -> Dict[str, ImportResult]:
        """批量導入模組"""
        results = {}
        
        for module_name in module_names:
            result = self.safe_import(module_name)
            results[module_name] = result
            
            if not result.success and not continue_on_error:
                logger.error(f"批量導入在 {module_name} 處停止: {result.error}")
                break
        
        return results
    
    def get_module_info(self, module_name: str) -> Optional[ModuleInfo]:
        """獲取模組信息"""
        return self._module_cache.get(module_name)
    
    def get_import_errors(self) -> Dict[str, str]:
        """獲取導入錯誤"""
        return self._import_errors.copy()
    
    def get_imported_modules(self) -> List[str]:
        """獲取已導入的模組"""
        return [name for name, info in self._module_cache.items() if info.imported]
    
    def get_failed_modules(self) -> List[str]:
        """獲取導入失敗的模組"""
        return [name for name, info in self._module_cache.items() if not info.imported]
    
    def clear_cache(self):
        """清除緩存"""
        self._module_cache.clear()
        self._import_errors.clear()
        self._dependency_graph.clear()
    
    def reload_module(self, module_name: str) -> ImportResult:
        """重新載入模組"""
        # 從緩存中移除
        if module_name in self._module_cache:
            del self._module_cache[module_name]
        
        if module_name in self._import_errors:
            del self._import_errors[module_name]
        
        # 重新導入
        return self.safe_import(module_name)

class TestModuleImporter(SafeModuleImporter):
    """測試模組導入器"""
    
    def __init__(self):
        super().__init__()
        self.test_module_paths = [
            "test",
            "test/level1",
            "test/level2", 
            "test/level3"
        ]
    
    def import_test_modules(self) -> Dict[str, ImportResult]:
        """導入測試模組"""
        results = {}
        
        for test_path in self.test_module_paths:
            # 發現測試模組
            modules = self.discover_modules(test_path)
            
            for module_name in modules:
                # 構建完整模組路徑
                full_module_path = f"{test_path.replace('/', '.')}.{module_name}"
                
                # 嘗試導入
                result = self.safe_import(full_module_path)
                results[full_module_path] = result
                
                if result.success:
                    logger.info(f"成功導入測試模組: {full_module_path}")
                else:
                    logger.warning(f"導入測試模組失敗 {full_module_path}: {result.error}")
        
        return results
    
    def get_test_classes(self, module_name: str) -> List[Type]:
        """從模組中獲取測試類"""
        module_info = self.get_module_info(module_name)
        if not module_info or not module_info.imported:
            return []
        
        test_classes = []
        module = module_info.module
        
        for name in dir(module):
            obj = getattr(module, name)
            
            if (inspect.isclass(obj) and 
                (name.endswith('Test') or name.endswith('Tester') or 
                 name.endswith('Framework') or name.endswith('Validator'))):
                test_classes.append(obj)
        
        return test_classes
    
    def instantiate_test_class(self, test_class: Type) -> Optional[Any]:
        """實例化測試類"""
        try:
            # 檢查構造函數參數
            sig = inspect.signature(test_class.__init__)
            params = list(sig.parameters.keys())[1:]  # 排除self
            
            if not params:
                # 無參數構造函數
                return test_class()
            else:
                # 有參數構造函數，嘗試提供默認值
                kwargs = {}
                for param_name in params:
                    param = sig.parameters[param_name]
                    if param.default != inspect.Parameter.empty:
                        continue
                    elif param_name in ['name', 'test_name']:
                        kwargs[param_name] = test_class.__name__
                    elif param_name in ['description']:
                        kwargs[param_name] = f"測試類: {test_class.__name__}"
                
                return test_class(**kwargs)
                
        except Exception as e:
            logger.error(f"實例化測試類 {test_class.__name__} 失敗: {e}")
            return None

class DependencyManager:
    """依賴管理器"""
    
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
        self.resolved_order: List[str] = []
    
    def add_dependency(self, module: str, dependencies: List[str]):
        """添加模組依賴"""
        self.dependencies[module] = dependencies
    
    def resolve_dependencies(self) -> List[str]:
        """解析依賴順序"""
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(module: str):
            if module in temp_visited:
                raise ValueError(f"檢測到循環依賴: {module}")
            
            if module in visited:
                return
            
            temp_visited.add(module)
            
            for dep in self.dependencies.get(module, []):
                if dep in self.dependencies:
                    visit(dep)
            
            temp_visited.remove(module)
            visited.add(module)
            result.append(module)
        
        for module in self.dependencies:
            if module not in visited:
                visit(module)
        
        self.resolved_order = result
        return result

# 全局導入器實例
_global_importer = None

def get_safe_importer() -> SafeModuleImporter:
    """獲取全局安全導入器"""
    global _global_importer
    if _global_importer is None:
        _global_importer = SafeModuleImporter()
    return _global_importer

def safe_import_module(module_name: str, package: Optional[str] = None) -> ImportResult:
    """安全導入模組的便捷函數"""
    importer = get_safe_importer()
    return importer.safe_import(module_name, package)

def import_test_framework(framework_name: str) -> Optional[Any]:
    """導入測試框架的便捷函數"""
    test_importer = TestModuleImporter()
    
    # 嘗試不同的導入路徑
    possible_paths = [
        f"test.{framework_name}",
        f"test.level1.{framework_name}",
        f"test.level2.{framework_name}",
        f"test.level3.{framework_name}"
    ]
    
    for path in possible_paths:
        result = test_importer.safe_import(path)
        if result.success:
            # 嘗試獲取測試類
            test_classes = test_importer.get_test_classes(path)
            if test_classes:
                # 實例化第一個測試類
                return test_importer.instantiate_test_class(test_classes[0])
    
    return None

if __name__ == "__main__":
    # 測試安全導入器
    importer = SafeModuleImporter()
    
    # 測試基本導入
    result = importer.safe_import("json")
    print(f"導入json: {result.success}")
    
    # 測試失敗導入
    result = importer.safe_import("non_existent_module")
    print(f"導入不存在模組: {result.success}, 錯誤: {result.error}")
    
    # 測試模組發現
    test_importer = TestModuleImporter()
    test_results = test_importer.import_test_modules()
    
    print(f"測試模組導入結果: {len(test_results)} 個模組")
    for name, result in test_results.items():
        status = "✅" if result.success else "❌"
        print(f"{status} {name}")
    
    # 顯示統計
    imported = importer.get_imported_modules()
    failed = importer.get_failed_modules()
    print(f"成功導入: {len(imported)}, 失敗: {len(failed)}")

