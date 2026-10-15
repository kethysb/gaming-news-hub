// State
let currentCategory = 'Todos';
let currentSearch = '';
let currentArticles = [];
let activeArticle = null;

// DOM Elements
const articlesGrid = document.getElementById('articles-grid');
const heroFeatured = document.getElementById('hero-featured');
const breakingTicker = document.getElementById('breaking-ticker');
const totalArticlesCount = document.getElementById('total-articles-count');
const searchInput = document.getElementById('search-input');
const categoryButtons = document.querySelectorAll('.cat-btn');

// Modals
const articleModal = document.getElementById('article-modal');
const logsModal = document.getElementById('logs-modal');
const settingsModal = document.getElementById('settings-modal');

// Buttons
const btnScanNow = document.getElementById('btn-scan-now');
const scanIcon = document.getElementById('scan-icon');
const btnOpenLogs = document.getElementById('btn-open-logs');
const btnCloseLogs = document.getElementById('btn-close-logs');
const btnRefreshLogs = document.getElementById('btn-refresh-logs');
const btnOpenSettings = document.getElementById('btn-open-settings');
const btnCloseSettings = document.getElementById('btn-close-settings');
const btnCloseModal = document.getElementById('btn-close-modal');
const settingsForm = document.getElementById('settings-form');

// Badges & Colors
const CATEGORY_COLORS = {
    'PlayStation': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    'Xbox': 'bg-green-500/20 text-green-400 border-green-500/30',
    'PC Gaming': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    'Nintendo': 'bg-red-500/20 text-red-400 border-red-500/30',
    'Promoções': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    'Vazamentos': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    'Lançamentos': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    'Geral': 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30'
};

function formatRelativeTime(dateString) {
    if (!dateString) return 'recente';
    const date = new Date(dateString);
    const now = new Date();
    const diffSeconds = Math.floor((now - date) / 1000);
    
    if (diffSeconds < 60) return 'agora mesmo';
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `há ${diffMinutes} min`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `há ${diffHours} h`;
    const diffDays = Math.floor(diffHours / 24);
    return `há ${diffDays} dias`;
}

// Fetch Articles
async function loadArticles() {
    try {
        let url = `/api/articles?limit=50`;
        if (currentCategory && currentCategory !== 'Todos') {
            url += `&category=${encodeURIComponent(currentCategory)}`;
        }
        if (currentSearch) {
            url += `&search=${encodeURIComponent(currentSearch)}`;
        }

        let data;
        try {
            const res = await fetch(url);
            if (res.ok) {
                data = await res.json();
            }
        } catch (e) {}

        // Fallback para news.json se API falhar ou estiver estática
        if (!data || !data.articles) {
            const resStatic = await fetch('/news.json');
            const staticData = await resStatic.json();
            let list = staticData.articles || [];
            if (currentCategory && currentCategory !== 'Todos') {
                list = list.filter(a => a.category === currentCategory);
            }
            if (currentSearch) {
                const s = currentSearch.toLowerCase();
                list = list.filter(a => (a.title && a.title.toLowerCase().includes(s)) || (a.summary && a.summary.toLowerCase().includes(s)));
            }
            data = { articles: list, stats: staticData.stats };
        }

        currentArticles = data.articles || [];
        if (totalArticlesCount && data.stats) {
            totalArticlesCount.innerText = data.stats.total_articles || currentArticles.length;
        } else if (totalArticlesCount) {
            totalArticlesCount.innerText = currentArticles.length;
        }
        
        renderHero();
        renderGrid();
        updateTicker();
    } catch (err) {
        console.error('Erro ao carregar artigos:', err);
    }
}

// Fetch Stats
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        if (res.ok) {
            const data = await res.json();
            if (totalArticlesCount) {
                totalArticlesCount.innerText = data.total_articles || currentArticles.length;
            }
        }
    } catch (e) {}
}

