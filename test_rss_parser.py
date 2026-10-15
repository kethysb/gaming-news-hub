import urllib.request
import xml.etree.ElementTree as ET
import html
import re
import time

def parse_reddit_rss(subreddit="Games", feed_type="new"):
    url = f"https://www.reddit.com/r/{subreddit}/{feed_type}.rss"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "desktop:com.gamingnewsradar.app:v1.0.0 (by /u/gaming_radar_br)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
            
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else ""
            link_elem = entry.find('atom:link', ns)
            reddit_link = link_elem.attrib.get('href') if link_elem is not None else ""
            entry_id = entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else ""
            updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ""
            author_elem = entry.find('atom:author/atom:name', ns)
            author = author_elem.text if author_elem is not None else ""
            
            content_elem = entry.find('atom:content', ns)
            content_html = content_elem.text if content_elem is not None else ""
            
            # Extrair links externos e thumbnail da descrição html
            external_url = reddit_link
            img_match = re.search(r'<img[^>]+src="([^">]+)"', content_html)
            image_url = img_match.group(1) if img_match else None
            
            # Extrair link real da matéria (se houver)
            link_matches = re.findall(r'<a href="([^"]+)">\[link\]</a>', content_html)
            if link_matches:
                external_url = link_matches[0]
                
            entries.append({
                'id': entry_id,
                'title': html.unescape(title),
                'reddit_url': reddit_link,
                'source_url': external_url,
                'author': author,
                'updated': updated,
                'image_url': image_url
            })
            
        print(f"✅ Coletadas {len(entries)} notícias de r/{subreddit} ({feed_type}):")
        for i, e in enumerate(entries[:3], 1):
            print(f"[{i}] {e['title']}")
            print(f"    🔗 Notícia: {e['source_url']}")
            print(f"    👤 Autor: {e['author']} | 🕒 {e['updated']}")
            if e['image_url']:
                print(f"    🖼️ Imagem: {e['image_url']}")
            print()
        return entries
    except Exception as e:
        print(f"❌ Erro em r/{subreddit}: {e}")
        return []

if __name__ == "__main__":
    parse_reddit_rss("Games", "new")
    time.sleep(1)
    parse_reddit_rss("gaming", "hot")
