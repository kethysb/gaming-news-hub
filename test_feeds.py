import urllib.request
import urllib.parse
import json
import ssl

def test_reddit_public():
    # Reddit public token-less request with standard headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    
    # Test via rss2json or direct
    test_urls = [
        ("Google News Games BR", "https://news.google.com/rss/search?q=jogos+games+when:24h&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
        ("GamerPower Giveaways", "https://www.gamerpower.com/api/giveaways?type=game&sort-by=popularity"),
        ("Steam News (Counter-Strike)", "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=730&count=3"),
        ("Reddit via RSS2JSON", "https://api.rss2json.com/v1/api.json?rss_url=https://www.reddit.com/r/Games/new.rss")
    ]
    
    for name, url in test_urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                print(f"[OK] {name}: Recebido {len(data)} bytes")
                if "api.rss2json" in url or "gamerpower" in url or "steampowered" in url:
                    j = json.loads(data.decode('utf-8'))
                    if "items" in j:
                        print(f"    Item 1: {j['items'][0].get('title')}")
                    elif isinstance(j, list) and len(j) > 0:
                        print(f"    Item 1: {j[0].get('title')}")
                    elif "appnews" in j:
                        print(f"    Item 1: {j['appnews']['newsitems'][0].get('title')}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")

if __name__ == "__main__":
    test_reddit_public()
