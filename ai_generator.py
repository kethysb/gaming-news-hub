import re
import json
import urllib.request
import urllib.parse
from datetime import datetime
import unicodedata

DEFAULT_GAMING_IMAGES = {
    "PlayStation": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=1200&q=80",
    "Xbox": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?auto=format&fit=crop&w=1200&q=80",
    "PC Gaming": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=1200&q=80",
    "Nintendo": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&w=1200&q=80",
    "Promoções": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80",
    "Lançamentos": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?auto=format&fit=crop&w=1200&q=80",
    "Vazamentos": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80",
    "Geral": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1200&q=80"
}

def generate_slug(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    timestamp = datetime.now().strftime("%m%d%H%M")
    return f"{text[:60]}-{timestamp}"

def detect_category(title, original_cat="Geral"):
    title_lower = title.lower()
    if any(w in title_lower for w in ['playstation', 'ps5', 'ps4', 'sony', 'dualshock', 'dualsense']):
        return 'PlayStation'
    if any(w in title_lower for w in ['xbox', 'game pass', 'microsoft', 'series x', 'series s']):
        return 'Xbox'
    if any(w in title_lower for w in ['nintendo', 'switch', 'mario', 'zelda', 'pokemon']):
        return 'Nintendo'
    if any(w in title_lower for w in ['steam', 'pc', 'rtx', 'gpu', 'nvidia', 'amd', 'epic games', 'valve']):
        return 'PC Gaming'
    if any(w in title_lower for w in ['free', 'grátis', 'gratis', 'giveaway', 'desconto', 'promoção', 'promocao']):
        return 'Promoções'
    if any(w in title_lower for w in ['leak', 'rumor', 'vazamento', 'vaza', 'insider']):
        return 'Vazamentos'
    if any(w in title_lower for w in ['trailer', 'anúncio', 'anuncio', 'reveal', 'lançamento', 'release date']):
        return 'Lançamentos'
    return original_cat if original_cat in DEFAULT_GAMING_IMAGES else 'Geral'

_ROUTER_AVAILABLE = None

def check_9router_alive():
    global _ROUTER_AVAILABLE
    if _ROUTER_AVAILABLE is not None:
        return _ROUTER_AVAILABLE
    try:
        req = urllib.request.Request("http://localhost:20128/v1/models")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            _ROUTER_AVAILABLE = (resp.status == 200)
    except Exception:
        _ROUTER_AVAILABLE = False
    return _ROUTER_AVAILABLE

def call_llm(prompt, settings):
    provider = settings.get('ai_provider', 'builtin')
    
    # 1. 9Router Local
    if provider in ['9router', 'builtin'] and check_9router_alive():
        try:
            url = "http://localhost:20128/v1/chat/completions"
            payload = {
                "model": "gemini/gemini-3-flash-preview",
                "messages": [
                    {"role": "system", "content": "Você é um especialista em SEO para Games e Redator Chefe de um grande portal de e-commerce e notícias de games no Brasil. Responda em JSON estrito."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                content = data['choices'][0]['message']['content']
                return json.loads(content)
        except Exception:
            pass

    # 2. Gemini API Oficial
    gemini_key = settings.get('gemini_api_key')
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt + "\nResponda em formato JSON válido."}]}]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                text_resp = data['candidates'][0]['content']['parts'][0]['text']
                text_clean = re.sub(r'```(?:json)?\n|\n```', '', text_resp.strip())
                return json.loads(text_clean)
        except Exception:
            pass

    return None

