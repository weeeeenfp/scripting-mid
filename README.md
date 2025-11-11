# 博客來 LLM 書籍管理系統

## 專案描述
本專案為 1141 Scripting 期中考作業，整合 Selenium 爬蟲與 SQLite 資料庫，實現 LLM 相關書籍的自動爬取、儲存與查詢。

## 功能
- 更新資料庫：從博客來爬取 LLM 書籍 (所有分頁)。
- 查詢書籍：依書名或作者模糊查詢。
- CLI 介面：簡單選單操作。

## 安裝
1. `pip install -r requirements.txt`
2. `python app.py`

## 結構
- app.py: 主程式與 UI。
- scraper.py: 爬蟲邏輯。
- database.py: 資料庫操作。
- books.db: 自動生成 (勿手動編輯)。

## 注意
- 參考 Selenium 官方文件 (註解標明)。
- 無抄襲，所有邏輯原創。