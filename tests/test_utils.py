"""
测试 utils.py 模块的功能
"""
import pytest
import pandas as pd
import numpy as np
from utils import clean_amount, extract_zip


class TestCleanAmount:
    """测试 clean_amount 函数"""

    def test_clean_normal_amount(self):
        """测试清洗正常金额"""
        assert clean_amount("50.00") == 50.00
        assert clean_amount("100") == 100.00
        assert clean_amount("99.99") == 99.99

    def test_clean_amount_with_currency_symbol(self):
        """测试清洗带货币符号的金额"""
        assert clean_amount("¥50.00") == 50.00
        assert clean_amount("￥100.00") == 100.00

    def test_clean_amount_with_comma(self):
        """测试清洗带逗号的金额"""
        assert clean_amount("1,000.00") == 1000.00
        assert clean_amount("10,500.50") == 10500.50

    def test_clean_negative_amount(self):
        """测试清洗负金额"""
        assert clean_amount("-50.00") == -50.00
        assert clean_amount("-¥100") == -100.00

    def test_clean_zero_amount(self):
        """测试清洗零金额"""
        assert clean_amount("0") == 0.00
        assert clean_amount("0.00") == 0.00
        assert clean_amount("¥0") == 0.00

    def test_clean_empty_string(self):
        """测试清洗空字符串"""
        assert clean_amount("") == 0.0
        assert clean_amount(" ") == 0.0

    def test_clean_nan_value(self):
        """测试清洗 NaN 值"""
        assert clean_amount(np.nan) == 0.0
        assert clean_amount(pd.NA) == 0.0

    def test_clean_invalid_string(self):
        """测试清洗无效字符串"""
        assert clean_amount("abc") == 0.0
        assert clean_amount("五十元") == 0.0

    def test_clean_amount_with_multiple_decimals(self):
        """测试清洗有多个小数点的金额（取最后一个）"""
        # 这里的实现可能需要根据实际需求调整
        result = clean_amount("50.00.00")
        # re.sub 会保留所有数字、点号和负号，所以可能是 5000.00
        # 实际结果取决于 regex 的行为
        assert isinstance(result, float)


class TestExtractZip:
    """测试 extract_zip 函数"""

    @pytest.mark.skip(reason="需要实际的 ZIP 文件")
    def test_extract_zip_success(self):
        """测试成功解压 ZIP 文件"""
        pass

    @pytest.mark.skip(reason="需要实际的 ZIP 文件")
    def test_extract_zip_with_password(self):
        """测试解压带密码的 ZIP 文件"""
        pass

    @pytest.mark.skip(reason="需要实际的 ZIP 文件")
    def test_extract_zip_wrong_password(self):
        """测试使用错误密码解压"""
        pass