def fallback_generate_article(raw_item):
    """
    Gerador autônomo com máxima otimização SEO e Caixa de Compra / Conversão.
    """
    raw_title = raw_item.get('title', '')
    source_url = raw_item.get('source_url', '')
    reddit_url = raw_item.get('reddit_url', '')
    author = raw_item.get('author', 'Comunidade Gamer')
    category = detect_category(raw_title)
    
    clean_title = re.sub(r'\[.*?\]|\(.*?\)', '', raw_title).strip()
    
    # Extrair possível nome do jogo
    game_keywords = ["Warhammer", "Xbox", "PlayStation", "Nintendo", "GTA", "Final Fantasy", "Zelda", "Fortnite", "Call of Duty", "Cyberpunk", "Resident Evil", "Elden Ring"]
    game_name = clean_title.split(':')[0] if ':' in clean_title else clean_title[:40]
    for kw in game_keywords:
        if kw.lower() in clean_title.lower():
            game_name = kw
            break
            
    summary = (
        f"Confira todos os detalhes, análises e onde garantir {clean_title} com o melhor preço e ofertas exclusivas no Brasil. "
        f"Veja a repercussão completa e os pontos mais importantes para os jogadores."
    )
    
    key_points = [
        f"Destaque principal no universo {category}.",
        "Repercussão massiva com milhares de jogadores debatendo o lançamento.",
        "Ofertas e disponibilidade oficial para compra digital e física.",
        f"Tópico apurado diretamente via canais oficiais e comunidade ({author})."
    ]
    
    faq_items = [
        {
            "question": f"Quando {game_name} está disponível e em quais plataformas?",
            "answer": f"O título e suas novidades atendem aos jogadores das plataformas principais ({category} e consoles de nova geração), com atualizações e suporte contínuo."
        },
        {
            "question": f"Onde comprar {game_name} com o melhor preço e garantia?",
            "answer": f"Você pode adquirir o jogo diretamente pelas lojas oficiais digitais e revendedores parceiros com descontos exclusivos e ativação imediata no botão de compra ao final desta matéria."
        },
        {
            "question": f"Vale a pena comprar {game_name} hoje?",
            "answer": "Sim! A recepção da comunidade e as novas melhorias trazem uma excelente relação custo-benefício para quem busca novas experiências e gameplay de alta qualidade."
        }
    ]
    
    deal_price = "R$ 149,90" if category != "Promoções" else "100% GRÁTIS"
    deal_discount = "-40% OFF" if category != "Promoções" else "POR TEMPO LIMITADO"
    buy_url = source_url if source_url else (reddit_url if reddit_url else "https://store.steampowered.com")
    
    content_html = f"""
    <p class="lead text-lg font-medium text-slate-200 mb-6 leading-relaxed">
        Uma grande novidade acaba de agitar o mercado de <strong>{category}</strong>: <em>{clean_title}</em> está entre os assuntos mais buscados e comentados pelos jogadores neste momento.
    </p>

    <!-- Caixa de Destaque / Resumo Rápido SEO -->
    <div class="my-6 p-5 rounded-2xl bg-gradient-to-r from-indigo-950/60 to-purple-950/40 border border-indigo-500/30 shadow-lg">
        <h3 class="text-base font-bold text-indigo-300 mb-3 flex items-center gap-2">
            ⚡ Resumo da Notícia em 1 Minuto:
        </h3>
        <ul class="space-y-2 text-slate-300 text-sm list-disc list-inside">
            {''.join([f'<li>{kp}</li>' for kp in key_points])}
        </ul>
    </div>

    <h2 class="text-2xl font-bold text-white mt-8 mb-4 border-l-4 border-indigo-500 pl-3">Tudo Sobre {clean_title}</h2>
    <p class="text-slate-300 leading-relaxed mb-4">
        Os anúncios e relatos em torno de <strong>{clean_title}</strong> geraram grande expectativa entre fãs e criadores de conteúdo. 
        Com gráficos aprimorados, mecânicas refinadas e alto engajamento da comunidade, o título se consolida como uma das recomendações mais fortes da temporada.
    </p>

    <h2 class="text-2xl font-bold text-white mt-8 mb-4 border-l-4 border-indigo-500 pl-3">Análise de Desempenho & Comunidade</h2>
    <p class="text-slate-300 leading-relaxed mb-4">
        As primeiras impressões dos jogadores reforçam a evolução na jogabilidade e a estabilidade das atualizações recentes.
        O feedback espontâneo nos maiores fóruns mundiais como o Reddit destaca o cuidado dos desenvolvedores em atender aos pedidos da comunidade.
    </p>

    <blockquote class="my-6 p-4 border-l-4 border-purple-500 bg-purple-950/30 rounded-r-xl italic text-slate-200 shadow-inner">
        "A movimentação em torno de {game_name} mostra como títulos bem otimizados e com suporte contínuo conquistam rapidamente o topo das vendas e a preferência dos jogadores."
    </blockquote>

    <!-- SEÇÃO DE FAQ ESTRUTURADA (SCHEMA.ORG RICH SNIPPET GOOGLE) -->
    <h2 class="text-2xl font-bold text-white mt-10 mb-4 border-l-4 border-indigo-500 pl-3">Perguntas Frequentes (FAQ)</h2>
    <div class="space-y-3 my-6">
        {''.join([f'''
        <div class="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
            <h4 class="font-bold text-white text-base mb-1.5 flex items-center gap-2">
                <i class="fa-solid fa-circle-question text-indigo-400 text-sm"></i> {faq["question"]}
            </h4>
            <p class="text-slate-300 text-sm leading-relaxed">{faq["answer"]}</p>
        </div>
        ''' for faq in faq_items])}
    </div>

    <!-- 🛒 CAIXA DE COMPRA / ALTA CONVERSÃO DE VENDAS -->
    <div class="my-10 p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-indigo-900/80 via-purple-950/90 to-slate-900 border-2 border-indigo-500/50 shadow-2xl relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 relative z-10">
            <div>
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-xs font-bold uppercase tracking-wider mb-3">
                    <i class="fa-solid fa-tag"></i> {deal_discount}
                </div>
                <h3 class="text-xl sm:text-2xl font-bold text-white font-['Space_Grotesk'] mb-1">
                    Garantir {game_name} com Oferta Especial
                </h3>
                <p class="text-slate-300 text-xs sm:text-sm">
                    Ativação Digital Instantânea • Garantia Oficial • Menor Preço do Dia
                </p>
            </div>

            <div class="flex flex-col sm:items-end gap-2 w-full sm:w-auto">
                <div class="text-2xl sm:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                    {deal_price}
                </div>
                <a href="{buy_url}" target="_blank" rel="noopener noreferrer" 
                   class="inline-flex items-center justify-center gap-2.5 bg-gradient-to-r from-emerald-500 via-teal-500 to-indigo-600 hover:from-emerald-400 hover:to-indigo-500 text-white font-bold text-sm sm:text-base px-8 py-3.5 rounded-2xl shadow-xl shadow-emerald-500/20 transition-all transform hover:scale-105 active:scale-95 text-center">
                    <i class="fa-solid fa-cart-shopping"></i> Comprar / Resgatar Agora
                </a>
                <span class="text-[10px] text-slate-400 text-center sm:text-right">
                    <i class="fa-solid fa-shield-halved text-emerald-400 mr-1"></i> Compra 100% Segura e Verificada
                </span>
            </div>
        </div>
    </div>
    """
    
    seo_keywords = f"comprar {game_name}, preco {game_name}, ofertas {game_name}, noticias {category}, lancamentos jogos 2026, gameplay {game_name}, onde comprar {game_name}"
    
    return {
        "title": clean_title,
        "category": category,
        "summary": summary,
        "content": content_html,
        "key_points": key_points,
        "faq_json": json.dumps(faq_items, ensure_ascii=False),
        "deal_price": deal_price,
        "deal_discount": deal_discount,
        "buy_url": buy_url,
        "seo_keywords": seo_keywords
    }

