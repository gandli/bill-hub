"""
自定义截图脚本，支持完整长页面导出
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def make_full_page_snapshot(html_path, png_path, width=1200):
    """
    生成完整长页面截图
    
    Args:
        html_path: HTML 文件路径
        png_path: 输出 PNG 路径
        width: 页面宽度（默认 1200px）
    """
    # 配置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'--window-size={width},1080')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--hide-scrollbars')
    
    driver = None
    try:
        # 启动浏览器
        driver = webdriver.Chrome(options=chrome_options)
        
        # 加载 HTML 文件
        file_url = f'file://{os.path.abspath(html_path)}'
        driver.get(file_url)
        
        # 等待页面加载完成（等待图表渲染）
        time.sleep(3)
        
        # 获取完整页面高度
        total_height = driver.execute_script("""
            return Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.clientHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            );
        """)
        
        # 设置窗口大小为完整页面尺寸
        driver.set_window_size(width, total_height)
        
        # 再次等待确保渲染完成
        time.sleep(2)
        
        # 截取完整页面
        driver.save_screenshot(png_path)
        
        return True
        
    except Exception as e:
        print(f"  截图失败: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
