# 🎮 NEXUS GAMING - Radar de Notícias & Blog Gamer Automático

Sistema completo de **Autoblog & Radar em Tempo Real** que monitora o Reddit (`/r/Games`, `/r/gaming`), portais de jogos e o **GamerPower**, converte as notícias virais em artigos jornalísticos em Português (com títulos chamativos, tags, imagens e SEO) e publica automaticamente no blog em segundos.

---

## ⚡ Recursos Principais

- 📡 **Radar Reddit em Tempo Real:** Captura novidades, vazamentos, notas de atualização e anúncios logo nos primeiros minutos.
- ✍️ **Redator IA Integrado:** Estrutura automaticamente matérias completas em PT-BR com introdução, tópicos de destaque, citações e análise.
- 🎨 **Interface Gamer Moderna:** Desenvolvida em Tailwind CSS com Dark Mode, filtros por categoria (PlayStation, Xbox, PC, Nintendo, Jogos Grátis, Lançamentos), ticker de últimas notícias e leitor de matérias modal.
- 🔄 **Piloto Automático (Auto-Pilot):** Thread em segundo plano que varre e publica notícias sem necessidade de intervenção humana.
- 📊 **Monitor & Logs ao Vivo:** Acompanhe em tempo real quais fóruns estão sendo varridos e quais matérias foram geradas.
- ⚙️ **Multi-Motor de IA:** Suporte nativo à IA Editorial embutida, 9Router local (`gemini/gemini-3-flash-preview`), Google Gemini API oficial ou OpenAI.

---

## 🚀 Como Executar

### 1. Iniciar o Servidor:
Clique duas vezes em `iniciar_blog.bat` ou rode no terminal:
```bash
cd C:\Users\Kethely\.gemini\antigravity\scratch\gaming-news-hub
python server.py
```

### 2. Acessar no Navegador:
Abra `http://localhost:3000` no seu Chrome ou navegador preferido.

---

## 📁 Estrutura do Projeto

```
gaming-news-hub/
│── news.db             # Banco de dados SQLite com todos os artigos e logs
│── server.py           # Servidor HTTP & API REST
│── database.py         # Modelos e operações do banco SQLite
│── ai_generator.py     # Motor gerador de artigos e redação IA
│── reddit_radar.py     # Coletor multicanal do Reddit e GamerPower
│── iniciar_blog.bat    # Executável rápido do servidor
│── public/
│   │── index.html      # Página principal do blog gamer
│   │── app.js          # Lógica reativa do frontend
│   │── style.css       # Estilos e animações
```
