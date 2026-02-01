import pyzipper
import pdfplumber
import pandas as pd
import re
import os
from tqdm import tqdm
from datetime import datetime

def extract_zip(zip_path, extract_to, password):
    """
    解压带密码的 ZIP 文件
    """
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            zf.setpassword(password.encode('utf-8'))
            extracted_files = []
            for member in zf.infolist():
                zf.extract(member, extract_to)
                extracted_files.append(os.path.join(extract_to, member.filename))
            return extracted_files
    except Exception as e:
        raise Exception(f"解压失败: {e}")

def clean_amount(val):
    """
    清洗金额字符串
    """
    if pd.isna(val) or val == '': return 0.0
    # 只保留数字、点号和负号
    res = re.sub(r'[^\d\.-]', '', str(val))
    try:
        return float(res)
    except:
        return 0.0

def parse_pdf_to_df(pdf_path, password=None):
    """
    解析 PDF 并返回 DataFrame，优先尝试无密码打开
    """
    all_data = []
    
    # 尝试打开 PDF 的辅助函数
    def try_open(pwd):
        try:
            return pdfplumber.open(pdf_path, password=pwd)
        except Exception:
            return None

    pdf = try_open(None)
    if pdf is None and password:
        pdf = try_open(password)
    
    if pdf is None:
        raise Exception(f"无法打开 PDF (密码错误或文件损坏): {os.path.basename(pdf_path)}")

    try:
        with pdf:
            for page in tqdm(pdf.pages, desc=f"解析 PDF: {os.path.basename(pdf_path)}", leave=False):
                tables = page.extract_tables()
                if not tables:
                    continue
                for table in tables:
                    df_page = pd.DataFrame(table)
                    all_data.append(df_page)

        if not all_data:
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
        return final_df

    except Exception as e:
        raise Exception(f"解析过程出错: {e}")
