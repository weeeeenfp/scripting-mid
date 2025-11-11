# database.py
"""
資料庫模組：負責建立 books.db、資料表 llm_books，並提供插入與模糊查詢功能。
使用 INSERT OR IGNORE 避免重複，啟用 Row factory。
"""

import sqlite3
from typing import List, Dict, Any

DB_FILE = "books.db"

def _get_connection():
    """建立並回傳啟用 Row factory 的資料庫連線。"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """建立資料表（若不存在）。"""
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                author TEXT,
                price INTEGER,
                link TEXT
            )
        """)
        conn.commit()

def insert_books(books: List[Dict[str, Any]]) -> int:
    """
    批量插入書籍，使用 INSERT OR IGNORE。

    Args:
        books: 書籍列表

    Returns:
        int: 新增的筆數
    """
    init_db()
    inserted = 0
    with _get_connection() as conn:
        cursor = conn.cursor()
        for book in books:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO llm_books (title, author, price, link)
                    VALUES (?, ?, ?, ?)
                """, (book["title"], book["author"], book["price"], book["link"]))
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.Error as e:
                print(f"插入失敗（{book['title']}）：{e}")
        conn.commit()
    return inserted

def query_books(field: str, keyword: str) -> List[Dict[str, Any]]:
    """
    模糊查詢（LIKE '%keyword%'）。

    Args:
        field: 'title' 或 'author'
        keyword: 搜尋關鍵字

    Returns:
        List[Dict]: 查詢結果
    """
    init_db()
    results = []
    with _get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT title, author, price FROM llm_books
                WHERE {field} LIKE ?
                ORDER BY price
            """, (f"%{keyword}%",))
            for row in cursor.fetchall():
                results.append({
                    "title": row["title"],
                    "author": row["author"],
                    "price": row["price"]
                })
        except sqlite3.Error as e:
            print(f"查詢失敗：{e}")
    return results