// Render Featured Hero
function renderHero() {
    if (currentArticles.length === 0 || currentCategory !== 'Todos' || currentSearch) {
        heroFeatured.innerHTML = '';
        heroFeatured.classList.add('hidden');
        return;
    }

    heroFeatured.classList.remove('hidden');
    const featured = currentArticles[0];
    const catClass = CATEGORY_COLORS[featured.category] || CATEGORY_COLORS['Geral'];

    heroFeatured.innerHTML = `
        <div class="relative rounded-3xl overflow-hidden bg-slate-900 border border-slate-800 shadow-2xl group cursor-pointer" onclick="openArticle('${featured.slug}')">
            <!-- Background Image with Overlay -->
            <div class="absolute inset-0">
                <img src="${featured.cover_image}" alt="${featured.title}" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 opacity-40">
                <div class="absolute inset-0 bg-gradient-to-t from-[#0B0F19] via-[#0B0F19]/80 to-transparent"></div>
            </div>

            <!-- Content -->
            <div class="relative p-6 sm:p-10 lg:p-12 max-w-3xl flex flex-col justify-end min-h-[380px]">
                <div class="flex items-center gap-3 mb-4">
                    <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${catClass}">
                        ${featured.category}
                    </span>
                    <span class="text-xs text-amber-400 font-semibold flex items-center gap-1">
                        <i class="fa-solid fa-fire"></i> Destaque Viral
                    </span>
                    <span class="text-xs text-slate-400">• ${formatRelativeTime(featured.published_at)}</span>
                </div>

                <h2 class="font-['Space_Grotesk'] text-2xl sm:text-4xl font-bold text-white leading-tight mb-4 group-hover:text-indigo-300 transition-colors">
                    ${featured.title}
                </h2>

                <p class="text-slate-300 text-sm sm:text-base line-clamp-2 mb-6 leading-relaxed">
                    ${featured.summary}
                </p>

                <div class="flex items-center gap-4">
                    <button class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm px-6 py-3 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all">
                        <span>Ler Matéria Completa</span>
                        <i class="fa-solid fa-arrow-right text-xs"></i>
                    </button>
                    <span class="text-xs text-slate-400">
                        <i class="fa-solid fa-arrow-up text-amber-400 mr-1"></i> ${featured.upvotes} votos no Reddit
                    </span>
                </div>
            </div>
        </div>
    `;
}

// Render Grid
function renderGrid() {
    const displayList = (currentCategory === 'Todos' && !currentSearch) ? currentArticles.slice(1) : currentArticles;

    if (displayList.length === 0) {
        articlesGrid.innerHTML = `
            <div class="col-span-full py-16 text-center text-slate-400 bg-slate-900/40 border border-slate-800 rounded-2xl">
                <i class="fa-solid fa-gamepad text-4xl text-slate-600 mb-3"></i>
                <p class="text-base font-semibold text-slate-300">Nenhum artigo encontrado</p>
                <p class="text-xs text-slate-500 mt-1">Clique em "Escanear Reddit Agora" para buscar novos artigos.</p>
            </div>
        `;
        return;
    }

    articlesGrid.innerHTML = displayList.map(art => {
        const catClass = CATEGORY_COLORS[art.category] || CATEGORY_COLORS['Geral'];
        return `
            <article class="article-card bg-[#111728] border border-slate-800/90 rounded-2xl overflow-hidden flex flex-col cursor-pointer group" onclick="openArticle('${art.slug}')">
                <!-- Card Image -->
                <div class="relative h-48 w-full overflow-hidden bg-slate-900">
                    <img src="${art.cover_image}" alt="${art.title}" class="card-img w-full h-full object-cover">
                    <div class="absolute inset-0 bg-gradient-to-t from-[#111728] via-transparent to-transparent"></div>
                    
                    <span class="absolute top-3 left-3 px-2.5 py-0.5 rounded-lg text-[11px] font-bold uppercase tracking-wider border backdrop-blur-md ${catClass}">
                        ${art.category}
                    </span>

                    <span class="absolute top-3 right-3 bg-black/60 backdrop-blur-md text-amber-400 text-[11px] font-semibold px-2 py-0.5 rounded-lg border border-white/10 flex items-center gap-1">
                        <i class="fa-solid fa-arrow-up text-[10px]"></i> ${art.upvotes}
                    </span>
                </div>

                <!-- Card Body -->
                <div class="p-5 flex-1 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center gap-2 text-[11px] text-slate-400 mb-2">
                            <span><i class="fa-regular fa-clock mr-1"></i>${formatRelativeTime(art.published_at)}</span>
                            <span>•</span>
                            <span><i class="fa-regular fa-eye mr-1"></i>${art.views || 0} visualizações</span>
                        </div>

                        <h3 class="font-['Space_Grotesk'] text-lg font-bold text-white group-hover:text-indigo-400 transition-colors line-clamp-2 leading-snug mb-2">
                            ${art.title}
                        </h3>

                        <p class="text-slate-400 text-xs line-clamp-3 leading-relaxed mb-4">
                            ${art.summary}
                        </p>
                    </div>

                    <div class="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs">
                        <span class="text-indigo-400 font-semibold group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                            Ler notícia <i class="fa-solid fa-chevron-right text-[10px]"></i>
                        </span>
                        <span class="text-slate-500 text-[11px]">Redação AI</span>
                    </div>
                </div>
            </article>
        `;
    }).join('');
}

