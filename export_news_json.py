import json
from database import get_articles, get_stats

def export_json():
    articles = get_articles(limit=100)
    stats = get_stats()
    
    with open("public/news.json", "w", encoding="utf-8") as f:
        json.dump({"articles": articles, "stats": stats, "count": len(articles)}, f, ensure_ascii=False, indent=2)
    print(f"Exportados {len(articles)} artigos para public/news.json com sucesso!")

if __name__ == "__main__":
    export_json()
