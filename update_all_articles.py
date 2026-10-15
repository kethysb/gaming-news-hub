import sqlite3
import json
import re
from database import get_db
from ai_generator import fallback_generate_article, DEFAULT_GAMING_IMAGES

def upgrade_existing_articles():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles")
    rows = cursor.fetchall()
    
    updated_count = 0
    for row in rows:
        raw_item = {
            "title": row['title'],
            "source_url": row['source_url'],
            "reddit_url": row['reddit_url'],
            "author": row['author'],
            "image_url": row['cover_image']
        }
        gen = fallback_generate_article(raw_item)
        
        cursor.execute("""
        UPDATE articles SET
            summary = ?,
            content = ?,
            buy_url = ?,
            deal_price = ?,
            deal_discount = ?,
            faq_json = ?,
            seo_keywords = ?
        WHERE id = ?
        """, (
            gen['summary'],
            gen['content'],
            gen['buy_url'],
            gen['deal_price'],
            gen['deal_discount'],
            gen['faq_json'],
            gen['seo_keywords'],
            row['id']
        ))
        updated_count += 1
        
    conn.commit()
    conn.close()
    print(f"Sucesso! {updated_count} artigos existentes foram atualizados com SEO Avançado e Caixas de Compra.")

if __name__ == "__main__":
    upgrade_existing_articles()
