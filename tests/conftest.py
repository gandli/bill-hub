"""
单元测试配置文件
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import tempfile
import shutil
from datetime import datetime

@pytest.fixture
def sample_df():
    """创建示例 DataFrame 用于测试"""
    data = {
        '交易时间': pd.to_datetime([
            '2024-01-15 10:30:00',
            '2024-01-15 14:20:00',
            '2024-01-16 09:00:00',
            '2024-01-20 18:30:00',
            '2024-02-01 12:00:00'
        ]),
        '收/支': ['支出', '收入', '支出', '支出', '支出'],
        '金额(元)': [50.00, 2000.00, 35.50, 128.00, 99.99],
        '交易对方': ['餐厅A', '工资', '超市B', '交通', '外卖C'],
        '交易类型': ['餐饮', '工资', '购物', '交通', '餐饮']
    }
    return pd.DataFrame(data)

@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)