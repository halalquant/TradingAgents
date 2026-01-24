<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=zh">中文</a>
</div>

---


# TradingAgents: Multi-Agent LLM Crypto Trading & Portfolio Management Framework

> 🎉 **TradingAgents** is now a comprehensive open-source platform for multi-agent, LLM-powered **crypto spot trading and portfolio management**. The framework is designed for research and practical experimentation in automated crypto trading, portfolio allocation, and risk management, with a strong focus on real-world crypto market dynamics.
>
> We thank our community for the enthusiasm and feedback! The project is fully open-source—join us to build the next generation of crypto trading agents.

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

<div align="center">

🚀 [TradingAgents](#tradingagents-framework) | ⚡ [Installation & CLI](#installation-and-cli) | 🎬 [Demo](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [Package Usage](#tradingagents-package) | 🤝 [Contributing](#contributing) | 📄 [Citation](#citation)

</div>


## Project Scope & Overview

**TradingAgents** is a multi-agent, LLM-driven framework for **crypto spot trading and portfolio management**. It simulates the structure of a modern crypto trading firm, with specialized agents for:

- **Technical, fundamental, news, and sentiment analysis** (crypto-focused)
- **Portfolio management**: allocation, rebalancing, and risk controls for multi-asset crypto portfolios
- **Trader and risk manager agents**: make and approve portfolio-aware, dollar-specific trading decisions
- **Advanced crypto features**: on-chain analytics, DeFi/yield integration, 24/7 market support, and more

The system is modular, research-oriented, and supports rapid adaptation to new crypto assets, exchanges, and data sources. It is not intended as financial advice. [See full disclaimer.](https://tauric.ai/disclaimer/)

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>


### Analyst Team (Crypto-Focused)
- **Fundamentals Analyst**: Evaluates tokenomics, on-chain metrics (TVL, active addresses), and project fundamentals for crypto assets.
- **Sentiment Analyst**: Analyzes crypto-specific social media, news, and sentiment signals (e.g., Twitter, Reddit, CoinDesk).
- **News Analyst**: Monitors global and crypto news, macro events, and regulatory changes impacting digital assets.
- **Technical Analyst**: Applies crypto-relevant indicators (e.g., MACD, RSI, Bollinger Bands, funding rates) to spot trends and signals.

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>


### Researcher Team
- **Bullish and Bearish Researchers**: Critically debate analyst insights, balancing upside and risk for each crypto asset and portfolio move.

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>


### Trader Agent
- **Trader**: Synthesizes all agent reports to make portfolio-aware, dollar-specific trading decisions (e.g., "Buy $500 BTC").

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>


## Installation and CLI

### Installation

Clone TradingAgents:
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

Create a virtual environment in any of your favorite environment managers:
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents

pyenv
pyenv local 3.12.7
python -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip list

deactivate

if error mini-racer
source .venv/bin/activate && pip install --no-deps -r requirements.txt #install without miniracer 

Api
python webapp.py

Bot Telegram
python bot.py
```

### Build the app and running (Local)
```
Docker build
docker build -t trading-bot:latest .
<!-- for arm64 -->
docker-buildx build \
  --platform linux/amd64 \
  -t jafarmuhammad/cryptoquant:latest \
  --push .

docker push jafarmuhammad/cryptoquant:latest
docker run --env-file .env trading-bot:latest

docker compose up -d
docker exec -it {container-id} bash
redis-cli -h localhost -p 6379 -a trading-agents

Run worker:
rq worker --url redis://:{{REDIS_PASSWORD}}@{{REDIS_HOST}}:{{REDIS_PORT}}/{{REDIS_DB}} --with-scheduler

Requeue failed jobs
rq requeue --all --queue default --url redis://:{{REDIS_PASSWORD}}@{{REDIS_HOST}}:{{REDIS_PORT}}/{{REDIS_DB}}

```

