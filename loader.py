import os
import sys
import ast
import logging
import traceback
from pathlib import Path
from typing import List, Optional, Set, Dict
from importlib import import_module, util
import argparse

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModuleAnalyzer:
    """模块分析器"""
    
    def __init__(self):
        self.imports = set()
        self.from_imports = {}
        
    def visit_file(self, file_path: str) -> Dict:
        """分析文件中的导入语句"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), file_path)
            
            for node in ast.walk(tree):
                # 处理 import xxx
                if isinstance(node, ast.Import):
                    for name in node.names:
                        self.imports.add(name.name)
                
                # 处理 from xxx import yyy
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        if node.module not in self.from_imports:
                            self.from_imports[node.module] = set()
                        for name in node.names:
                            self.from_imports[node.module].add(name.name)
            
            return {
                'imports': self.imports,
                'from_imports': self.from_imports
            }
        except Exception as e:
            logger.debug(f"分析文件 {file_path} 失败: {e}")
            return {}

class ModuleLoader:
    """模块加载器"""
    
    SKIP_FILES = {
        'loader.py',    # 跳过加载器自身
        'setup.py',     # 跳过安装脚本
        '__init__.py',  # 跳过空的初始化文件
        'conftest.py'   # 跳过pytest配置
    }
    
    SKIP_DIRS = {
        '__pycache__',  # 跳过Python缓存目录
        '.pytest_cache', # 跳过pytest缓存
        'build',        # 跳过构建目录
        'dist',         # 跳过分发目录
        '.git',         # 跳过git目录
        '.vscode',      # 跳过vscode配置
        '.idea',        # 跳过pycharm配置
        'venv',         # 跳过虚拟环境
        'env'           # 跳过虚拟环境
    }
    
    def __init__(self):
        self._loaded_modules = {}
        self._analyzed_files = set()
        self.analyzer = ModuleAnalyzer()
    
    def _get_relative_import_path(self, from_file: str, to_module: str) -> str:
        """计算相对导入路径"""
        from_path = Path(from_file)
        to_path = Path(to_module.replace('.', '/'))
        
        # 计算相对路径
        try:
            rel_path = os.path.relpath(to_path, from_path.parent)
            # 转换为导入路径格式
            import_path = rel_path.replace('/', '.').replace('\\', '.')
            if import_path.startswith('..'):
                # 如果是向上级目录导入，保持原样
                return to_module
            return import_path
        except ValueError:
            # 如果在不同驱动器，使用绝对导入
            return to_module
            
    def _should_skip_file(self, file_path: str) -> bool:
        """检查是否应该跳过该文件"""
        file_name = os.path.basename(file_path)
        if file_name in self.SKIP_FILES:
            return True
            
        # 检查是否是空文件或只包含注释
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or all(line.strip().startswith('#') for line in content.split('\n')):
                    return True
        except Exception:
            return True
            
        return False
    
    def _should_skip_dir(self, dir_path: str) -> bool:
        """检查是否应该跳过该目录"""
        dir_name = os.path.basename(dir_path)
        if dir_name.endswith('__pycache__'):
            return True
        return dir_name in self.SKIP_DIRS
    
    def _safe_import_module(self, module_path: str, root_dir: str) -> None:
        """安全导入模块"""
        try:
            # 分析模块依赖
            imports = self.analyzer.visit_file(module_path)
            
            # 获取相对于根目录的路径
            rel_path = os.path.relpath(module_path, root_dir)
            module_name = os.path.splitext(rel_path)[0].replace('/', '.').replace('\\', '.')
            
            # 修改导入语句为相对导入
            if imports:
                with open(module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换导入语句
                for imp in imports.get('imports', []):
                    rel_import = self._get_relative_import_path(module_path, imp)
                    content = content.replace(f"import {imp}", f"import {rel_import}")
                
                for module, names in imports.get('from_imports', {}).items():
                    rel_import = self._get_relative_import_path(module_path, module)
                    for name in names:
                        content = content.replace(
                            f"from {module} import {name}",
                            f"from {rel_import} import {name}"
                        )
                
                # 写回文件
                with open(module_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 导入模块
            spec = util.spec_from_file_location(module_name, module_path)
            if spec and spec.loader:
                module = util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                self._loaded_modules[module_name] = module
                logger.info(f"成功导入模块: {module_name}")
            
        except Exception as e:
            logger.error(f"导入模块失败 {module_name}: {type(e).__name__} - {str(e)}")
            logger.error(traceback.format_exc())
            self._loaded_modules[module_name] = None

    def load_all_modules(self, root_dir: str) -> None:
        """加载指定目录下的所有Python模块"""
        logger.info(f"项目根目录: {root_dir}")
        parent_dir = str(Path(root_dir).parent)
        logger.info(f"父级目录: {parent_dir}")
        
        # 添加项目目录到Python路径
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            logger.info(f"添加到Python路径: {parent_dir}")
        
        logger.info("开始加载模块...")
        
        # 获取所有Python文件
        for root, dirs, files in os.walk(root_dir):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if not self._should_skip_dir(os.path.join(root, d))]
            
            for file in files:
                if file.endswith('.py'):
                    module_path = os.path.join(root, file)
                    if not self._should_skip_file(module_path):
                        self._safe_import_module(module_path, root_dir)
        
        # 打印加载结果
        loaded = [name for name, module in self._loaded_modules.items() if module is not None]
        logger.info(f"成功加载 {len(loaded)} 个模块:")
        for name in loaded:
            logger.info(f" - {name}")

def init_plugins() -> None:
    """初始化插件"""
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建模块加载器
    loader = ModuleLoader()
    
    # 加载所有模块
    loader.load_all_modules(current_dir)

def show_examples():
    """显示使用示例"""
    examples = """
