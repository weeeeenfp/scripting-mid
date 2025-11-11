#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 資料庫管理模組
作者: [Your Name]
日期: 2025-11-12
"""

import sqlite3
from typing import List, Dict, Any
from contextlib import contextmanager


DB_FILE = "books.db"


@contextmanager
def get_db_connection():
    """資料庫連線上下文管理器"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 啟用 Row factory
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """初始化資料庫與資料表"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                author TEXT,
                price INTEGER,
                link TEXT
            )
        """)
        conn.commit()


def insert_books(books: List[Dict[str, str]]) -> int:
    """
    批量插入書籍 (使用 INSERT OR IGNORE 避免重複)

    Args:
        books: 書籍列表

    Returns:
        int: 新增筆數
    """
    new_count = 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for book in books:
            cursor.execute("""
                INSERT OR IGNORE INTO llm_books (title, author, price, link)
                VALUES (?, ?, ?, ?)
            """, (book["title"], book["author"], int(book["price"]), book["link"]))
            if cursor.rowcount > 0:
                new_count += 1
        conn.commit()
    return new_count


def query_books_by_title(keyword: str) -> List[Dict[str, Any]]:
    """依書名模糊查詢"""
    return _query_books("title", keyword)


def query_books_by_author(keyword: str) -> List[Dict[str, Any]]:
    """依作者模糊查詢"""
    return _query_books("author", keyword)


def _query_books(column: str, keyword: str) -> List[Dict[str, Any]]:
    """通用查詢函式 (LIKE '%keyword%')"""
    results = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT title, author, price FROM llm_books
            WHERE {column} LIKE ?
        """, (f"%{keyword}%",))
        for row in cursor.fetchall():
            results.append(dict(row))
    return results