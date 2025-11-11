#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博客來 LLM 書籍管理系統 - 主程式
作者: [Your Name]
日期: 2025-11-12
"""

import sys
from typing import List, Dict
from scraper import scrape_books
from database import init_db, insert_books, query_books_by_title, query_books_by_author


def print_menu() -> None:
    """印出主選單"""
    print("\n----- 博客來 LLM 書籍管理系統 -----")
    print("1. 更新書籍資料庫")
    print("2. 查詢書籍")
    print("3. 離開系統")
    print("---------------------------------")


def print_query_menu() -> None:
    """印出查詢子選單"""
    print("\n--- 查詢書籍 ---")
    print("a. 依書名查詢")
    print("b. 依作者查詢")
    print("c. 返回主選單")
    print("---------------")


def main() -> None:
    """主程式進入點"""
    try:
        init_db()  # 初始化資料庫
    except Exception as e:
        print(f"初始化資料庫失敗: {e}")
        sys.exit(1)

    while True:
        print_menu()
        choice = input("請選擇操作選項 (1-3): ").strip()

        if choice == "1":
            # 更新資料庫
            print("開始從網路爬取最新書籍資料...")
            try:
                books: List[Dict[str, str]] = scrape_books()
                if not books:
                    print("無資料爬取。")
                    continue
                count = insert_books(books)
                print(f"爬取完成。資料庫更新完成！共爬取 {len(books)} 筆資料，新增了 {count} 筆新書記錄。")
            except Exception as e:
                print(f"更新資料庫失敗: {e}")

        elif choice == "2":
            # 查詢書籍
            while True:
                print_query_menu()
                q_choice = input("請選擇查詢方式 (a-c): ").strip().lower()

                if q_choice == "a":
                    keyword = input("請輸入關鍵字: ").strip()
                    results = query_books_by_title(keyword)
                    display_results(results, "書名")
                elif q_choice == "b":
                    keyword = input("請輸入關鍵字: ").strip()
                    results = query_books_by_author(keyword)
                    display_results(results, "作者")
                elif q_choice == "c":
                    break
                else:
                    print("無效選項，請重新輸入。")

        elif choice == "3":
            print("感謝使用，系統已退出。")
            sys.exit(0)

        else:
            print("無效選項，請重新輸入。")


def display_results(results: List[Dict[str, str]], query_type: str) -> None:
    """顯示查詢結果"""
    if not results:
        print("查無資料。")
        return

    print(f"====================")
    for row in results:
        author_str = row["author"] if row["author"] != "N/A" else "N/A"
        print(f"書名：{row['title']}")
        print(f"作者：{author_str}")
        print(f"價格：{row['price']}")
        print("---")
    print("====================")


if __name__ == "__main__":
    main()