import unittest
import os
import sys
import logging
import traceback

# 设置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    # 设置调试环境
    os.environ['DEBUG_MODE'] = 'True'
    current_dir = 'D:\\AI\\Comfyui_Nvidia\\'
    os.chdir(current_dir)
    logger.info(f"工作目录设置为: {current_dir}")
    
    class_path = os.path.join(os.getcwd(), "custom_nodes", "comfyui_ffmpeg_deepseek")
    sys.path.append(class_path)
    logger.info(f"添加到Python路径: {class_path}")

    # 导入所需模块
    from parsers.command_parser import parse_ffmpeg_command
    from parsers.lexer.filter_lexer import FilterLexer
    from parsers.semantic_analyzer import SemanticAnalyzer
    from core.error_types import FFmpegError, ErrorLevel
    from parsers.lexer.token_types import FilterTokenType
    
    logger.info("所有模块导入成功")

except Exception as e:
    logger.error(f"初始化失败: {str(e)}")
    logger.error(traceback.format_exc())
    sys.exit(1)

class TestParserComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """测试类初始化时运行"""
        logger.info("=== 开始测试套件 ===")
        
    def setUp(self):
        """每个测试用例运行前执行"""
        logger.info(f"开始测试: {self._testMethodName}")
        
    def tearDown(self):
        """每个测试用例运行后执行"""
        logger.info(f"结束测试: {self._testMethodName}")
        
    @classmethod
    def tearDownClass(cls):
        """测试类结束时运行"""
        logger.info("=== 测试套件结束 ===")

    def test_filter_lexer_basic(self):
        """测试基础滤镜链词法分析"""
        try:
            lexer = FilterLexer("[0:v]scale=1280:720[out]")
            tokens = lexer.tokenize()
            logger.debug(f"生成的Tokens: {tokens}")
            
            expected_tokens = [
                (FilterTokenType.LBRACKET, '['),
                (FilterTokenType.IDENTIFIER, '0:v'),
                (FilterTokenType.RBRACKET, ']'),
                (FilterTokenType.IDENTIFIER, 'scale'),
                (FilterTokenType.EQUALS, '='),
                (FilterTokenType.NUMBER, 1280),
                (FilterTokenType.COLON, ':'),
                (FilterTokenType.NUMBER, 720),
                (FilterTokenType.LBRACKET, '['),
                (FilterTokenType.IDENTIFIER, 'out'),
                (FilterTokenType.RBRACKET, ']')
            ]
            
            self.assertEqual(len(tokens), len(expected_tokens), 
                f"Token数量不匹配: 期望 {len(expected_tokens)}, 实际 {len(tokens)}")
            
            for i, (expected, actual) in enumerate(zip(expected_tokens, tokens)):
                self.assertEqual(expected[0], actual[0], 
                    f"第{i+1}个Token类型不匹配: 期望 {expected[0]}, 实际 {actual[0]}")
                self.assertEqual(str(expected[1]), str(actual[1]), 
                    f"第{i+1}个Token值不匹配: 期望 {expected[1]}, 实际 {actual[1]}")
            
        except Exception as e:
            logger.error(f"测试失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise

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
        print("Special Characters Tokens:", tokens)
        expected_tokens = [
            (FilterTokenType.LBRACKET, '['),
            (FilterTokenType.IDENTIFIER, '0:v'),
            (FilterTokenType.RBRACKET, ']'),
            (FilterTokenType.IDENTIFIER, 'scale'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.NUMBER, 1280),
            (FilterTokenType.COLON, ':'),
            (FilterTokenType.NUMBER, 720),
            (FilterTokenType.COMMA, ','),
            (FilterTokenType.IDENTIFIER, 'format'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.IDENTIFIER, 'yuv420p'),
            (FilterTokenType.PIPE, '|'),
            (FilterTokenType.IDENTIFIER, 'nv12'),
            (FilterTokenType.LBRACKET, '['),
            (FilterTokenType.IDENTIFIER, 'out'),
            (FilterTokenType.RBRACKET, ']')
        ]
        self.assertEqual(len(tokens), len(expected_tokens), "应正确解析特殊字符")
        for i, (expected, actual) in enumerate(zip(expected_tokens, tokens)):
            self.assertEqual(expected[0], actual[0], 
                f"第{i+1}个Token类型不匹配: 期望 {expected[0]}, 实际 {actual[0]}")
            self.assertEqual(str(expected[1]), str(actual[1]), 
                f"第{i+1}个Token值不匹配: 期望 {expected[1]}, 实际 {actual[1]}")

    def test_long_filter_chain(self):
        """测试超长滤镜链"""
        input_str = "[0:v]scale=1280:720,format=yuv420p,hue=s=0,eq=gamma=1.0:contrast=1.0[out]"
        lexer = FilterLexer(input_str)
        tokens = lexer.tokenize()
        print("Long Filter Chain Tokens:", tokens)
        expected_tokens = [
            (FilterTokenType.LBRACKET, '['),
            (FilterTokenType.IDENTIFIER, '0:v'),
            (FilterTokenType.RBRACKET, ']'),
            (FilterTokenType.IDENTIFIER, 'scale'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.NUMBER, 1280),
            (FilterTokenType.COLON, ':'),
            (FilterTokenType.NUMBER, 720),
            (FilterTokenType.COMMA, ','),
            (FilterTokenType.IDENTIFIER, 'format'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.IDENTIFIER, 'yuv420p'),
            (FilterTokenType.COMMA, ','),
            (FilterTokenType.IDENTIFIER, 'hue'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.IDENTIFIER, 's'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.NUMBER, 0),
            (FilterTokenType.COMMA, ','),
            (FilterTokenType.IDENTIFIER, 'eq'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.IDENTIFIER, 'gamma'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.NUMBER, 1.0),
            (FilterTokenType.COLON, ':'),
            (FilterTokenType.IDENTIFIER, 'contrast'),
            (FilterTokenType.EQUALS, '='),
            (FilterTokenType.NUMBER, 1.0),
            (FilterTokenType.LBRACKET, '['),
            (FilterTokenType.IDENTIFIER, 'out'),
            (FilterTokenType.RBRACKET, ']')
        ]
        self.assertEqual(len(tokens), len(expected_tokens), "应正确解析超长滤镜链")
        for i, (expected, actual) in enumerate(zip(expected_tokens, tokens)):
            self.assertEqual(expected[0], actual[0], 
                f"第{i+1}个Token类型不匹配: 期望 {expected[0]}, 实际 {actual[0]}")
            self.assertEqual(str(expected[1]), str(actual[1]), 
                f"第{i+1}个Token值不匹配: 期望 {expected[1]}, 实际 {actual[1]}")

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
            "streams": [
                {"id": "0:v", "type": "video"},
                {"id": "scaled", "type": "video"},
                {"id": "out", "type": "video"}
            ],
            "filter_chains": [
                {"inputs": ["0:v"], "output": "scaled", "filters": []},
                {"inputs": ["scaled"], "output": "out", "filters": []}
            ]
        }
        self.assertTrue(analyzer.validate(valid_command), "合法命令应通过验证")

        invalid_command = {
            "streams": [],
            "filter_chains": [
                {"inputs": ["undefined"], "output": "out", "filters": []}
            ]
        }
        with self.assertRaises(FFmpegError):
            analyzer.validate(invalid_command)

    def test_parse_ffmpeg_command(self):
        """测试FFmpeg命令解析"""
        command = '-i "D:\\AI\\Comfyui_Nvidia\\input\\video\\2.mp4" -threads 16 -c:v libx264 "D:\\AI\\Comfyui_Nvidia\\output\\AdvancedVideoMix_2_9.mp4"'
        result = parse_ffmpeg_command(command)
        expected_input = os.path.normpath('D:\\AI\\Comfyui_Nvidia\\input\\video\\2.mp4')
        expected_output = os.path.normpath('D:\\AI\\Comfyui_Nvidia\\output\\AdvancedVideoMix_2_9.mp4')
        
        self.assertEqual(result['inputs'], [expected_input])
        self.assertEqual(result['outputs'], [expected_output])
        self.assertEqual(result['options'], {'-threads': '16', '-c:v': 'libx264'})
        self.assertEqual(result['filters'], [])

