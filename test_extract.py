import urllib.request
import json
import ssl

def parse_reddit():
    url = "https://old.reddit.com/r/Games/hot.json?limit=10"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GamingNewsRadar/1.0"}
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        posts = data['data']['children']
        print(f"Total posts coletados: {len(posts)}")
        for idx, p in enumerate(posts[:5], 1):
            d = p['data']
            title = d.get('title')
            score = d.get('score')
            comments = d.get('num_comments')
            url = d.get('url')
            permalink = "https://reddit.com" + d.get('permalink')
            thumbnail = d.get('thumbnail')
            preview_img = None
            if 'preview' in d and 'images' in d['preview'] and len(d['preview']['images']) > 0:
                preview_img = d['preview']['images'][0]['source']['url'].replace('&amp;', '&')
            
            print(f"[{idx}] {title}")
            print(f"    ⭐ Upvotes: {score} | 💬 Comentários: {comments}")
            print(f"    🔗 Link Notícia: {url}")
            print(f"    🖼️ Imagem: {preview_img or thumbnail}")
            print()

if __name__ == "__main__":
    parse_reddit()
