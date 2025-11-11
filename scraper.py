# scraper.py
"""
期中考爬蟲模組：爬取博客來「LLM」搜尋結果的所有書籍資料（多分頁）
使用 Selenium + ChromeDriver + headless=new
"""

import re
import os
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_books() -> List[Dict[str, Optional[str | int]]]:
    """
    爬取博客來「LLM」搜尋結果的所有書籍資料（多分頁）。

    Returns:
        List[Dict]: 每本書包含 title, author, price, link
    """
    books: List[Dict[str, Optional[str | int]]] = []

    # === 1. 設定 Chrome 選項（headless=new 必須）===
    options = Options()
    #創建一個Chrome options的物件​
    options.add_argument("--disable-notifications")
    options.add_argument("--headless=new")        # 關鍵！Chrome 142 必須
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    # === 2. 指定本地 chromedriver.exe ===
    driver_path = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
    if not os.path.exists(driver_path):
        print(f"[錯誤] 找不到 chromedriver.exe！請放在：{driver_path}")
        return []

    service = Service(executable_path=driver_path)
    try:
        print("正在啟動 Chrome 瀏覽器...")
        browser = webdriver.Chrome()  # 啟動 Chrome webdriver
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 30)
        # === 3. 開啟博客來首頁 ===
        print("正在開啟 https://www.books.com.tw/")
        browser.get('https://www.books.com.tw/')
        #print(f"網頁標題：{driver.title}")
        time.sleep(2)  # 等待 DOM 載入
        browser.execute_script("""
            const openBtn = document.querySelector('a.open[title="展開廣告"]');
            if (openBtn) {
            openBtn.remove();
            console.log('廣告按鈕已移除');
            }
            // 額外防禦：移除所有廣告相關元素
            document.querySelectorAll('div, iframe').forEach(el => {
                const style = w                                                                                             indow.getComputedStyle(el);
                if (style.position === 'fixed' || style.zIndex > 1000) {
                    el.remove();
                }
            });
        """)
        
        # === 4. 找到搜尋框並輸入「LLM」===
        print("正在搜尋「LLM」...")
        qelement = browser.find_element(By.NAME, "q")  # 找到 name = q 的標籤(即輸入框)
        qelement.send_keys("LLM")  # 輸入關鍵字
        qelement.submit()  # 送出
        #search_box = wait.until(EC.presence_of_element_located((By.NAME, "query")))
        #search_box.clear()
        #search_box.send_keys("LLM")
        #search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        # === 5. 勾選「圖書」分類 ===
        print("正在勾選「圖書」分類...")
        book_label = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='BKA']")))
        browser.execute_script("arguments[0].click();", book_label)

        # 等待結果出現
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-td")))
        print("搜尋結果載入完成")

        # === 6. 開始分頁爬取 ===
        page = 1
        while True:
            print(f"正在爬取第 {page} 頁...")
            items = driver.find_elements(By.CSS_SELECTOR, "div.table-td")
            if not items:
                print("本頁無資料，停止爬取")
                break

            for item in items:
                try:
                    # 書名 + 連結
                    title_tag = item.find_element(By.CSS_SELECTOR, "h4 a")
                    title = title_tag.text.strip()
                    link = title_tag.get_attribute("href")

                    # 作者
                    author_tags = item.find_elements(By.CSS_SELECTOR, "p.author a")
                    author = ", ".join([a.text.strip() for a in author_tags]) if author_tags else "N/A"

                    # 價格（用正規表達式清理）
                    price_text = item.find_element(By.CSS_SELECTOR, "ul.price strong b").text
                    price_match = re.search(r'\d+', price_text)
                    price = int(price_match.group()) if price_match else 0

                    books.append({
                        "title": title,
                        "author": author,
                        "price": price,
                        "link": link
                    })
                except Exception as e:
                    continue  # 跳過有問題的項目

            # === 7. 點擊下一頁 ===
            try:
                next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']")))
                driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                next_btn.click()
                wait.until(EC.staleness_of(next_btn))  # 等待頁面更新
                page += 1
                time.sleep(1)
            except TimeoutException:
                print("已達最後一頁")
                break

        print(f"爬取完成！共取得 {len(books)} 筆資料")

    except Exception as e:
        print(f"爬蟲過程中發生錯誤：{e}")
    finally:
        if driver:
            print("正在關閉瀏覽器...")
            driver.quit()

    return books