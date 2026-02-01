import pandas as pd
import numpy as np
from pyecharts.charts import Line, Pie, Bar, Scatter, Page
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import os

# 容错处理 JSCode 导入
try:
    from pyecharts.commons.utils import JSCode
except ImportError:
    class JSCode:
        def __init__(self, code: str): self.code = code
        def __str__(self): return self.code

def generate_visualizations(df, output_path):
    """
    基于交易数据生成可视化 HTML 报表，包含财务概览、趋势分析和消费洞察
    支持移动端自适应和图表导出功能
    """
    if df is None or df.empty:
        return

    df_plot = df.copy()
    if '金额(元)' not in df_plot.columns or '交易时间' not in df_plot.columns:
        return

    # 1. 数据深度预处理
    type_col = None
    for col in ['收/支/其他', '收/支']:
        if col in df_plot.columns:
            type_col = col
            break
            
    df_plot['月份'] = df_plot['交易时间'].dt.to_period('M').astype(str)
    df_plot['小时'] = df_plot['交易时间'].dt.hour
    df_plot['日期'] = df_plot['交易时间'].dt.date
    
    # 统计核心指标
    total_expense = df_plot[df_plot[type_col] == '支出']['金额(元)'].sum() if type_col else 0
    total_income = df_plot[df_plot[type_col] == '收入']['金额(元)'].sum() if type_col else 0
    net_flow = total_income - total_expense
    merchant_count = df_plot['交易对方'].nunique()

    # 核心数据子集
    df_expense = df_plot[df_plot[type_col] == '支出'] if type_col else df_plot
    df_income = df_plot[df_plot[type_col] == '收入'] if type_col else pd.DataFrame()

    # 创建页面，使用简洁布局并添加自定义样式
    page = Page(
        layout=Page.SimplePageLayout,
        page_title="微信支付账单分析报告"
    )
    
    # 添加页面级配置
    page.page_title = "微信支付账单分析报告"
    
    # 自定义 CSS 样式（将在渲染后注入）
    custom_css = """
    <style>
        body {
            background: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }
        .chart-container {
            margin: 10px auto;
            max-width: 1400px;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            font-size: 28px;
            margin: 15px 0;
            font-weight: 600;
        }
    </style>
    """

    # 通用工具栏配置（支持导出PNG）
    common_toolbox = opts.ToolboxOpts(
        feature=opts.ToolBoxFeatureOpts(
            save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
                title="保存为图片",
                pixel_ratio=2  # 高清导出
            ),
            restore=opts.ToolBoxFeatureRestoreOpts(title="还原"),
            data_view=opts.ToolBoxFeatureDataViewOpts(title="数据视图", is_read_only=True),
        )
    )

    # --- 💎 顶部数据看板：核心摘要 (使用表格式展示) ---
    # 计算更多统计指标
    total_transactions = len(df_plot)
    expense_count = len(df_expense)
    income_count = len(df_income)
    avg_expense = total_expense / expense_count if expense_count > 0 else 0
    avg_income = total_income / income_count if income_count > 0 else 0
    
    # 计算更多核心指标
    trading_days = df_plot['日期'].nunique()  # 交易天数
    daily_avg_expense = total_expense / trading_days if trading_days > 0 else 0  # 日均支出
    max_single_expense = df_expense['金额(元)'].max() if not df_expense.empty else 0  # 最大单笔支出
    expense_days = df_expense['日期'].nunique() if not df_expense.empty else 0  # 支出天数
    
    # 使用 Bar 创建卡片式看板
    summary_bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN, height="220px"))
        .add_xaxis([
            "总支出", "总收入", "收支净额", "交易天数", 
            "支出笔数", "收入笔数", "商户数", 
            "笔均支出", "笔均收入", "日均支出", "最大单笔", "支出天数"
        ])
        .add_yaxis(
            "金额/数量", 
            [
                round(total_expense, 2), 
                round(total_income, 2), 
                round(net_flow, 2), 
                trading_days,
                expense_count,
                income_count,
                merchant_count,
                round(avg_expense, 2),
                round(avg_income, 2),
                round(daily_avg_expense, 2),
                round(max_single_expense, 2),
                expense_days
            ],
            label_opts=opts.LabelOpts(
                is_show=True, 
                position="top",
                formatter="{c}",
                font_size=11,
                font_weight="bold"
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="💎 财务数据核心摘要", 
                subtitle=f"账单周期概览 | 总交易笔数: {total_transactions} | 跨度: {trading_days} 天",
                pos_left="center"
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(rotate=0, font_size=11),
            ),
            yaxis_opts=opts.AxisOpts(is_show=False),
            legend_opts=opts.LegendOpts(is_show=False),
            toolbox_opts=common_toolbox,
        )
        .set_series_opts(
            itemstyle_opts=opts.ItemStyleOpts(
                color=JSCode("""
                    function(params) {
                        var colorList = ['#d14b41', '#5793f3', '#675bba', '#fac858', '#91cc75', '#73c0de', '#ee6666', '#3ba272'];
                        return colorList[params.dataIndex];
                    }
                """)
            )
        )
    )
    page.add(summary_bar)

    # --- 📈 基础图表 1：月度收支趋势 ---
    monthly_expense = df_expense.groupby('月份')['金额(元)'].sum()
    monthly_income = df_income.groupby('月份')['金额(元)'].sum()
    months = sorted(list(set(monthly_expense.index.tolist() + monthly_income.index.tolist())))
    
    bar_trend = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
        .add_xaxis(months)
        .add_yaxis("月度支出", [round(monthly_expense.get(m, 0), 2) for m in months], color="#d14b41")
        .add_yaxis("月度收入", [round(monthly_income.get(m, 0), 2) for m in months], color="#5793f3")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="📈 月度收支走势分析", subtitle="观察跨月财务变动情况"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
            legend_opts=opts.LegendOpts(pos_top="5%"),
            toolbox_opts=common_toolbox,
        )
    )
    page.add(bar_trend)

    # --- 🏦 基础图表 2 & 3：收支对比与分类构成的组合 (Pie) ---
    if type_col:
        type_dist = df_plot.groupby(type_col)['金额(元)'].sum()
        pie_ratio = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.WALDEN, width="480px", height="400px"))
            .add(
                "", 
                [list(z) for z in zip(type_dist.index.tolist(), type_dist.round(2).tolist())],
                radius=["40%", "70%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="🏦 资金结构分布", pos_left="center"),
                legend_opts=opts.LegendOpts(is_show=False),
                toolbox_opts=common_toolbox,
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
        )

        counterparty_col = '交易对方' if '交易对方' in df_plot.columns else None
        if counterparty_col and not df_expense.empty:
            cat_summary = df_expense.groupby(counterparty_col)['金额(元)'].sum().sort_values(ascending=False)
            top_10_cats = cat_summary.head(10).to_dict()
            others_val = cat_summary.iloc[10:].sum() if len(cat_summary) > 10 else 0
            pie_data = [list(z) for z in top_10_cats.items()]
            if others_val > 0: pie_data.append(["其他商户汇总", round(others_val, 2)])

            pie_cat = (
                Pie(init_opts=opts.InitOpts(theme=ThemeType.WALDEN, width="480px", height="400px"))
                .add(
                    "", 
                    pie_data,
                    radius=["30%", "65%"],
                    rosetype="area"
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="🍔 消费去向构成 (Top 10)", pos_left="center"),
                    legend_opts=opts.LegendOpts(is_show=False),
                    toolbox_opts=common_toolbox,
                )
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
            )
            page.add(pie_ratio, pie_cat)

    # --- 🥇 专题图表 1：单商户累计支出 Top 20 ---
    if counterparty_col and not df_expense.empty:
        top_merchants = df_expense.groupby(counterparty_col)['金额(元)'].sum().sort_values(ascending=True).tail(20)
        bar_top = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
            .add_xaxis(top_merchants.index.tolist())
            .add_yaxis("支出金额", top_merchants.round(2).tolist())
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="🥇 商户支出排行榜 (Top 20)", subtitle="识别主要消费对象"),
                xaxis_opts=opts.AxisOpts(name="金额"),
                visualmap_opts=opts.VisualMapOpts(is_show=False, min_=0, max_=float(top_merchants.max()), dimension=0, range_color=["#7fb9d8", "#005ea1"]),
                toolbox_opts=common_toolbox,
            )
        )
        page.add(bar_top)

    # --- 🕒 & 🔍 专题图表：交易时间分析 & 商户频率分析（并排显示）---
    line_time = None
    bar_consec = None
    
    if not df_expense.empty:
        hourly_stats = df_expense.groupby('小时')['金额(元)'].agg(['count', 'sum']).reindex(range(24), fill_value=0)
        line_time = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.WALDEN, width="700px", height="400px"))
            .add_xaxis([f"{h}点" for h in range(24)])
            .add_yaxis("交易频次", hourly_stats['count'].tolist(), is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=3, color="#ff9900"))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="🕒 24小时交易习惯分析", subtitle="了解日常消费时间分布"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                xaxis_opts=opts.AxisOpts(boundary_gap=False),
                toolbox_opts=common_toolbox,
            )
            .set_series_opts(
                areastyle_opts=opts.AreaStyleOpts(opacity=0.1, color="#ff9900")
            )
        )
    
    if counterparty_col and not df_expense.empty:
        def calc_max_consecutive(group):
            dates = sorted(group['日期'].unique())
            if not dates: return 0
            max_c = 1; curr_c = 1
            for i in range(1, len(dates)):
                if (dates[i] - dates[i-1]).days == 1: curr_c += 1
                else: max_c = max(max_c, curr_c); curr_c = 1
            return max(max_c, curr_c)
        consecutive_stats = df_expense.groupby(counterparty_col).apply(calc_max_consecutive, include_groups=False).sort_values(ascending=True).tail(15)
        bar_consec = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN, width="700px", height="400px"))
            .add_xaxis(consecutive_stats.index.tolist())
            .add_yaxis("最高连续消费天数", consecutive_stats.tolist(), color="#fc8d59")
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="🔍 商户消费频率分析", subtitle="识别高频消费商户"),
                xaxis_opts=opts.AxisOpts(name="天数"),
                toolbox_opts=common_toolbox,
            )
        )
    
    # 将两个图表并排添加
    if line_time and bar_consec:
        page.add(line_time, bar_consec)
    elif line_time:
        page.add(line_time)
    elif bar_consec:
        page.add(bar_consec)


    # 渲染页面
    page.render(output_path)
    
    # 注入自定义样式
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 在 </head> 前插入自定义样式
        html_content = html_content.replace('</head>', f'{custom_css}</head>')
        
        # 添加页面标题
        title_html = '<h1>📊 微信支付账单分析报告</h1>'
        html_content = html_content.replace('<body >', f'<body >{title_html}')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        print(f"  样式注入失败: {e}")
    
    print(f"  可视化报表已生成: {output_path}")
    print(f"  提示: 报表已支持移动端自适应，每个图表右上角可导出为 PNG 图片")
    
    # 生成完整长页面 PNG
    try:
        from screenshot_utils import make_full_page_snapshot
        
        png_path = output_path.replace('.html', '_full_page.png')
        success = make_full_page_snapshot(output_path, png_path, width=1400)
        
        if success:
            print(f"  ✓ 完整长页面 PNG 已导出: {png_path}")
        else:
            print(f"  ✗ PNG 导出失败，请检查 Chrome 浏览器是否已安装")
    except ImportError:
        print(f"  提示: screenshot_utils.py 未找到")
    except Exception as e:
        print(f"  PNG 导出异常: {e}")

