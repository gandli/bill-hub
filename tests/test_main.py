"""
测试 main.py 模块的功能
"""
import pytest
import pandas as pd
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from main import process_pdf


class TestProcessPdf:
    """测试 process_pdf 函数"""

    def test_process_pdf_with_valid_data(self, temp_dir):
        """测试处理有效的 PDF 数据"""
        # 模拟 parse_pdf_to_df 返回有效数据
        mock_df = pd.DataFrame({
            '交易时间': pd.to_datetime(['2024-01-15 10:30:00']),
            '收/支': ['支出'],
            '金额(元)': [50.00],
            '交易对方': ['测试商户']
        })
        
        with patch('main.parse_pdf_to_df') as mock_parse:
            with patch('main.generate_visualizations') as mock_viz:
                mock_parse.return_value = mock_df
                mock_viz.return_value = None
                
                output_dir = temp_dir
                result = process_pdf('/fake/path.pdf', output_dir, 'password')
                
                # 应该返回 DataFrame
                assert result is not None
                assert isinstance(result, pd.DataFrame)
                
                # 应该调用可视化生成
                mock_viz.assert_called_once()

    def test_process_pdf_with_no_data(self, temp_dir):
        """测试处理没有数据的 PDF"""
        with patch('main.parse_pdf_to_df') as mock_parse:
            mock_parse.return_value = None
            
            output_dir = temp_dir
            result = process_pdf('/fake/path.pdf', output_dir, 'password')
            
            # 应该返回 None
            assert result is None

    def test_process_pdf_creates_excel_file(self, temp_dir):
        """测试处理 PDF 会创建 Excel 文件"""
        mock_df = pd.DataFrame({
            '交易时间': pd.to_datetime(['2024-01-15 10:30:00']),
            '收/支': ['支出'],
            '金额(元)': [50.00],
            '交易对方': ['测试商户']
        })
        
        with patch('main.parse_pdf_to_df') as mock_parse:
            with patch('main.generate_visualizations'):
                mock_parse.return_value = mock_df
                
                output_dir = temp_dir
                result = process_pdf('/fake/test.pdf', output_dir, 'password')
                
                # 检查是否创建了 Excel 文件
                excel_path = os.path.join(output_dir, 'test.xlsx')
                assert os.path.exists(excel_path)
                assert os.path.getsize(excel_path) > 0

    def test_process_pdf_handles_visualization_error(self, temp_dir):
        """测试处理可视化生成错误的情况"""
        mock_df = pd.DataFrame({
            '交易时间': pd.to_datetime(['2024-01-15 10:30:00']),
            '收/支': ['支出'],
            '金额(元)': [50.00],
            '交易对方': ['测试商户']
        })
        
        with patch('main.parse_pdf_to_df') as mock_parse:
            with patch('main.generate_visualizations') as mock_viz:
                mock_parse.return_value = mock_df
                mock_viz.side_effect = Exception("Visualization error")
                
                output_dir = temp_dir
                result = process_pdf('/fake/test.pdf', output_dir, 'password')
                
                # 即使可视化失败，也应该返回 DataFrame
                assert result is not None

    def test_process_pdf_handles_parse_error(self, temp_dir):
        """测试处理 PDF 解析错误的情况"""
        with patch('main.parse_pdf_to_df') as mock_parse:
            mock_parse.side_effect = Exception("Parse error")
            
            output_dir = temp_dir
            result = process_pdf('/fake/test.pdf', output_dir, 'password')
            
            # 解析失败应该返回 None
            assert result is None

    def test_process_pdf_creates_html_report(self, temp_dir):
        """测试处理 PDF 会创建 HTML 报告"""
        mock_df = pd.DataFrame({
            '交易时间': pd.to_datetime(['2024-01-15 10:30:00']),
            '收/支': ['支出'],
            '金额(元)': [50.00],
            '交易对方': ['测试商户']
        })
        
        with patch('main.parse_pdf_to_df') as mock_parse:
            with patch('main.generate_visualizations') as mock_viz:
                mock_parse.return_value = mock_df
                mock_viz.side_effect = lambda df, path: open(path, 'w').write('<html>test</html>')
                
                output_dir = temp_dir
                result = process_pdf('/fake/test.pdf', output_dir, 'password')
                
                # 检查是否创建了 HTML 文件
                html_path = os.path.join(output_dir, 'test.html')
                assert os.path.exists(html_path)