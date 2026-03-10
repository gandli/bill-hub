"""
微信支付账单批处理解析器主程序
支持 ZIP 压缩包和独立 PDF 文件的批量处理
"""
import os
import sys
from typing import Optional, List

import pandas as pd
from logger_config import logger
from utils import extract_zip, parse_pdf_to_df, validate_transaction_data
from visualize import generate_visualizations


def main() -> None:
    """主函数：处理账单文件并生成可视化报告"""
    print("=== 微信支付账单批处理解析器 ===")

    input_dir = 'input'
    output_dir = 'output'
    temp_dir = 'temp_extracted'

    # 确保目录存在
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        msg = f"提示: 已创建 {input_dir} 目录，请将 ZIP 或 PDF 文件放入其中后再次运行。"
        logger.info(msg)
        print(msg)
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"创建输出目录: {output_dir}")

    # 扫描 input 目录
    zip_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.zip')])
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')])

    if not zip_files and not pdf_files:
        msg = f"错误: 在 {input_dir} 目录中未找到 .zip 或 .pdf 文件"
        logger.error(msg)
        print(msg)
        return

    logger.info(f"找到 {len(zip_files)} 个 ZIP 文件和 {len(pdf_files)} 个 PDF 文件")

    # 用于存放所有解析出的数据
    all_dfs: List[pd.DataFrame] = []
    # 记录通用密码
    common_password: Optional[str] = None

    # 处理 ZIP 文件
    for zip_file in zip_files:
        zip_path = os.path.join(input_dir, zip_file)
        logger.info(f"[处理压缩包] {zip_file}")
        print(f"\n[处理压缩包] {zip_file}")

        password = common_password
        retry_count = 0
        while retry_count < 3:
            if not password:
                # 使用 getpass 获取密码（但在非交互环境会失败）
                try:
                    import getpass
                    password = getpass.getpass(f"请输入解压密码: ")
                except Exception:
                    logger.error("无法获取密码（非交互环境）")
                    break

            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            try:
                extracted_files = extract_zip(zip_path, temp_dir, password)
                common_password = password  # 更新通用密码

                # 查找解压出的 PDF
                extracted_pdfs = [f for f in extracted_files if f.lower().endswith('.pdf')]
                if not extracted_pdfs:
                    msg = "  警告: 压缩包内未找到 PDF 文件"
                    logger.warning(msg)
                    print(msg)

                for pdf_path in extracted_pdfs:
                    df = process_pdf(pdf_path, output_dir, password)
                    if df is not None:
                        all_dfs.append(df)
                break  # 成功处理，跳出重试循环
            except Exception as e:
                logger.error(f"处理压缩包失败 {zip_file}: {e}")
                print(f"  错误: {e}")
                password = None  # 清空密码以便重新输入
                retry_count += 1
                if retry_count < 3:
                    print(f"  请重试密码 (剩余次数: {3-retry_count})")
                else:
                    print(f"  跳过该文件。")

    # 处理 input 目录直接存放的 PDF 文件
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        logger.info(f"[处理独立 PDF] {pdf_file}")
        print(f"\n[处理独立 PDF] {pdf_file}")
        df = process_pdf(pdf_path, output_dir, common_password)
        if df is not None:
            all_dfs.append(df)

    # 清理临时目录
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)
        logger.info(f"清理临时目录: {temp_dir}")

    # === 合并汇总逻辑 ===
    if len(all_dfs) > 1:
        logger.info("正在生成合并汇总报告")
        print("\n--- 正在生成合并汇总报告 ---")
        merged_df = pd.concat(all_dfs, ignore_index=True)

        # 按交易时间排序
        if '交易时间' in merged_df.columns:
            merged_df.sort_values(by='交易时间', inplace=True)

        merged_base = "merged_bill"
        merged_xlsx = os.path.join(output_dir, f"{merged_base}.xlsx")
        merged_html = os.path.join(output_dir, f"{merged_base}.html")

        # 导出汇总 Excel
        try:
            with pd.ExcelWriter(
                merged_xlsx,
                engine='xlsxwriter',
                datetime_format='yyyy-mm-dd hh:mm:ss'
            ) as writer:
                merged_df.to_excel(writer, index=False)
            logger.info(f"汇总 Excel 已导出: {merged_xlsx}")
            print(f"  汇总 Excel 已导出: {merged_xlsx}")
        except Exception as e:
            logger.error(f"导出汇总 Excel 失败: {e}")
            print(f"  导出汇总 Excel 失败: {e}")

        # 生成汇总可视化
        try:
            generate_visualizations(merged_df, merged_html)
            logger.info(f"汇总可视化报表已生成: {merged_html}")
            print(f"  汇总可视化报表已生成: {merged_html}")
        except Exception as ev:
            logger.error(f"生成汇总报表失败: {ev}")
            print(f"  生成汇总报表失败: {ev}")

    logger.info("所有任务处理完成")
    print("\n=== 所有任务处理完成 ===")


def process_pdf(pdf_path: str, output_dir: str, password: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    处理单个 PDF 文件

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录
        password: PDF 密码（可选）

    Returns:
        处理后的 DataFrame，如果失败则返回 None
    """
    try:
        df = parse_pdf_to_df(pdf_path, password)

        if df is None:
            return None

        # 验证数据有效性
        is_valid, errors = validate_transaction_data(df)
        if not is_valid:
            logger.warning(f"数据验证失败 {pdf_path}: {', '.join(errors)}")

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.xlsx")

        # 使用 ExcelWriter 并指定日期时间格式
        try:
            with pd.ExcelWriter(
                output_path,
                engine='xlsxwriter',
                datetime_format='yyyy-mm-dd hh:mm:ss'
            ) as writer:
                df.to_excel(writer, index=False)

            logger.info(f"成功导出: {output_path}")
            print(f"  成功导出: {output_path}")
        except Exception as e:
            logger.error(f"导出 Excel 失败 {output_path}: {e}")
            print(f"  导出 Excel 失败: {e}")
            return df  # 即使导出失败也返回数据

        # 生成可视化报表
        html_output_path = os.path.join(output_dir, f"{base_name}.html")
        try:
            generate_visualizations(df, html_output_path)
            logger.info(f"可视化报表已生成: {html_output_path}")
            print(f"  可视化报表已生成: {html_output_path}")
        except Exception as ev:
            logger.error(f"生成可视化报表失败 {html_output_path}: {ev}")
            print(f"  生成可视化报表失败: {ev}")

        return df

    except Exception as e:
        logger.error(f"解析 PDF 失败 {pdf_path}: {e}")
        print(f"  解析 PDF 失败: {e}")
        return None


if __name__ == "__main__":
    main()