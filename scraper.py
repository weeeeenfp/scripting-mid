#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客來 LLM 書籍爬蟲模組
參考: Selenium 官方文件[](https://selenium-python.readthedocs.io/)
作者: [Your Name]
日期: 2025-11-12
"""

from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import time


def scrape_books() -> List[Dict[str, str]]:
    """
    爬取博客來 LLM 書籍資料 (所有分頁)

    Returns:
        List[Dict[str, str]]: 書籍列表，每筆包含 title, author, price, link
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    books: List[Dict[str, str]] = []
    current_url = "https://search.books.com.tw/search/query/key/LLM/cat/BKA"  # 預設圖書分類

    try:
        driver.get("https://www.books.com.tw/")
        time.sleep(2)

        # 輸入關鍵字並送出
        search_box = wait.until(EC.presence_of_element_located((By.ID, "keyword")))
        search_box.clear()
        search_box.send_keys("LLM")
        search_box.submit()
        time.sleep(2)

        # 勾選圖書分類 (點擊圖書選項)
        book_cat = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), '圖書')]")))
        book_cat.click()
        time.sleep(2)

        # 現在 URL 應為分類後的，開始爬取
        driver.get(current_url) if current_url else None
        time.sleep(3)

        while True:
            # 等待書籍列表載入
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "table-searchbox")))

            # 爬取當前頁書籍
            book_items = driver.find_elements(By.CLASS_NAME, "table-td")
            for item in book_items:
                try:
                    # 書名與連結
                    title_elem = item.find_element(By.TAG_NAME, "h4")
                    title_link = title_elem.find_element(By.TAG_NAME, "a")
                    title = title_link.text.strip()
                    link = title_link.get_attribute("href")

                    # 作者 (多位合併)
                    author_elems = item.find_elements(By.XPATH, ".//p[@class='author']//a")
                    authors = [a.text.strip() for a in author_elems if a.text.strip()]
                    author = ", ".join(authors) if authors else "N/A"

                    # 價格清理 (提取數字)
                    price_text = item.find_element(By.XPATH, ".//b[contains(text(), '元')]").text
                    price_match = re.search(r'(\d+)', price_text)
                    price = int(price_match.group(1)) if price_match else 0

                    books.append({
                        "title": title,
                        "author": author,
                        "price": str(price),  # 轉 str 給 DB
                        "link": link
                    })
                except (NoSuchElementException, ValueError):
                    continue  # 跳過缺失資料

            print(f"正在爬取第 {len(books) // 30 + 1} 頁...")  # 粗估頁數 (每頁 ~30 本)

            # 下一頁處理
            try:
                next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'next')]")))
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3)
            except TimeoutException:
                print("偵測到總共有 X 頁。")  # 可替換為實際頁數邏輯
                break

    except Exception as e:
        print(f"爬蟲錯誤: {e}")
    finally:
        driver.quit()

    return books