import os
import sys
import importlib
from typing import List



class FileUtils:
    @staticmethod
    def find_file_path(filename: str) -> str:
        """根据输入的文件名在指定目录中搜索完整路径"""
        current_file_path = os.path.join(os.getcwd(), "custom_nodes", "ffmpeg-analyzer")
        for root, dirs, files in os.walk(current_file_path):
            if filename in files:
                return os.path.join(root, filename)
        return "文件未找到"

class ClassImporter:
    def class_import(self, files: List[str]) -> None:
        for filename in files:
            file_path = FileUtils.find_file_path(filename)
            if file_path == "文件未找到":
                print(f"文件 {filename} 未找到")
                continue
            
            # 获取文件所在目录并添加到sys.path
            file_dir = os.path.dirname(file_path)
            if file_dir not in sys.path:
                sys.path.insert(0, file_dir)
            
            # 提取模块名（不含扩展名）
            module_name = os.path.splitext(filename)[0]
            
            try:
                # 动态导入模块
                module = importlib.import_module(module_name)
                sys.path.append(os.path.dirname(file_path))
                # 将模块内容导入全局命名空间
                globals().update(module.__dict__)
                print(f"成功导入模块 {module_name}")
            except Exception as e:
                print(f"导入模块 {module_name} 失败: {e}")
            finally:
                # 移除临时添加的路径（可选）
                sys.path.remove(file_dir)


os.environ['DEBUG_MODE'] = 'True'
os.environ['DEBUG_path'] = r'D:\\AI\\Comfyui_Nvidia\\'
os.chdir(r'D:\\AI\\Comfyui_Nvidia\\')
Classimport = ClassImporter()
Classimport.class_import(["error_types.py", "semantic_analyzer.py", "acceleration.py", "command_processor.py"])



__version__ = "1.0.0"
__all__ = ['FFmpegCommandProcessor', 'SemanticAnalyzer', 'FileUtils']