// Update Breaking Ticker
function updateTicker() {
    if (currentArticles.length > 0) {
        const topHeadlines = currentArticles.slice(0, 5).map(a => `<span class="inline-block mr-6 text-slate-300">🔥 ${a.title}</span>`).join(' • ');
        breakingTicker.innerHTML = topHeadlines;
    }
}

// Open Article Modal
async function openArticle(slug) {
    try {
        let art = currentArticles.find(a => a.slug === slug || String(a.id) === String(slug));
        if (!art) {
            try {
                const res = await fetch(`/api/articles/${slug}`);
                if (res.ok) art = await res.json();
            } catch (e) {}
        }
        if (!art) return;
        activeArticle = art;

        document.getElementById('modal-title').innerText = art.title;
        document.getElementById('modal-category-badge').innerText = art.category;
        document.getElementById('modal-category-badge').className = `px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wider border ${CATEGORY_COLORS[art.category] || CATEGORY_COLORS['Geral']}`;
        document.getElementById('modal-date').innerText = new Date(art.published_at).toLocaleString('pt-BR');
        document.getElementById('modal-views').innerText = art.views;
        document.getElementById('modal-upvotes').innerHTML = `<i class="fa-solid fa-arrow-up mr-1"></i>${art.upvotes} votos`;
        document.getElementById('modal-comments').innerHTML = `<i class="fa-solid fa-comments mr-1"></i>${art.comments_count} comentários`;
        document.getElementById('modal-image').src = art.cover_image;
        document.getElementById('modal-content').innerHTML = art.content;
        
        // Atualizar Barra Sticky de Compra
        const stickyDiscount = document.getElementById('sticky-discount-badge');
        const stickyTitle = document.getElementById('sticky-title-preview');
        const stickyPrice = document.getElementById('sticky-price-display');
        const stickyBtn = document.getElementById('sticky-buy-btn');

        if (stickyDiscount) stickyDiscount.innerText = art.deal_discount || 'OFERTA ESPECIAL';
        if (stickyTitle) stickyTitle.innerText = `Garantir ${art.title.split(':')[0] || 'Edição Oficial'}`;
        if (stickyPrice) stickyPrice.innerText = art.deal_price || 'R$ 149,90';
        if (stickyBtn) stickyBtn.href = art.buy_url || art.source_url || '#';

        // Atualizar Meta Title & SEO
        document.title = `${art.title} | NEXUS GAMING`;

        // Injetar Schema.org JSON-LD para Google News, Discover & Rich Snippets
        let faqs = [];
        try {
            faqs = JSON.parse(art.faq_json || '[]');
        } catch (e) {}

        const schemaData = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "NewsArticle",
                    "headline": art.title,
                    "description": art.summary,
                    "image": [art.cover_image],
                    "datePublished": art.published_at,
                    "dateModified": art.published_at,
                    "author": [{
                        "@type": "Person",
                        "name": art.author || "Redação Gamer AI"
                    }],
                    "publisher": {
                        "@type": "Organization",
                        "name": "NEXUS GAMING",
                        "logo": {
                            "@type": "ImageObject",
                            "url": `${window.location.origin}/favicon.ico`
                        }
                    },
                    "mainEntityOfPage": {
                        "@type": "WebPage",
                        "@id": `${window.location.origin}/#${art.slug}`
                    }
                },
                ...(faqs.length > 0 ? [{
                    "@type": "FAQPage",
                    "mainEntity": faqs.map(f => ({
                        "@type": "Question",
                        "name": f.question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f.answer
                        }
                    }))
                }] : []),
                {
                    "@type": "Product",
                    "name": art.title.split(':')[0] || art.title,
                    "image": art.cover_image,
                    "description": art.summary,
                    "offers": {
                        "@type": "Offer",
                        "priceCurrency": "BRL",
                        "price": (art.deal_price || "149.90").replace(/[^0-9,.]/g, '').replace(',', '.') || "149.90",
                        "availability": "https://schema.org/InStock",
                        "url": art.buy_url || `${window.location.origin}/#${art.slug}`
                    }
                }
            ]
        };

        const schemaTag = document.getElementById('seo-schema-jsonld');
        if (schemaTag) {
            schemaTag.textContent = JSON.stringify(schemaData, null, 2);
        }

        const sourceLink = document.getElementById('modal-source-link');
        if (art.source_url) {
            sourceLink.href = art.source_url;
            sourceLink.style.display = 'inline-flex';
        } else {
            sourceLink.style.display = 'none';
        }

        const redditLink = document.getElementById('modal-reddit-link');
        if (art.reddit_url) {
            redditLink.href = art.reddit_url;
            redditLink.style.display = 'inline-flex';
        } else {
            redditLink.style.display = 'none';
        }

        articleModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        window.location.hash = art.slug;
    } catch (e) {
        console.error('Erro ao abrir artigo:', e);
    }
}

