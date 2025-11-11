# app.py
"""
主程式：提供完整 CLI 選單，呼叫 scraper.py 與 database.py。
功能：更新資料庫、依書名/作者查詢、離開。
"""

import scraper
import database

def print_header():
    print("\n----- 博客來 LLM 書籍管理系統 -----")
    print("1. 更新書籍資料庫")
    print("2. 查詢書籍")
    print("3. 離開系統")
    print("-" * 35)

def print_query_menu():
    print("\n--- 查詢書籍 ---")
    print("a. 依書名查詢")
    print("b. 依作者查詢")
    print("c. 返回主選單")
    print("-" * 15)

def display_results(books):
    if not books:
        print("查無資料。")
        return
    print("=" * 20)
    for b in books:
        print(f"書名：{b['title']}")
        print(f"作者：{b['author']}")
        print(f"價格：{b['price']}")
        print("---")
    print("=" * 20)

def main():
    while True:
        print_header()
        choice = input("請選擇操作選項 (1-3): ").strip()

        if choice == "1":
            print("開始從網路爬取最新書籍資料...")
            books = scraper.get_books()
            if books:
                new_count = database.insert_books(books)
                print(f"資料庫更新完成！共爬取 {len(books)} 筆資料，新增了 {new_count} 筆新書記錄。")
            else:
                print("爬取失敗，無資料可更新。")

        elif choice == "2":
            while True:
                print_query_menu()
                sub = input("請選擇查詢方式 (a-c): ").strip().lower()
                if sub == "a":
                    kw = input("請輸入關鍵字: ").strip()
                    results = database.query_books("title", kw)
                    display_results(results)
                elif sub == "b":
                    kw = input("請輸入關鍵字: ").strip()
                    results = database.query_books("author", kw)
                    display_results(results)
                elif sub == "c":
                    break
                else:
                    print("無效選項，請重新輸入。")

        elif choice == "3":
            print("感謝使用，系統已退出。")
            break
        else:
            print("無效選項，請重新輸入。")

if __name__ == "__main__":
    main()