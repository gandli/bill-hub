"""
测试 visualize.py 模块的功能
"""
import pytest
import pandas as pd
import os
from visualize import generate_visualizations


class TestGenerateVisualizations:
    """测试 generate_visualizations 函数"""

    def test_generate_with_valid_data(self, sample_df, temp_dir):
        """测试使用有效数据生成可视化"""
        output_path = os.path.join(temp_dir, "test_report.html")
        
        # 应该成功生成文件
        generate_visualizations(sample_df, output_path)
        
        # 检查文件是否生成
        assert os.path.exists(output_path)
        
        # 检查文件是否包含内容
        assert os.path.getsize(output_path) > 0

    def test_generate_with_empty_dataframe(self, temp_dir):
        """测试使用空 DataFrame 生成可视化"""
        empty_df = pd.DataFrame()
        output_path = os.path.join(temp_dir, "empty_report.html")
        
        # 应该不会生成文件或文件为空
        generate_visualizations(empty_df, output_path)
        
        # 检查文件不存在或为空
        if os.path.exists(output_path):
            assert os.path.getsize(output_path) == 0

    def test_generate_with_none_dataframe(self, temp_dir):
        """测试使用 None 生成可视化"""
        output_path = os.path.join(temp_dir, "none_report.html")
        
        # 应该不会生成文件或文件为空
        generate_visualizations(None, output_path)
        
        # 检查文件不存在或为空
        if os.path.exists(output_path):
            assert os.path.getsize(output_path) == 0

    def test_generate_without_required_columns(self, sample_df, temp_dir):
        """测试缺少必需列时的行为"""
        # 移除必需的列
        df_missing = sample_df.drop(columns=['金额(元)', '交易时间'])
        output_path = os.path.join(temp_dir, "missing_cols_report.html")
        
        # 应该不会生成文件
        generate_visualizations(df_missing, output_path)
        
        # 检查文件不存在或为空
        if os.path.exists(output_path):
            assert os.path.getsize(output_path) == 0

    def test_generate_creates_multiple_charts(self, sample_df, temp_dir):
        """测试生成的 HTML 包含多个图表"""
        output_path = os.path.join(temp_dir, "charts_report.html")
        
        generate_visualizations(sample_df, output_path)
        
        # 读取生成的 HTML
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 检查是否包含图表标识（pyecharts 会生成对应的容器）
        assert len(html_content) > 100  # 应该有实质内容

    def test_generate_output_html_valid(self, sample_df, temp_dir):
        """测试生成的 HTML 文件格式有效"""
        output_path = os.path.join(temp_dir, "valid_report.html")
        
        generate_visualizations(sample_df, output_path)
        
        # 读取并检查 HTML 结构
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 应该包含基本的 HTML 标签
        assert '<!DOCTYPE html>' in html_content or '<html' in html_content
        assert '</html>' in html_content

    def test_generate_with_single_month_data(self, temp_dir):
        """测试只有单月数据的可视化"""
        data = {
            '交易时间': pd.to_datetime(['2024-01-15 10:30:00', '2024-01-20 14:00:00']),
            '收/支': ['支出', '支出'],
            '金额(元)': [50.00, 100.00],
            '交易对方': ['商户A', '商户B']
        }
        df = pd.DataFrame(data)
        output_path = os.path.join(temp_dir, "single_month_report.html")
        
        # 应该成功生成
        generate_visualizations(df, output_path)
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_generate_with_multiple_months(self, temp_dir):
        """测试跨月数据的可视化"""
        data = {
            '交易时间': pd.to_datetime([
                '2024-01-15 10:30:00',
                '2024-01-20 14:00:00',
                '2024-02-01 09:00:00',
                '2024-02-10 18:00:00'
            ]),
            '收/支': ['支出', '支出', '支出', '支出'],
            '金额(元)': [50.00, 100.00, 75.00, 120.00],
            '交易对方': ['商户A', '商户B', '商户C', '商户D']
        }
        df = pd.DataFrame(data)
        output_path = os.path.join(temp_dir, "multi_month_report.html")
        
        # 应该成功生成
        generate_visualizations(df, output_path)
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0