if __name__ == '__main__':
    try:
        logger.info("\n=== 开始自动测试 ===\n")
        
        # 创建测试套件
        suite = unittest.TestLoader().loadTestsFromTestCase(TestParserComponents)
        
        # 创建测试运行器，设置详细输出
        runner = unittest.TextTestRunner(verbosity=2)
        
        # 运行测试并捕获结果
        result = runner.run(suite)
        
        # 输出详细的测试结果
        logger.info("\n=== 测试结果汇总 ===")
        logger.info(f"运行测试总数: {result.testsRun}")
        logger.info(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
        logger.info(f"失败: {len(result.failures)}")
        logger.info(f"错误: {len(result.errors)}")
        
        # 输出失败的测试详情
        if result.failures:
            logger.error("\n=== 测试失败详情 ===")
            for i, failure in enumerate(result.failures, 1):
                logger.error(f"\n{i}. {failure[0]}")
                logger.error(f"失败原因:\n{failure[1]}")
                
        # 输出错误的测试详情
        if result.errors:
            logger.error("\n=== 测试错误详情 ===")
            for i, error in enumerate(result.errors, 1):
                logger.error(f"\n{i}. {error[0]}")
                logger.error(f"错误信息:\n{error[1]}")
        
        logger.info("\n=== 测试执行完成 ===\n")
        
        # 根据测试结果设置退出码
        if not result.wasSuccessful():
            sys.exit(1)
        
    except Exception as e:
        logger.critical(f"测试运行时发生严重错误: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)