# ⬡ Nexus Research

A premium AI-powered research agent built with Streamlit, Groq (LLaMA 3.3 70B), and Tavily Search.

## Stack
| Layer | Tool |
|-------|------|
| UI | Streamlit |
| LLM (summarisation) | Groq · llama-3.3-70b-versatile |
| Web Search | Tavily Search API |
| Package manager | uv |

## Setup

### 1. Get API keys
- **Groq** → https://console.groq.com (free)
- **Tavily** → https://tavily.com (free tier: 1,000 searches/month)

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and paste your keys
```

### 3. Install dependencies with uv
```bash
uv sync
```

### 4. Run
```bash
uv run streamlit run main.py
```

The app opens at **http://localhost:8501**

## Deploy to Streamlit Cloud
1. Push to a GitHub repo
2. Go to https://share.streamlit.io → New app
3. Set `GROQ_API_KEY` and `TAVILY_API_KEY` in **Secrets** (Settings → Secrets)
4. Deploy ✓
