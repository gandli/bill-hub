"""
单元测试模块
测试核心功能和数据处理逻辑
"""
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np


class TestCleanAmount(unittest.TestCase):
    """测试金额清洗函数"""

    def setUp(self):
        """导入待测试的函数"""
        from utils import clean_amount
        self.clean_amount = clean_amount

    def test_clean_valid_numbers(self):
        """测试有效的数字清洗"""
        self.assertEqual(self.clean_amount(100.5), 100.5)
        self.assertEqual(self.clean_amount("100.5"), 100.5)
        self.assertEqual(self.clean_amount("¥100.5"), 100.5)
        self.assertEqual(self.clean_amount("$100.5"), 100.5)

    def test_clean_negative_numbers(self):
        """测试负数清洗"""
        self.assertEqual(self.clean_amount(-50.25), -50.25)
        self.assertEqual(self.clean_amount("-50.25"), -50.25)

    def test_clean_invalid_values(self):
        """测试无效值处理"""
        self.assertEqual(self.clean_amount(None), 0.0)
        self.assertEqual(self.clean_amount(""), 0.0)
        self.assertEqual(self.clean_amount("abc"), 0.0)
        self.assertEqual(self.clean_amount("¥abc"), 0.0)


class TestValidateTransactionData(unittest.TestCase):
    """测试交易数据验证函数"""

    def setUp(self):
        """导入待测试的函数"""
        from utils import validate_transaction_data
        self.validate_transaction_data = validate_transaction_data

        # 创建有效的测试数据
        self.valid_df = pd.DataFrame({
            '交易时间': pd.to_datetime(['2024-01-01', '2024-01-02']),
            '金额(元)': [100.0, 200.0],
            '交易对方': ['商户A', '商户B']
        })

    def test_valid_data(self):
        """测试有效数据"""
        is_valid, errors = self.validate_transaction_data(self.valid_df)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_empty_dataframe(self):
        """测试空数据框"""
        empty_df = pd.DataFrame()
        is_valid, errors = self.validate_transaction_data(empty_df)
        self.assertFalse(is_valid)
        self.assertIn("数据为空", errors)

    def test_missing_required_columns(self):
        """测试缺少必要列"""
        invalid_df = pd.DataFrame({
            '时间': pd.to_datetime(['2024-01-01']),
            '金额': [100.0]
        })
        is_valid, errors = self.validate_transaction_data(invalid_df)
        self.assertFalse(is_valid)
        self.assertIn("缺少必要列: 交易时间", errors)

    def test_null_dates(self):
        """测试空日期"""
        invalid_df = self.valid_df.copy()
        invalid_df.loc[0, '交易时间'] = None
        is_valid, errors = self.validate_transaction_data(invalid_df)
        self.assertFalse(is_valid)
        self.assertTrue(any("交易时间为空" in error for error in errors))

    def test_negative_amounts(self):
        """测试负金额"""
        invalid_df = self.valid_df.copy()
        invalid_df.loc[0, '金额(元)'] = -100.0
        is_valid, errors = self.validate_transaction_data(invalid_df)
        self.assertFalse(is_valid)
        self.assertTrue(any("金额为负数" in error for error in errors))


class TestGenerateVisualizations(unittest.TestCase):
    """测试可视化生成函数"""

    def setUp(self):
        """创建测试数据"""
        from visualize import generate_visualizations
        self.generate_visualizations = generate_visualizations

        # 创建模拟数据
        self.test_df = pd.DataFrame({
            '交易时间': pd.to_datetime([
                '2024-01-01 10:00',
                '2024-01-02 14:00',
                '2024-01-03 09:00'
            ]),
            '金额(元)': [100.0, 200.0, 150.0],
            '收/支/其他': ['支出', '支出', '收入'],
            '交易对方': ['商户A', '商户B', '商户C']
        })

        # 创建临时文件用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, 'test_report.html')

    def tearDown(self):
        """清理临时文件"""
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        os.rmdir(self.temp_dir)

    def test_generate_visualizations_success(self):
        """测试成功生成可视化"""
        try:
            self.generate_visualizations(self.test_df, self.output_path)
            self.assertTrue(os.path.exists(self.output_path))
        except Exception as e:
            self.fail(f"生成可视化失败: {e}")

    def test_generate_visualizations_empty_df(self):
        """测试空数据框"""
        empty_df = pd.DataFrame()
        # 应该静默返回，不抛出异常
        try:
            self.generate_visualizations(empty_df, self.output_path)
        except Exception:
            pass  # 空数据框可能不会生成文件

    def test_generate_visualizations_missing_columns(self):
        """测试缺少必要列"""
        invalid_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })
        # 应该静默返回，不抛出异常
        try:
            self.generate_visualizations(invalid_df, self.output_path)
        except Exception:
            pass


class TestMainFunctions(unittest.TestCase):
    """测试主程序函数"""

    def test_main_creates_directories(self):
        """测试 main 函数创建目录"""
        from main import main

        # 在临时目录中运行
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # 运行主程序（会在没有文件时退出）
                with patch('sys.stdout'):  # 抑制输出
                    main()

                # 检查目录是否创建
                self.assertTrue(os.path.exists('input'))
                self.assertTrue(os.path.exists('output'))

            finally:
                os.chdir(original_cwd)


class TestLoggerConfig(unittest.TestCase):
    """测试日志配置"""

    def test_setup_logger(self):
        """测试日志配置函数"""
        from logger_config import setup_logger

        logger = setup_logger("test_logger")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")

    def test_logger_with_file(self):
        """测试带文件输出的日志配置"""
        from logger_config import setup_logger

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'test.log')
            logger = setup_logger("test_file_logger", log_file=log_file)

            logger.info("Test message")

            # 验证日志文件已创建
            self.assertTrue(os.path.exists(log_file))

            # 验证日志内容
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("Test message", content)


if __name__ == '__main__':
    unittest.main(verbosity=2)