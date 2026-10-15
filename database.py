import sqlite3
import os
import json
import shutil
from datetime import datetime

ORIG_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news.db")

if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    DB_PATH = "/tmp/news.db"
    if not os.path.exists(DB_PATH) and os.path.exists(ORIG_DB_PATH):
        try:
            shutil.copyfile(ORIG_DB_PATH, DB_PATH)
        except Exception:
            DB_PATH = ORIG_DB_PATH
else:
    DB_PATH = ORIG_DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabela de artigos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reddit_id TEXT UNIQUE,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL DEFAULT 'Geral',
        summary TEXT NOT NULL,
        content TEXT NOT NULL,
        cover_image TEXT,
        source_url TEXT,
        reddit_url TEXT,
        buy_url TEXT DEFAULT '',
        deal_price TEXT DEFAULT '',
        deal_discount TEXT DEFAULT '',
        faq_json TEXT DEFAULT '[]',
        seo_keywords TEXT DEFAULT '',
        upvotes INTEGER DEFAULT 0,
        comments_count INTEGER DEFAULT 0,
        author TEXT DEFAULT 'Redação Gamer',
        status TEXT DEFAULT 'published',
        views INTEGER DEFAULT 0,
        published_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Migrações automáticas de colunas se tabela antiga existir
    for col, col_type in [
        ('buy_url', 'TEXT DEFAULT ""'),
        ('deal_price', 'TEXT DEFAULT ""'),
        ('deal_discount', 'TEXT DEFAULT ""'),
        ('faq_json', 'TEXT DEFAULT "[]"'),
        ('seo_keywords', 'TEXT DEFAULT ""')
    ]:
        try:
            cursor.execute(f"ALTER TABLE articles ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass # Coluna já existe
    
    # Tabela de configurações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """)
    
    # Tabela de logs do radar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS radar_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'info'
    )
    """)
    
    # Configurações padrão se não existirem
    default_settings = {
        "autopilot": "true",
        "scan_interval_minutes": "3",
        "ai_provider": "builtin", # builtin, 9router, gemini, openai
        "gemini_api_key": "",
        "openai_api_key": "",
        "reddit_client_id": "",
        "reddit_client_secret": "",
        "min_upvotes": "5"
    }
    
    for key, val in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))
        
    conn.commit()
    conn.close()

def save_article(article_data):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO articles (
            reddit_id, title, slug, category, summary, content,
            cover_image, source_url, reddit_url, buy_url, deal_price,
            deal_discount, faq_json, seo_keywords, upvotes, comments_count,
            author, status, published_at
        ) VALUES (
            :reddit_id, :title, :slug, :category, :summary, :content,
            :cover_image, :source_url, :reddit_url, :buy_url, :deal_price,
            :deal_discount, :faq_json, :seo_keywords, :upvotes, :comments_count,
            :author, :status, :published_at
        )
        """, article_data)
        conn.commit()
        article_id = cursor.lastrowid
        return article_id
    except sqlite3.IntegrityError:
        # Já existe (duplicado)
        return None
    finally:
        conn.close()

def get_articles(category=None, search=None, limit=20, offset=0):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM articles WHERE status = 'published'"
    params = []
    
    if category and category != 'Todos':
        query += " AND category = ?"
        params.append(category)
        
    if search:
        query += " AND (title LIKE ? OR summary LIKE ? OR content LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    query += " ORDER BY published_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_article_by_slug_or_id(identifier):
    conn = get_db()
    cursor = conn.cursor()
    
    if str(identifier).isdigit():
        cursor.execute("SELECT * FROM articles WHERE id = ?", (int(identifier),))
    else:
        cursor.execute("SELECT * FROM articles WHERE slug = ?", (str(identifier),))
        
    row = cursor.fetchone()
    if row:
        # Incrementar views
        cursor.execute("UPDATE articles SET views = views + 1 WHERE id = ?", (row['id'],))
        conn.commit()
        result = dict(row)
        conn.close()
        return result
    conn.close()
    return None

def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM articles")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as today FROM articles WHERE DATE(published_at) = DATE('now')")
    today = cursor.fetchone()['today']
    
    cursor.execute("SELECT SUM(views) as total_views FROM articles")
    views_row = cursor.fetchone()
    total_views = views_row['total_views'] if views_row['total_views'] is not None else 0
    
    conn.close()
    return {"total_articles": total, "today_articles": today, "total_views": total_views}

def log_radar(source, message, status="info"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO radar_logs (source, message, status) VALUES (?, ?, ?)",
        (source, message, status)
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit=30):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM radar_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}

def update_settings(settings_dict):
    conn = get_db()
    cursor = conn.cursor()
    for key, val in settings_dict.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(val)))
    conn.commit()
    conn.close()

init_db()

if __name__ == "__main__":
    print("Banco de dados SQLite inicializado com sucesso!")
