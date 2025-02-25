import unittest
import logging
import traceback
import os
import sys

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

if __name__ == "__main__":
    os.environ['DEBUG_MODE'] = 'True'
    os.chdir('D:\\AI\\Comfyui_Nvidia\\')
    class_path = os.path.join(os.getcwd(), "custom_nodes","comfyui_ffmpeg_deepseek")
    sys.path.append(class_path)
    from loader import init_plugins
    init_plugins()

from core.error_types import FFmpegError, ErrorLevel

class TestErrorTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """测试类初始化时运行"""
        logger.info("=== 开始错误类型测试套件 ===")
        
    def setUp(self):
        """每个测试用例运行前执行"""
        logger.info(f"开始测试: {self._testMethodName}")
        
    def tearDown(self):
        """每个测试用例运行后执行"""
        logger.info(f"结束测试: {self._testMethodName}")
        
    @classmethod
    def tearDownClass(cls):
        """测试类结束时运行"""
        logger.info("=== 错误类型测试套件结束 ===")

    def test_error_creation(self):
        """测试错误对象创建"""
        error = FFmpegError(
            message="测试错误",
            error_type="TEST_ERROR",
            level=ErrorLevel.ERROR,
            suggestion="这是一个测试建议"
        )
        self.assertEqual(error.message, "测试错误")
        self.assertEqual(error.error_type, "TEST_ERROR")
        self.assertEqual(error.level, ErrorLevel.ERROR)
        self.assertEqual(error.suggestion, "这是一个测试建议")

    def test_error_str_representation(self):
        """测试错误字符串表示"""
        error = FFmpegError("测试错误", suggestion="测试建议")
        expected_str = "[LEXER_ERROR] 测试错误\n建议: 测试建议"
        self.assertEqual(str(error), expected_str)

        # 测试没有建议的情况
        error = FFmpegError("测试错误")
        expected_str = "[LEXER_ERROR] 测试错误"
        self.assertEqual(str(error), expected_str)

    def test_error_dict_conversion(self):
        """测试错误转换为字典"""
        error = FFmpegError(
            message="测试错误",
            error_type="TEST_ERROR",
            level=ErrorLevel.WARNING,
            suggestion="测试建议"
        )
        error_dict = error.to_dict()
        
        self.assertEqual(error_dict["message"], "测试错误")
        self.assertEqual(error_dict["error_type"], "TEST_ERROR")
        self.assertEqual(error_dict["level"], "WARNING")
        self.assertEqual(error_dict["suggestion"], "测试建议")

    def test_error_levels(self):
        """测试错误级别"""
        self.assertEqual(ErrorLevel.WARNING.value, "WARNING")
        self.assertEqual(ErrorLevel.ERROR.value, "ERROR")
        self.assertEqual(ErrorLevel.CRITICAL.value, "CRITICAL")

    def test_error_inheritance(self):
        """测试错误继承关系"""
        error = FFmpegError("测试错误")
        self.assertIsInstance(error, Exception)
        self.assertIsInstance(error, FFmpegError)

    def test_error_with_default_values(self):
        """测试使用默认值创建错误"""
        error = FFmpegError("测试错误")
        self.assertEqual(error.error_type, "LEXER_ERROR")
        self.assertEqual(error.level, ErrorLevel.ERROR)
        self.assertIsNone(error.suggestion)

    def test_error_with_different_levels(self):
        """测试不同级别的错误"""
        warning = FFmpegError("警告", level=ErrorLevel.WARNING)
        error = FFmpegError("错误", level=ErrorLevel.ERROR)
        critical = FFmpegError("严重错误", level=ErrorLevel.CRITICAL)

        self.assertEqual(warning.level, ErrorLevel.WARNING)
        self.assertEqual(error.level, ErrorLevel.ERROR)
        self.assertEqual(critical.level, ErrorLevel.CRITICAL)

if __name__ == '__main__':
    try:
        logger.info("\n=== 开始自动测试 ===\n")
        
        # 创建测试套件
        suite = unittest.TestLoader().loadTestsFromTestCase(TestErrorTypes)
        
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
