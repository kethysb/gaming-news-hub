import os
import sys
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler

# Adicionar pasta raiz ao path para importar database, reddit_radar, etc.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database import (
    get_articles, get_article_by_slug_or_id, get_stats,
    get_recent_logs, get_settings, update_settings
)
from reddit_radar import scan_and_generate

class handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/articles":
            category = query.get('category', [None])[0]
            search = query.get('search', [None])[0]
            limit = int(query.get('limit', [24])[0])
            offset = int(query.get('offset', [0])[0])
            articles = get_articles(category=category, search=search, limit=limit, offset=offset)
            return self.send_json({"articles": articles, "count": len(articles)})

        elif path.startswith("/api/articles/"):
            slug_or_id = path.replace("/api/articles/", "").strip()
            article = get_article_by_slug_or_id(slug_or_id)
            if article:
                return self.send_json(article)
            return self.send_json({"error": "Artigo não encontrado"}, status=404)

        elif path == "/api/stats":
            return self.send_json(get_stats())

        elif path == "/api/logs":
            return self.send_json({"logs": get_recent_logs()})

        elif path == "/api/settings":
            return self.send_json(get_settings())

        return self.send_json({"error": "Endpoint não encontrado"}, status=404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if path == "/api/radar/scan":
            new_count = scan_and_generate()
            return self.send_json({"success": True, "new_articles": new_count, "message": f"{new_count} novos artigos adicionados!"})

        elif path == "/api/settings":
            update_settings(payload)
            return self.send_json({"success": True, "settings": get_settings()})

        self.send_json({"error": "Endpoint não encontrado"}, status=404)