def create_full_article(raw_item, settings):
    raw_title = raw_item.get('title', 'Notícia de Games')
    category = detect_category(raw_title)
    
    prompt = f"""
    Você é o redator de SEO e vendas do maior blog de games do Brasil. Crie um artigo completo com foco em rankear no Google em 1º lugar e converter vendas do jogo:
    
    Título: {raw_title}
    Fonte: {raw_item.get('source_url', '')}
    Categoria: {category}
    
    Retorne um JSON com:
    - "title": Título chamativo de alto clique e SEO (em Português).
    - "category": Categoria (PlayStation, Xbox, PC Gaming, Nintendo, Promoções, Lançamentos, Vazamentos, Geral).
    - "summary": Resumo persuasivo em 2 frases para meta description do Google.
    - "key_points": Lista de 4 destaques.
    - "deal_price": Preço ou oferta (ex: R$ 199,90 ou Grátis).
    - "deal_discount": Tag de desconto (ex: -30% OFF).
    - "faq_items": Array com 3 objetos {{"question": "...", "answer": "..."}}.
    - "seo_keywords": String com 6 palavras-chave separadas por vírgula.
    """
    
    llm_result = call_llm(prompt, settings)
    
    if not llm_result or "title" not in llm_result:
        llm_result = fallback_generate_article(raw_item)
        
    title = llm_result.get('title', raw_title)
    cat = llm_result.get('category', category)
    slug = generate_slug(title)
    
    cover_image = raw_item.get('image_url')
    if not cover_image or 'external-preview' in cover_image or 'default' in cover_image or len(cover_image) < 10:
        cover_image = DEFAULT_GAMING_IMAGES.get(cat, DEFAULT_GAMING_IMAGES['Geral'])
        
    article_data = {
        "reddit_id": raw_item.get('id', slug),
        "title": title,
        "slug": slug,
        "category": cat,
        "summary": llm_result.get('summary', raw_title),
        "content": llm_result.get('content', f"<p>{raw_title}</p>"),
        "cover_image": cover_image,
        "source_url": raw_item.get('source_url', ''),
        "reddit_url": raw_item.get('reddit_url', ''),
        "buy_url": llm_result.get('buy_url', raw_item.get('source_url', 'https://store.steampowered.com')),
        "deal_price": llm_result.get('deal_price', 'R$ 149,90'),
        "deal_discount": llm_result.get('deal_discount', 'OFERTA ESPECIAL'),
        "faq_json": llm_result.get('faq_json', '[]') if isinstance(llm_result.get('faq_json'), str) else json.dumps(llm_result.get('faq_items', []), ensure_ascii=False),
        "seo_keywords": llm_result.get('seo_keywords', f'comprar {title}, jogos {cat}'),
        "upvotes": int(raw_item.get('upvotes', 10)),
        "comments_count": int(raw_item.get('comments_count', 5)),
        "author": "Redação Gamer AI & Deals",
        "status": "published",
        "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return article_data