使用示例:
    # 分析FFmpeg命令
    python loader.py analyze "ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4"
    
    # 以JSON格式输出分析结果
    python loader.py analyze --format json "ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4"
    
    # 优化FFmpeg命令
    python loader.py optimize "ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4"
    
    # 使用硬件加速优化命令
    python loader.py optimize --hw-accel "ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4"
    
    # 验证FFmpeg命令
    python loader.py validate "ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4"
    """
    print(examples)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='FFmpeg命令分析器和优化器',
        usage='%(prog)s [options] command [command_options]',
        epilog='使用 --examples 查看使用示例'
    )
    
    # 全局选项
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径'
    )
    parser.add_argument(
        '--workdir',
        type=str,
        help='工作目录路径'
    )
    parser.add_argument(
        '--examples',
        action='store_true',
        help='显示使用示例'
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析FFmpeg命令')
    analyze_parser.add_argument('input', help='输入的FFmpeg命令')
    analyze_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    
    # optimize 命令
    optimize_parser = subparsers.add_parser('optimize', help='优化FFmpeg命令')
    optimize_parser.add_argument('input', help='输入的FFmpeg命令')
    optimize_parser.add_argument('--hw-accel', action='store_true', help='启用硬件加速')
    
    # validate 命令
    validate_parser = subparsers.add_parser('validate', help='验证FFmpeg命令')
    validate_parser.add_argument('input', help='输入的FFmpeg命令')
    
    args = parser.parse_args()
    
    if args.examples:
        show_examples()
        sys.exit(0)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    return args

def execute_command(args):
    """执行命令"""
    if args.command == 'analyze':
        from parsers.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(args.input)
        if args.format == 'json':
            import json
            print(json.dumps(result, indent=2))
        else:
            print(result)
            
    elif args.command == 'optimize':
        from core.command_builder import CommandBuilder
        builder = CommandBuilder()
        if args.hw_accel:
            from hardware.acceleration import AccelerationManager
            accel = AccelerationManager()
            builder.enable_hw_accel(accel.get_current_accelerator())
        result = builder.build(args.input)
        print(result)
        
    elif args.command == 'validate':
        from parsers.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        try:
            analyzer.validate(args.input)
            print("命令验证通过")
        except Exception as e:
            print(f"命令验证失败: {e}")
            sys.exit(1)

def setup_environment(args):
    """设置运行环境"""
    # 设置工作目录
    if args.workdir:
        project_root = args.workdir
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    os.chdir(project_root)
    logger.info(f"工作目录设置为: {project_root}")
    
    # 添加项目目录到Python路径
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"添加到Python路径: {project_root}")
    
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        logger.info(f"添加到Python路径: {current_dir}")
    
    # 添加插件目录到Python路径
    plugin_dir = os.path.join(project_root, "custom_nodes", "comfyui_ffmpeg_deepseek")
    if plugin_dir not in sys.path:
        sys.path.append(plugin_dir)
        logger.info(f"添加到Python路径: {plugin_dir}")
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")

def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_args()
        
        # 设置环境
        setup_environment(args)
        
        # 初始化插件
        init_plugins()
        
        # 执行命令
        execute_command(args)
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()

# 确保导出类
__all__ = ['ModuleLoader', 'ModuleAnalyzer']
