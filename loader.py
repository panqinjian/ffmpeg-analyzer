import importlib
import logging
import os
import sys
from pathlib import Path
from typing import List, Set, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)



def init_plugins():
    os.environ['DEBUG_MODE'] = 'True'
    os.environ['DEBUG_path'] = r'D:\\AI\\Comfyui_Nvidia\\'
    os.chdir(r'D:\\AI\\Comfyui_Nvidia\\')
    # 确保使用 Path 对象
    plugins_dir = Path(os.path.join(os.getcwd(), "custom_nodes", "ffmpeg-analyzer")).parent / "ffmpeg-analyzer"  # ← 关键修复
    DynamicModuleLoader.load_modules(plugins_dir)


class DynamicModuleLoader:
    _imported_modules: Set[str] = set()
    
    def __init__(self):
        self._filters: List[Callable[[str], bool]] = []
        self._post_import_hooks: List[Callable[[str], None]] = []

    @classmethod
    def load_modules(
        cls,
        base_path: Path,
        parent_package: Optional[str] = None,
        max_workers: int = 4,
    ) -> List[str]:
        """
        递归加载指定目录下的所有Python模块
        
        :param base_path: 目标目录的Path对象
        :param parent_package: 父包名称 (例如 "myapp.plugins")
        :param max_workers: 并行导入的线程数
        :return: 成功加载的模块列表
        """
        if not base_path.is_dir():
            raise ValueError(f"Invalid directory path: {base_path}")

        sys.path.insert(0, str(base_path.parent))
        try:
            return cls._load_modules_recursive(
                base_path, 
                base_path,
                parent_package or base_path.name,
                max_workers
            )
        finally:
            sys.path.pop(0)

    @classmethod
    def _load_modules_recursive(
        cls,
        root: Path,
        current: Path,
        package: str,
        max_workers: int
    ) -> List[str]:
        modules = []
        futures = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 处理当前目录
            for path in current.iterdir():
                if path.is_dir():
                    if (path / "__init__.py").exists():
                        modules.extend(
                            cls._load_modules_recursive(
                                root,
                                path,
                                f"{package}.{path.name}",
                                max_workers
                            )
                        )
                    continue
                
                if cls._is_valid_module(path):
                    module_name = cls._build_module_name(root, path, package)
                    futures.append(
                        executor.submit(
                            cls._safe_import_module,
                            module_name
                        )
                    )

            # 收集结果
            for future in as_completed(futures):
                result = future.result()
                if result:
                    modules.append(result)
        
        return modules

    @classmethod
    def _is_valid_module(cls, path: Path) -> bool:
        """验证是否为有效模块文件"""
        return (
            path.suffix == ".py"
            and path.name != "__init__.py"
            and not path.name.startswith("_")
        )

    @classmethod
    def _build_module_name(
        cls,
        root: Path,
        path: Path,
        package: str
    ) -> str:
        """构建完整模块名称"""
        relative_path = path.relative_to(root.parent)
        return str(relative_path.with_suffix('')).replace('/', '.')

    @classmethod
    def _safe_import_module(cls, module_name: str) -> Optional[str]:
        """线程安全的模块导入"""
        if module_name in cls._imported_modules:
            return None
            
        try:
            module = importlib.import_module(module_name)
            cls._imported_modules.add(module_name)
            logger.debug(f"Successfully imported: {module_name}")
            return module_name
        except Exception as e:
            logger.error(
                f"Failed to import {module_name}: {type(e).__name__} - {str(e)}",
                exc_info=True
            )
            return None

    def add_filter(self, filter_fn: Callable[[str], bool]):
        """添加模块过滤函数"""
        self._filters.append(filter_fn)

    def add_hook(self, hook_fn: Callable[[str], None]):
        """添加后导入钩子函数"""
        self._post_import_hooks.append(hook_fn)

"""
# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    loader = DynamicModuleLoader()
    
    # 添加自定义过滤器
    loader.add_filter(lambda name: "test" not in name)
    
    # 添加后处理钩子
    def registration_hook(module_name: str):
        module = sys.modules[module_name]
        # 注册模块中的组件
        ...
    
    loader.add_hook(registration_hook)
    
    # 加载模块
    loaded = loader.load_modules(
        Path(__file__).parent / "plugins",
        max_workers=8
    )
    
    print(f"Loaded {len(loaded)} modules:")
    for m in loaded:
        print(f" - {m}")
"""