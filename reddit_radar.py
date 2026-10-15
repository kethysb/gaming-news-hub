import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import html
import re
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from database import get_db, save_article, log_radar, get_settings
from ai_generator import create_full_article

def fetch_rss2json_reddit(subreddit="Games", feed="new"):
    """Puxa notícias do Reddit via conversor JSON"""
    rss_url = f"https://www.reddit.com/r/{subreddit}/{feed}.rss"
    encoded_url = urllib.parse.quote(rss_url, safe='')
    url = f"https://api.rss2json.com/v1/api.json?rss_url={encoded_url}"
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data.get('items', [])
            results = []
            for item in items:
                title = item.get('title', '').strip()
                guid = item.get('guid', '')
                link = item.get('link', '')
                author = item.get('author', 'Reddit Gamer')
                content = item.get('content', '') or item.get('description', '')
                
                # Extrair link da fonte real
                source_url = link
                link_match = re.search(r'<a href="([^"]+)">\[link\]</a>', content)
                if link_match:
                    source_url = link_match.group(1)
                    
                # Extrair imagem
                image_url = None
                img_match = re.search(r'<img[^>]+src="([^">]+)"', content)
                if img_match:
                    image_url = img_match.group(1)
                elif item.get('thumbnail'):
                    image_url = item.get('thumbnail')
                    
                results.append({
                    "id": f"reddit_{guid.split('/')[-1] if '/' in guid else guid}",
                    "title": html.unescape(title),
                    "reddit_url": link,
                    "source_url": source_url,
                    "author": author,
                    "image_url": image_url,
                    "upvotes": 45,
                    "comments_count": 12
                })
            return results
    except Exception as e:
        log_radar(f"Reddit r/{subreddit}", f"Erro ao consultar: {str(e)[:100]}", "error")
        return []

def fetch_gamerpower_giveaways():
    """Puxa jogos grátis e promoções que viralizam"""
    url = "https://www.gamerpower.com/api/giveaways?type=game&sort-by=popularity"
    req = urllib.request.Request(url, headers={"User-Agent": "GamingNewsHub/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = []
            for item in data[:6]:
                results.append({
                    "id": f"gamerpower_{item.get('id')}",
                    "title": f"JOGO GRÁTIS: {item.get('title')} liberado para resgate ({item.get('platforms')})",
                    "reddit_url": item.get('gamerpower_url', ''),
                    "source_url": item.get('open_giveaway_url', ''),
                    "author": "GamerPower Promoções",
                    "image_url": item.get('image'),
                    "upvotes": int(item.get('users', 100)),
                    "comments_count": 25
                })
            return results
    except Exception as e:
        log_radar("GamerPower", f"Erro ao consultar: {str(e)[:100]}", "warning")
        return []

def scan_and_generate():
    """
    Varre todas as fontes, identifica novidades e gera novos artigos de blog automaticamente.
    """
    settings = get_settings()
    log_radar("Radar Geral", "Iniciando varredura em tempo real no Reddit e portais de games...", "info")
    
    # Coletar itens de várias fontes
    all_raw_items = []
    
    # 1. Reddit /r/Games
    reddit_games = fetch_rss2json_reddit("Games", "new")
    all_raw_items.extend(reddit_games)
    
    # 2. Reddit /r/gaming
    time.sleep(0.5)
    reddit_gaming = fetch_rss2json_reddit("gaming", "hot")
    all_raw_items.extend(reddit_gaming)
    
    # 3. GamerPower (Jogos grátis virais)
    giveaways = fetch_gamerpower_giveaways()
    all_raw_items.extend(giveaways)
    
    if not all_raw_items:
        log_radar("Radar Geral", "Nenhuma novidade encontrada nas fontes.", "warning")
        return 0
        
    # Verificar quais já foram cadastrados no banco
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT reddit_id FROM articles")
    existing_ids = set(row['reddit_id'] for row in cursor.fetchall())
    conn.close()
    
    new_articles_count = 0
    
    for raw in all_raw_items:
        raw_id = raw.get('id')
        if not raw_id or raw_id in existing_ids:
            continue # Já temos no blog
            
        try:
            # Gerar artigo completo via IA / Editorial
            article_data = create_full_article(raw, settings)
            saved_id = save_article(article_data)
            
            if saved_id:
                existing_ids.add(raw_id)
                new_articles_count += 1
                log_radar("Novo Artigo", f"Publicado: '{article_data['title'][:60]}...' ({article_data['category']})", "success")
        except Exception as e:
            log_radar("Gerador IA", f"Erro ao processar post: {str(e)[:100]}", "error")
            
    log_radar("Radar Geral", f"Varredura concluída! {new_articles_count} novos artigos gerados e publicados.", "info")
    return new_articles_count

if __name__ == "__main__":
    print("Testando varredura do radar...")
    count = scan_and_generate()
    print(f"Varredura finalizada. Novos artigos: {count}")
