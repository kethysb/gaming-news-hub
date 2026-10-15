import urllib.request
import json

def test_9router():
    url = "http://localhost:20128/v1/chat/completions"
    payload = {
        "model": "gemini/gemini-3-flash-preview",
        "messages": [
            {"role": "user", "content": "Escreva um título chamativo para uma notícia de games sobre o lançamento de GTA VI."}
        ],
        "max_tokens": 100
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print("9Router Response:")
            print(res['choices'][0]['message']['content'])
            return True
    except Exception as e:
        print("9Router off/erro:", e)
        return False

if __name__ == "__main__":
    test_9router()
