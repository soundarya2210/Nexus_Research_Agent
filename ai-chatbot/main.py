import os
import re
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ── env ──────────────────────────────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nexus Research",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@300;400&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --ink:        #0a0a0b;
  --ink-2:      #111113;
  --ink-3:      #1a1a1e;
  --gold:       #c9a84c;
  --gold-dim:   #7a6430;
  --gold-glow:  rgba(201,168,76,0.12);
  --text:       #e8e3d8;
  --text-dim:   #7a7568;
  --text-muted: #3d3b36;
  --border:     rgba(201,168,76,0.18);
  --border-dim: rgba(255,255,255,0.06);
  --red:        #c94c4c;
  --teal:       #4cc9a8;
}

/* ── global reset ── */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--ink) !important;
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-weight: 300;
}

/* hide streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display:none !important; }

/* ── main container ── */
[data-testid="stMain"] { background: var(--ink) !important; }
.block-container {
  max-width: 860px !important;
  padding: 0 2rem 4rem !important;
  margin: 0 auto !important;
}

/* ── masthead ── */
.masthead {
  text-align: center;
  padding: 3.5rem 0 2.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2.5rem;
  position: relative;
}
.masthead::before {
  content: '';
  position: absolute;
  bottom: -1px; left: 50%;
  transform: translateX(-50%);
  width: 60px; height: 2px;
  background: var(--gold);
}
.masthead-eyebrow {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.35em;
  color: var(--gold);
  text-transform: uppercase;
  margin-bottom: 0.8rem;
}
.masthead h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.2rem, 5vw, 3.2rem);
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
  line-height: 1.1;
  margin: 0 0 0.6rem;
}
.masthead-sub {
  font-size: 0.9rem;
  color: var(--text-dim);
  font-weight: 300;
  letter-spacing: 0.02em;
}

/* ── search bar ── */
[data-testid="stTextInput"] > div > div {
  background: var(--ink-3) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  transition: border 0.25s, box-shadow 0.25s;
}
[data-testid="stTextInput"] > div > div:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 3px var(--gold-glow) !important;
}
[data-testid="stTextInput"] input {
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1rem !important;
  padding: 0.85rem 1.1rem !important;
  background: transparent !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--text-muted) !important; }
[data-testid="stTextInput"] label {
  color: var(--text-dim) !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.15em !important;
  text-transform: uppercase !important;
  font-family: 'DM Mono', monospace !important;
}

/* ── button ── */
[data-testid="stButton"] > button {
  width: 100%;
  background: var(--gold) !important;
  color: var(--ink) !important;
  border: none !important;
  border-radius: 4px !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  padding: 0.85rem 1.5rem !important;
  font-weight: 400 !important;
  transition: opacity 0.2s, transform 0.15s;
  cursor: pointer;
}
[data-testid="stButton"] > button:hover {
  opacity: 0.88 !important;
  transform: translateY(-1px);
}

/* ── result cards ── */
.result-header {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 1.5rem 0 1rem;
  border-bottom: 1px solid var(--border-dim);
  margin-bottom: 1.5rem;
}
.result-header .tag {
  font-family: 'DM Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--gold);
  background: var(--gold-glow);
  border: 1px solid var(--border);
  padding: 0.25rem 0.6rem;
  border-radius: 2px;
}
.result-count {
  font-family: 'DM Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-left: auto;
}

.source-card {
  background: var(--ink-2);
  border: 1px solid var(--border-dim);
  border-left: 3px solid var(--gold);
  border-radius: 4px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
  overflow: hidden;
}
.source-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--gold-glow) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s;
}
.source-card:hover { border-color: var(--gold); background: var(--ink-3); }
.source-card:hover::before { opacity: 1; }

.source-num {
  font-family: 'DM Mono', monospace;
  font-size: 0.6rem;
  color: var(--gold-dim);
  letter-spacing: 0.1em;
  margin-bottom: 0.4rem;
}
.source-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.05rem;
  font-weight: 400;
  color: var(--text);
  margin-bottom: 0.35rem;
  line-height: 1.35;
}
.source-url {
  font-family: 'DM Mono', monospace;
  font-size: 0.68rem;
  color: var(--gold);
  text-decoration: none;
  word-break: break-all;
  opacity: 0.8;
}
.source-url:hover { opacity: 1; text-decoration: underline; }
.source-snippet {
  margin-top: 0.7rem;
  font-size: 0.85rem;
  color: var(--text-dim);
  line-height: 1.6;
  font-weight: 300;
}

/* ── summary box ── */
.summary-box {
  background: var(--ink-3);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.5rem 1.8rem;
  margin-bottom: 2rem;
  position: relative;
}
.summary-box::before {
  content: '"';
  font-family: 'Playfair Display', serif;
  font-size: 4rem;
  color: var(--gold);
  opacity: 0.15;
  position: absolute;
  top: 0.2rem; left: 1rem;
  line-height: 1;
}
.summary-label {
  font-family: 'DM Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 0.8rem;
}
.summary-text {
  font-size: 0.92rem;
  line-height: 1.75;
  color: var(--text-dim);
  font-weight: 300;
}

/* ── error ── */
.err-box {
  background: rgba(201,76,76,0.08);
  border: 1px solid rgba(201,76,76,0.3);
  border-radius: 4px;
  padding: 1rem 1.4rem;
  font-family: 'DM Mono', monospace;
  font-size: 0.8rem;
  color: var(--red);
}

