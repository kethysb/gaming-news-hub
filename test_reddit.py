import urllib.request
import json
import ssl

def test_endpoints():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "desktop:gaming-radar-bot:v1.0 (by /u/anonymous_gamer)",
        "curl/8.4.0",
        "GamingNewsHub/1.0"
    ]
    urls = [
        "https://www.reddit.com/r/Games/hot.json?limit=3",
        "https://old.reddit.com/r/Games/new.json?limit=3",
        "https://www.reddit.com/r/gaming/top.json?t=day&limit=3",
        "https://www.reddit.com/r/Games/new.rss"
    ]
    
    ctx = ssl.create_default_context()
    for ua in user_agents:
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": ua})
                with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                    content = resp.read().decode('utf-8', errors='ignore')
                    print(f"[OK] UA: {ua[:25]}... | URL: {url} | Resp length: {len(content)}")
                    if ".json" in url:
                        data = json.loads(content)
                        posts = data.get('data', {}).get('children', [])
                        if posts:
                            print(f" -> Post 1: {posts[0]['data']['title']} ({posts[0]['data']['score']} upvotes)")
                    break
            except Exception as e:
                # print(f"[FAIL] UA: {ua[:25]}... | URL: {url} | Erro: {e}")
                pass

if __name__ == "__main__":
    test_endpoints()
