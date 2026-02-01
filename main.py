import os
import getpass
import sys
import pandas as pd
from utils import extract_zip, parse_pdf_to_df
from visualize import generate_visualizations

def main():
    print("=== 微信支付账单批处理解析器 ===")
    
    input_dir = 'input'
    output_dir = 'output'
    temp_dir = 'temp_extracted'
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"提示: 已创建 {input_dir} 目录，请将 ZIP 或 PDF 文件放入其中后再次运行。")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 扫描 input 目录
    zip_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.zip')])
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')])
    
    if not zip_files and not pdf_files:
        print(f"错误: 在 {input_dir} 目录中未找到 .zip 或 .pdf 文件")
        return

    # 用于存放所有解析出的数据
    all_dfs = []
    # 记录通用密码
    common_password = None

    # 处理 ZIP 文件
    for zip_file in zip_files:
        zip_path = os.path.join(input_dir, zip_file)
        print(f"\n[处理压缩包] {zip_file}")
        
        password = common_password
        retry_count = 0
        while retry_count < 3:
            if not password:
                password = getpass.getpass(f"请输入解压密码: ")
            
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            try:
                extracted_files = extract_zip(zip_path, temp_dir, password)
                common_password = password # 更新通用密码
                
                # 查找解压出的 PDF
                extracted_pdfs = [f for f in extracted_files if f.lower().endswith('.pdf')]
                if not extracted_pdfs:
                    print("  警告: 压缩包内未找到 PDF 文件")
                
                for pdf_path in extracted_pdfs:
                    df = process_pdf(pdf_path, output_dir, password)
                    if df is not None:
                        all_dfs.append(df)
                break # 成功处理，跳出重试循环
            except Exception as e:
                print(f"  错误: {e}")
                password = None # 清空密码以便重新输入
                retry_count += 1
                if retry_count < 3:
                    print(f"  请重试密码 (剩余次数: {3-retry_count})")
                else:
                    print(f"  跳过该文件。")

    # 处理 input 目录直接存放的 PDF 文件
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        print(f"\n[处理独立 PDF] {pdf_file}")
        df = process_pdf(pdf_path, output_dir, common_password)
        if df is not None:
            all_dfs.append(df)

    # 清理临时目录
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)
    
    # === 合并汇总逻辑 ===
    if len(all_dfs) > 1:
        print("\n--- 正在生成合并汇总报告 ---")
        merged_df = pd.concat(all_dfs, ignore_index=True)
        # 按交易时间排序
        if '交易时间' in merged_df.columns:
            merged_df.sort_values(by='交易时间', inplace=True)
        
        merged_base = "merged_bill"
        merged_xlsx = os.path.join(output_dir, f"{merged_base}.xlsx")
        merged_html = os.path.join(output_dir, f"{merged_base}.html")
        
        # 导出汇总 Excel
        with pd.ExcelWriter(merged_xlsx, engine='xlsxwriter', datetime_format='yyyy-mm-dd hh:mm:ss') as writer:
            merged_df.to_excel(writer, index=False)
        print(f"  汇总 Excel 已导出: {merged_xlsx}")
        
        # 生成汇总可视化
        try:
            generate_visualizations(merged_df, merged_html)
            print(f"  汇总可视化报表已生成: {merged_html}")
        except Exception as ev:
            print(f"  生成汇总报表失败: {ev}")

    print("\n=== 所有任务处理完成 ===")

def process_pdf(pdf_path, output_dir, password):
    try:
        df = parse_pdf_to_df(pdf_path, password)
        if df is not None:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}.xlsx")
            
            # 使用 ExcelWriter 并指定日期时间格式
            with pd.ExcelWriter(output_path, engine='xlsxwriter', datetime_format='yyyy-mm-dd hh:mm:ss') as writer:
                df.to_excel(writer, index=False)
                
            print(f"  成功导出: {output_path}")

            # 生成可视化报表
            html_output_path = os.path.join(output_dir, f"{base_name}.html")
            try:
                generate_visualizations(df, html_output_path)
                print(f"  可视化报表已生成: {html_output_path}")
            except Exception as ev:
                print(f"  生成可视化报表失败: {ev}")
            
            return df
        else:
            print(f"  提示: {os.path.basename(pdf_path)} 中未识别出交易数据")
            return None
    except Exception as e:
        print(f"  解析 PDF 失败: {e}")
        return None

if __name__ == "__main__":
    main()
