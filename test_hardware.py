import unittest  # 导入unittest模块，用于单元测试

import os
import sys

os.environ['DEBUG_MODE'] = 'True'
os.environ['DEBUG_path'] = 'D:\\AI\\Comfyui_Nvidia\\'
is_debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
os.chdir('D:\\AI\\Comfyui_Nvidia\\')

class_path = os.path.join(os.getcwd(), "custom_nodes","ffmpeg-analyzer")
sys.path.append(class_path)
from __init__ import ClassImporter 
importer = ClassImporter()
importer.class_import(["error_types.py", "nvidia.py", "semantic_analyzer.py"])
from nvidia import CUDAAccelerator
from error_types import FFmpegError, ErrorLevel

# 定义测试CUDA加速器的测试类
class TestCUDAAcceleration(unittest.TestCase):  
    # 测试前准备方法，用于初始化测试环境
    def setUp(self):  
        # 创建CUDA加速器实例
        self.accelerator = CUDAAccelerator()  

    # 测试缩放滤镜转换功能
    def test_scale_filter_conversion(self):  
        # 定义测试参数，包括宽度和高度
        params = {"width": 1280, "height": 720}  
        # 调用优化滤镜的方法，传入scale滤镜和测试参数
        result = self.accelerator.optimize_filter(f"qsv_scale=width={params['width']}:height={params['height']}")  
        # 定义期望结果，qsv_scale滤镜的宽度和高度
        expected = "qsv_scale=width=1280:height=720"  
        # 断言结果与期望结果相等
        self.assertEqual(result, expected)  

# 如果是主程序
if __name__ == '__main__':  
    # 运行所有测试
    unittest.main()  # 运行单元测试