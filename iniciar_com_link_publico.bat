@echo off
title NEXUS GAMING - Link Publico Online
echo ====================================================
echo  Gerando Link Publico Online para o Blog Gamer...
echo ====================================================
start /min python server.py
timeout /t 2 /nobreak >nul
echo Conectando ao tunel publico...
npx localtunnel --port 28888 --subdomain nexus-gaming-news-br
pause
