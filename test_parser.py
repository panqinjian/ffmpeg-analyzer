import unittest
import os
import sys

if __name__ == "__main__":
    os.environ['DEBUG_MODE'] = 'True'
    os.chdir('D:\\AI\\Comfyui_Nvidia\\')
    class_path = os.path.join(os.getcwd(), "custom_nodes","comfyui_ffmpeg_deepseek")
    sys.path.append(class_path)
    from loader import init_plugins
    init_plugins()
from lexer.filter_lexer import FilterLexer
from parsers.semantic_analyzer import SemanticAnalyzer
from core.error_types import FFmpegError, ErrorLevel



class TestParserComponents(unittest.TestCase):
    def test_filter_lexer_basic(self):
        """测试基础滤镜链词法分析"""
        
        lexer = FilterLexer(
            "ffmpeg.exe -y -hwaccel cuda -threads 16 "
            "-i D:\\AI\\Comfyui_Nvidia\\input\\video\\2.mp4 "
            "-i D:\\AI\\Comfyui_Nvidia\\input\\video\\b.mp4 "
            "-filter_complex "
            "[1:v]scale=iw*1.0:ih*1.0,rotate=0.0*PI/180, "
            "colorbalance=rs=0:gs=0:bs=0,gblur=sigma=0.0,eq=brightness=0.0:contrast=1.0,format=rgba, "
            "colorchannelmixer=aa=1.0[v2];"
            "[0:v]scale=iw/2:ih/2[base1]; "
            "[v2]scale=iw/2:ih/2[base2]; "
            "[base1][base2]hstack[outv];"
            "[1:a]volume=1.0[a1]; "
            "[0:a][a1]amix=inputs=2[aout]; "
            "-map [outv] -map [aout] "
            "-c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k "
            "D:\\AI\\Comfyui_Nvidia\\output\\AdvancedVideoMix_2_9.mp4"
        )
        tokens = lexer.tokenize()
        print(tokens)
        self.assertEqual(len(tokens), 9, "应正确切分9个token")

    def test_empty_input(self):
        """测试空输入"""
        lexer = FilterLexer("")
        with self.assertRaises(FFmpegError):
            lexer.tokenize()

    def test_special_characters(self):
        """测试特殊字符"""
        input_str = "[0:v]scale=1280:720,format=yuv420p|nv12[out]"
        lexer = FilterLexer(input_str)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 10, "应正确解析特殊字符")

    def test_long_filter_chain(self):
        """测试超长滤镜链"""
        input_str = "[0:v]scale=1280:720,format=yuv420p,hue=s=0,eq=gamma=1.0:contrast=1.0[out]"
        lexer = FilterLexer(input_str)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 16, "应正确解析超长滤镜链")

    def test_invalid_syntax(self):
        """测试非法语法"""
        input_str = "[0:v]scale=1280:720,format=yuv420p|nv12[out"
        lexer = FilterLexer(input_str)
        with self.assertRaises(FFmpegError):
            lexer.tokenize()

    def test_missing_closing_bracket(self):
        """测试缺少右括号"""
        input_str = "[0:vscale=1280:720[out]"
        lexer = FilterLexer(input_str)
        with self.assertRaises(FFmpegError):
            lexer.tokenize()

    def test_invalid_number_format(self):
        """测试非法数字格式"""
        input_str = "[0:v]scale=1280x720[out]"
        lexer = FilterLexer(input_str)
        with self.assertRaises(FFmpegError):
            lexer.tokenize()

    def test_undefined_stream(self):
        """测试未定义流标签"""
        input_str = "[1:v]scale=1280:720[out]"
        analyzer = SemanticAnalyzer()
        with self.assertRaises(FFmpegError):
            analyzer.analyze(input_str)

    def test_semantic_validation(self):
        """测试流标签生命周期验证"""
        analyzer = SemanticAnalyzer()
        valid_command = {
            "filter_chains": [
                {"inputs": ["0:v"], "output": "scaled", "filters": []},
                {"inputs": ["scaled"], "output": "out", "filters": []}
            ]
        }
        self.assertTrue(analyzer.validate(valid_command), "合法命令应通过验证")

        invalid_command = {
            "filter_chains": [
                {"inputs": ["undefined"], "output": "out", "filters": []}
            ]
        }
        with self.assertRaises(Exception):
            analyzer.validate(invalid_command)
# 如果是主程序
if __name__ == '__main__':  
    # 运行所有测试
    unittest.main()  # 运行单元测试