"""
工具函数模块
包含 ZIP 解压、PDF 解析和数据处理功能
"""
import os
import re
from typing import List, Optional, Tuple
from datetime import datetime

import pandas as pd
import pdfplumber
import pyzipper
from tqdm import tqdm

from logger_config import logger


def extract_zip(zip_path: str, extract_to: str, password: str) -> List[str]:
    """
    解压带密码的 ZIP 文件

    Args:
        zip_path: ZIP 文件路径
        extract_to: 解压目标目录
        password: 解压密码

    Returns:
        解压后的文件路径列表

    Raises:
        Exception: 解压失败时抛出异常
    """
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            zf.setpassword(password.encode('utf-8'))
            extracted_files: List[str] = []
            for member in zf.infolist():
                zf.extract(member, extract_to)
                extracted_files.append(os.path.join(extract_to, member.filename))
            logger.info(f"成功解压 {zip_path}，共 {len(extracted_files)} 个文件")
            return extracted_files
    except Exception as e:
        logger.error(f"解压失败 {zip_path}: {e}")
        raise Exception(f"解压失败: {e}")


def clean_amount(val) -> float:
    """
    清洗金额字符串，将其转换为浮点数

    Args:
        val: 待清洗的值

    Returns:
        清洗后的金额（浮点数）
    """
    if pd.isna(val) or val == '':
        return 0.0
    # 只保留数字、点号和负号
    res = re.sub(r'[^\d\.-]', '', str(val))
    try:
        return float(res)
    except ValueError:
        return 0.0


def parse_pdf_to_df(pdf_path: str, password: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    解析 PDF 并返回 DataFrame，优先尝试无密码打开

    Args:
        pdf_path: PDF 文件路径
        password: PDF 密码（可选）

    Returns:
        解析后的 DataFrame，如果失败则返回 None

    Raises:
        Exception: 解析过程出错时抛出异常
    """
    all_data: List[pd.DataFrame] = []

    # 尝试打开 PDF 的辅助函数
    def try_open(pwd: Optional[str]) -> Optional[pdfplumber.PDF]:
        try:
            return pdfplumber.open(pdf_path, password=pwd)
        except Exception:
            return None

    pdf = try_open(None)
    if pdf is None and password:
        pdf = try_open(password)

    if pdf is None:
        msg = f"无法打开 PDF (密码错误或文件损坏): {os.path.basename(pdf_path)}"
        logger.error(msg)
        raise Exception(msg)

    try:
        with pdf:
            filename = os.path.basename(pdf_path)
            for page in tqdm(pdf.pages, desc=f"解析 PDF: {filename}", leave=False):
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    df_page = pd.DataFrame(table)
                    all_data.append(df_page)

        if not all_data:
            logger.warning(f"{filename}: 未提取到任何表格数据")
            return None

        final_df = pd.concat(all_data, ignore_index=True)

        # 寻找表头
        header_row_idx = -1
        for idx, row in final_df.iterrows():
            if '交易时间' in row.values:
                header_row_idx = idx
                break

        if header_row_idx != -1:
            final_df.columns = final_df.iloc[header_row_idx]
            final_df = final_df.iloc[header_row_idx + 1:].reset_index(drop=True)
            # 清洗列名，移除换行符
            final_df.columns = [str(c).replace('\n', '') if c else c for c in final_df.columns]

        # 清洗数据
        if '交易时间' in final_df.columns:
            final_df['交易时间'] = pd.to_datetime(final_df['交易时间'], errors='coerce')

        if '金额(元)' in final_df.columns:
            final_df['金额(元)'] = final_df['金额(元)'].apply(clean_amount)

        # 移除完全为空的行
        final_df.dropna(how='all', inplace=True)

        logger.info(f"成功解析 {filename}，共 {len(final_df)} 条记录")
        return final_df

    except Exception as e:
        logger.error(f"解析过程出错 {pdf_path}: {e}")
        raise Exception(f"解析过程出错: {e}")


def validate_transaction_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    验证交易数据的有效性

    Args:
        df: 待验证的 DataFrame

    Returns:
        (是否有效, 错误信息列表)
    """
    errors: List[str] = []

    if df.empty:
        errors.append("数据为空")
        return False, errors

    required_columns = ['交易时间', '金额(元)']
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"缺少必要列: {col}")

    if errors:
        return False, errors

    # 检查数据质量
    null_dates = df['交易时间'].isna().sum()
    if null_dates > 0:
        errors.append(f"有 {null_dates} 条记录的交易时间为空")

    invalid_amounts = (df['金额(元)'] < 0).sum()
    if invalid_amounts > 0:
        errors.append(f"有 {invalid_amounts} 条记录的金额为负数")

    return len(errors) == 0, errors