// Close Modal
function closeModal() {
    articleModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
    document.title = 'NEXUS GAMING | Notícias de Jogos, Lançamentos & Ofertas Exclusivas';
    if (window.location.hash) {
        history.pushState("", document.title, window.location.pathname + window.location.search);
    }
}

// Scan Now Trigger
async function handleScanNow() {
    btnScanNow.disabled = true;
    scanIcon.classList.add('fa-spin');
    const originalText = btnScanNow.innerHTML;
    btnScanNow.innerHTML = `<i class="fa-solid fa-arrows-rotate fa-spin"></i> <span>Escaneando Reddit...</span>`;

    try {
        const res = await fetch('/api/radar/scan', { method: 'POST' });
        const data = await res.json();
        
        await loadArticles();
        await loadStats();

        // Toast de sucesso
        alert(`⚡ Varredura concluída!\n${data.new_articles} novos artigos foram gerados e adicionados ao blog.`);
    } catch (e) {
        alert('Erro ao executar varredura do radar.');
    } finally {
        btnScanNow.disabled = false;
        scanIcon.classList.remove('fa-spin');
        btnScanNow.innerHTML = originalText;
    }
}

// Load Logs
async function loadLogs() {
    const logsContainer = document.getElementById('logs-container');
    try {
        const res = await fetch('/api/logs');
        const data = await res.json();
        const logs = data.logs || [];
        
        if (logs.length === 0) {
            logsContainer.innerHTML = '<div class="text-slate-500">Nenhum log registrado ainda.</div>';
            return;
        }

        logsContainer.innerHTML = logs.map(l => {
            const color = l.status === 'success' ? 'text-emerald-400' : (l.status === 'error' ? 'text-rose-400' : 'text-slate-300');
            return `
                <div class="p-2 rounded bg-slate-950 border border-slate-900 flex items-start gap-2">
                    <span class="text-slate-500 shrink-0">[${l.timestamp.split(' ')[1] || l.timestamp}]</span>
                    <span class="text-indigo-400 font-semibold shrink-0">${l.source}:</span>
                    <span class="${color}">${l.message}</span>
                </div>
            `;
        }).join('');
    } catch (e) {
        logsContainer.innerHTML = '<div class="text-rose-400">Erro ao carregar logs.</div>';
    }
}

