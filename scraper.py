# scraper.py
"""
爬蟲模組：使用 Selenium 自動爬取博客來「LLM」搜尋結果的所有書籍資料。
支援多分頁、資料清理、錯誤處理、headless 模式。
"""

import re
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)

def get_books() -> List[Dict[str, Optional[str | int]]]:
    """
    爬取博客來「LLM」搜尋結果的所有書籍資料（多分頁）。

    Returns:
        List[Dict[str, Optional[str | int]]]: 書籍列表，包含 title, author, price, link。
    """
    books: List[Dict[str, Optional[str | int]]] = []

    # 設定 Chrome 無頭模式
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)

        print("正在開啟博客來首頁...")
        driver.get("https://www.books.com.tw/")

        # 步驟 1：搜尋 LLM
        print("輸入搜尋關鍵字：LLM")
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "query")))
        search_box.clear()
        search_box.send_keys("LLM")
        search_box.send_keys(Keys.RETURN)

        # 步驟 2：勾選「圖書」分類
        print("勾選「圖書」分類...")
        book_category = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='BKA']"))
        )
        driver.execute_script("arguments[0].click();", book_category)

        # 等待搜尋結果載入
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-searchbox")))

        page = 1
        while True:
            print(f"正在爬取第 {page} 頁...")
            items = driver.find_elements(By.CSS_SELECTOR, "div.table-td")
            if not items:
                print("本頁無資料，跳出。")
                break

            for item in items:
                try:
                    # 書名 & 連結
                    title_tag = item.find_element(By.CSS_SELECTOR, "h4 a")
                    title = title_tag.text.strip()
                    link = title_tag.get_attribute("href")

                    # 作者（可能多位）
                    author_tags = item.find_elements(By.CSS_SELECTOR, "p.author a")
                    author = ", ".join([a.text.strip() for a in author_tags]) if author_tags else "N/A"

                    # 價格清理
                    price_text = item.find_element(By.CSS_SELECTOR, "ul.price strong b").text
                    price_match = re.search(r'\d+', price_text)
                    price = int(price_match.group()) if price_match else 0

                    books.append({
                        "title": title,
                        "author": author,
                        "price": price,
                        "link": link
                    })
                except NoSuchElementException:
                    continue  # 跳過資料不完整的書籍

            # 下一頁
            try:
                next_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                next_btn.click()
                wait.until(EC.staleness_of(next_btn))
                page += 1
            except TimeoutException:
                print("已達最後一頁。")
                break

        print(f"爬取完成，共取得 {len(books)} 筆資料。")

    except WebDriverException as e:
        print(f"瀏覽器啟動失敗：{e}")
    except Exception as e:
        print(f"爬取過程中發生錯誤：{e}")
    finally:
        if driver:
            driver.quit()

    return books