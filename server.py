import http.server
import json
import os
import re
import sys
import threading
import time
import urllib.parse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from database import (
    get_articles, get_article_by_slug_or_id, get_stats,
    get_recent_logs, get_settings, update_settings, log_radar
)
from reddit_radar import scan_and_generate

PORT = 28888
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

class GamingNewsHandler(http.server.BaseHTTPRequestHandler):
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

    def serve_static(self, filepath, content_type):
        if not os.path.exists(filepath):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return
        
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        with open(filepath, 'rb') as f:
            self.wfile.write(f.read())

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Rotas estáticas
        if path == "/" or path == "/index.html":
            return self.serve_static(os.path.join(PUBLIC_DIR, "index.html"), "text/html; charset=utf-8")
        elif path.startswith("/public/") or path.endswith(('.css', '.js', '.png', '.svg', '.jpg', '.ico')):
            filename = os.path.basename(path)
            ext = os.path.splitext(filename)[1].lower()
            mime_types = {
                '.css': 'text/css; charset=utf-8',
                '.js': 'application/javascript; charset=utf-8',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon'
            }
            content_type = mime_types.get(ext, 'application/octet-stream')
            return self.serve_static(os.path.join(PUBLIC_DIR, filename), content_type)

        # 2. Rotas da API
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

        # Fallback para SPA / index.html
        return self.serve_static(os.path.join(PUBLIC_DIR, "index.html"), "text/html; charset=utf-8")

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
            # Dispara varredura imediata
            new_count = scan_and_generate()
            return self.send_json({"success": True, "new_articles": new_count, "message": f"{new_count} novos artigos adicionados!"})

        elif path == "/api/settings":
            update_settings(payload)
            return self.send_json({"success": True, "settings": get_settings()})

        self.send_json({"error": "Endpoint não encontrado"}, status=404)

def background_autopilot_worker():
    """Worker em segundo plano para varredura contínua"""
    while True:
        try:
            settings = get_settings()
            autopilot = settings.get('autopilot', 'true').lower() == 'true'
            interval_mins = int(settings.get('scan_interval_minutes', 3))
            
            if autopilot:
                scan_and_generate()
                
            time.sleep(max(60, interval_mins * 60))
        except Exception as e:
            print(f"[Autopilot Error]: {e}")
            time.sleep(60)

def start_server():
    if not os.path.exists(PUBLIC_DIR):
        os.makedirs(PUBLIC_DIR)
        
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), GamingNewsHandler)
    print(f"=====================================================")
    print(f"🚀 NEXUS GAMING NEWS HUB NO AR!")
    print(f"🌐 Acesse no seu navegador: http://localhost:{PORT}")
    print(f"=====================================================")
    
    # Iniciar thread do piloto automático
    worker_thread = threading.Thread(target=background_autopilot_worker, daemon=True)
    worker_thread.start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")

if __name__ == "__main__":
    start_server()