/* ── spinner override ── */
[data-testid="stSpinner"] { color: var(--gold) !important; }

/* ── history pills ── */
.history-wrap {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
  margin-bottom: 2rem;
}
.history-pill {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  padding: 0.3rem 0.75rem;
  border-radius: 2px;
  background: var(--ink-3);
  border: 1px solid var(--border-dim);
  color: var(--text-dim);
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
}
.history-pill:hover { border-color: var(--gold); color: var(--gold); }

/* ── divider ── */
.rule { border: none; border-top: 1px solid var(--border-dim); margin: 2rem 0; }

/* ── column gaps ── */
[data-testid="stColumns"] { gap: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def search_tavily(query: str, max_results: int = 8) -> list[dict]:
    """Call Tavily Search API and return list of source dicts."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": True,
        "include_raw_content": False,
    }
    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])
    answer  = data.get("answer", "")
    return results, answer


def summarize_with_groq(topic: str, sources: list[dict]) -> str:
    """Ask Groq to write a research brief from the sources."""
    client = Groq(api_key=GROQ_API_KEY)
    snippets = "\n".join(
        f"[{i+1}] {s.get('title','')}: {s.get('content','')[:300]}"
        for i, s in enumerate(sources[:6])
    )
    prompt = (
        f"You are a concise research analyst. Given the following web sources about "
        f'"{topic}", write a tight 3-4 sentence research brief that synthesises the '
        f"key findings. Do NOT mention source numbers. Be informative and neutral.\n\n"
        f"Sources:\n{snippets}"
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def domain_from_url(url: str) -> str:
    m = re.search(r'https?://(?:www\.)?([^/]+)', url)
    return m.group(1) if m else url


# ── session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "results"  not in st.session_state:
    st.session_state.results  = None
if "summary"  not in st.session_state:
    st.session_state.summary  = ""
if "topic"    not in st.session_state:
    st.session_state.topic    = ""


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="masthead">
  <div class="masthead-eyebrow">⬡ Intelligence Research</div>
  <h1>Nexus Research</h1>
  <div class="masthead-sub">Surface authoritative sources across the open web — instantly.</div>
</div>
""", unsafe_allow_html=True)

# ── API key warnings ──
if not GROQ_API_KEY:
    st.markdown('<div class="err-box">⚠ GROQ_API_KEY not found in .env</div>', unsafe_allow_html=True)
    st.stop()
if not TAVILY_API_KEY:
    st.markdown('<div class="err-box">⚠ TAVILY_API_KEY not found in .env — add it to search the web</div>', unsafe_allow_html=True)
    st.stop()

# ── input row ──
col1, col2 = st.columns([5, 1])
with col1:
    topic_input = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs 2025",
        label_visibility="visible",
        key="topic_input",
    )
with col2:
    st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
    search_btn = st.button("Search →")

# ── history pills ──
if st.session_state.history:
    st.markdown('<div class="history-wrap">' +
        "".join(f'<span class="history-pill">{h}</span>' for h in st.session_state.history[-6:]) +
        '</div>', unsafe_allow_html=True)

# ── search logic ──
trigger = search_btn and topic_input.strip()

if trigger:
    topic = topic_input.strip()
    with st.spinner("Searching across the web…"):
        try:
            raw_results, tavily_answer = search_tavily(topic, max_results=8)
        except Exception as e:
            st.markdown(f'<div class="err-box">Search error: {e}</div>', unsafe_allow_html=True)
            st.stop()

    with st.spinner("Synthesising research brief…"):
        try:
            summary = summarize_with_groq(topic, raw_results)
        except Exception as e:
            summary = tavily_answer or ""

    st.session_state.results = raw_results
    st.session_state.summary = summary
    st.session_state.topic   = topic
    if topic not in st.session_state.history:
        st.session_state.history.append(topic)

# ── results display ──
if st.session_state.results:
    topic   = st.session_state.topic
    sources = st.session_state.results
    summary = st.session_state.summary

    # Summary
    if summary:
        st.markdown(f"""
        <div class="summary-box">
          <div class="summary-label">Research Brief</div>
          <div class="summary-text">{summary}</div>
        </div>
        """, unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div class="result-header">
      <span class="tag">Sources</span>
      <span style="font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--text)">
        {topic}
      </span>
      <span class="result-count">{len(sources)} results</span>
    </div>
    """, unsafe_allow_html=True)

    # Cards — two columns
    left, right = st.columns(2)
    for i, src in enumerate(sources):
        title   = src.get("title", "Untitled")
        url     = src.get("url", "#")
        snippet = src.get("content", "")[:220].rstrip() + "…"
        domain  = domain_from_url(url)
        card_html = f"""
        <div class="source-card">
          <div class="source-num">SOURCE {i+1:02d} · {domain}</div>
          <div class="source-title">{title}</div>
          <a class="source-url" href="{url}" target="_blank">{url[:72]}{"…" if len(url)>72 else ""}</a>
          <div class="source-snippet">{snippet}</div>
        </div>
        """
        if i % 2 == 0:
            left.markdown(card_html, unsafe_allow_html=True)
        else:
            right.markdown(card_html, unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;font-family:\'DM Mono\',monospace;font-size:0.62rem;'
        'color:var(--text-muted);letter-spacing:0.2em">NEXUS RESEARCH · POWERED BY GROQ + TAVILY</div>',
        unsafe_allow_html=True
    )
