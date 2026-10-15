import urllib.request
import json
import ssl

def check_resp():
    url = "https://www.reddit.com/r/Games/new.rss"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        print("Status RSS:", resp.status)
        print("Content-Type RSS:", resp.headers.get('Content-Type'))
        raw = resp.read()
        print("Length RSS:", len(raw))

    url_json = "https://old.reddit.com/r/Games/hot.json?limit=5"
    req_json = urllib.request.Request(url_json, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"})
    with urllib.request.urlopen(req_json, context=ctx, timeout=10) as resp:
        print("Status JSON:", resp.status)
        print("Content-Type JSON:", resp.headers.get('Content-Type'))
        raw_json = resp.read().decode('utf-8', errors='ignore')
        print("Length JSON:", len(raw_json))
        print("Preview JSON:", raw_json[:200])

if __name__ == "__main__":
    check_resp()