// Load & Save Settings
async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        const s = await res.json();
        document.getElementById('set-autopilot').value = s.autopilot || 'true';
        document.getElementById('set-interval').value = s.scan_interval_minutes || '3';
        document.getElementById('set-ai-provider').value = s.ai_provider || 'builtin';
        document.getElementById('set-gemini-key').value = s.gemini_api_key || '';
    } catch (e) {}
}

async function saveSettings(e) {
    e.preventDefault();
    const payload = {
        autopilot: document.getElementById('set-autopilot').value,
        scan_interval_minutes: document.getElementById('set-interval').value,
        ai_provider: document.getElementById('set-ai-provider').value,
        gemini_api_key: document.getElementById('set-gemini-key').value
    };

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert('✅ Configurações salvas com sucesso!');
            settingsModal.classList.add('hidden');
        }
    } catch (e) {
        alert('Erro ao salvar configurações.');
    }
}

// Event Listeners
categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        categoryButtons.forEach(b => {
            b.classList.remove('active', 'bg-indigo-600', 'text-white', 'shadow-md', 'shadow-indigo-500/20');
            b.classList.add('bg-slate-800/80', 'text-slate-300');
        });
        btn.classList.add('active', 'bg-indigo-600', 'text-white', 'shadow-md', 'shadow-indigo-500/20');
        btn.classList.remove('bg-slate-800/80', 'text-slate-300');
        
        currentCategory = btn.getAttribute('data-cat');
        loadArticles();
    });
});

let searchTimeout;
searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentSearch = e.target.value.trim();
        loadArticles();
    }, 300);
});

btnScanNow.addEventListener('click', handleScanNow);

btnOpenLogs.addEventListener('click', () => {
    logsModal.classList.remove('hidden');
    loadLogs();
});
btnCloseLogs.addEventListener('click', () => logsModal.classList.add('hidden'));
btnRefreshLogs.addEventListener('click', loadLogs);

btnOpenSettings.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
    loadSettings();
});
btnCloseSettings.addEventListener('click', () => settingsModal.classList.add('hidden'));
settingsForm.addEventListener('submit', saveSettings);

btnCloseModal.addEventListener('click', closeModal);
articleModal.addEventListener('click', (e) => {
    if (e.target === articleModal) closeModal();
});

// Share buttons
document.getElementById('btn-share-whatsapp').addEventListener('click', () => {
    if (!activeArticle) return;
    const text = encodeURIComponent(`Confira essa notícia: ${activeArticle.title} - ${window.location.origin}/#${activeArticle.slug}`);
    window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
});

document.getElementById('btn-share-x').addEventListener('click', () => {
    if (!activeArticle) return;
    const text = encodeURIComponent(`🔥 ${activeArticle.title}`);
    const url = encodeURIComponent(`${window.location.origin}/#${activeArticle.slug}`);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
});

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
    loadStats();
    
    // Check URL Hash for direct article link
    if (window.location.hash) {
        const slug = window.location.hash.replace('#', '');
        if (slug) setTimeout(() => openArticle(slug), 500);
    }
    
    // Auto-refresh feed every 45s
    setInterval(() => {
        loadArticles();
        loadStats();
    }, 45000);
});
