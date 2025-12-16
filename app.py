from __future__ import annotations

from typing import List, Dict, Any
import streamlit as st
from dotenv import load_dotenv

from src.config import get_settings
from src.clients import make_clients
from src.ui import inject_css, hero, sidebar_help
from src.arxiv import fetch_papers, Paper
from src.utils import clip, stable_hash, join_nonempty
from src.rag import build_index, top_k
from src.prompts import BRIEF_SYSTEM, BRIEF_USER, CHAT_SYSTEM, CHAT_USER
from src.perplexity_api import web_signals, PerplexityError

load_dotenv()

st.set_page_config(page_title="ArxivPulse — Research → Industry Briefing (RAG)", page_icon="📚", layout="wide")
inject_css()
hero()
sidebar_help()

def ensure_state():
    st.session_state.setdefault("papers", [])
    st.session_state.setdefault("paper_vectors", None)
    st.session_state.setdefault("paper_texts", [])
    st.session_state.setdefault("paper_metas", [])
    st.session_state.setdefault("briefing", "")
    st.session_state.setdefault("web_signals", "")
    st.session_state.setdefault("chat", [])
    st.session_state.setdefault("emb_cache", {})

ensure_state()

def openai_embed(client, model: str, texts: List[str]) -> List[List[float]]:
    out = []
    for i in range(0, len(texts), 64):
        batch = texts[i:i+64]
        r = client.embeddings.create(model=model, input=batch)
        out.extend([d.embedding for d in r.data])
    return out

def get_or_embed(client, model: str, texts: List[str]) -> List[List[float]]:
    cache = st.session_state["emb_cache"]
    vecs: List[Any] = [None]*len(texts)
    missing, missing_meta = [], []
    for i,t in enumerate(texts):
        h = stable_hash(model + "::" + t)
        if h in cache:
            vecs[i] = cache[h]
        else:
            missing.append(t)
            missing_meta.append((i,h))
    if missing:
        new = openai_embed(client, model, missing)
        for (i,h),v in zip(missing_meta, new):
            cache[h] = v
            vecs[i] = v
    return vecs  # type: ignore

def build_paper_index(openai_client, embed_model: str, papers: List[Paper]):
    texts, metas = [], []
    for i, p in enumerate(papers, start=1):
        text = f"Title: {p.title}\nAbstract: {p.summary}"
        texts.append(text)
        metas.append({
            "pid": f"P{i}",
            "arxiv_id": p.arxiv_id,
            "title": p.title,
            "abs_url": p.abs_url,
            "pdf_url": p.pdf_url,
            "published": p.published,
            "authors": p.authors
        })
    vecs = get_or_embed(openai_client, embed_model, texts)
    st.session_state["paper_texts"] = texts
    st.session_state["paper_metas"] = metas
    st.session_state["paper_vectors"] = build_index(vecs, metas, texts)

def make_paper_list(papers: List[Paper]) -> str:
    return "\n".join([f"[P{i}] {p.title} — {p.abs_url}" for i,p in enumerate(papers, start=1)])

def make_abstract_block(papers: List[Paper]) -> str:
    blocks = []
    for i, p in enumerate(papers, start=1):
        blocks.append(f"[P{i}] {p.title}\n{p.summary}")
    return "\n\n".join(blocks)

def generate_briefing(openai_client, chat_model: str, papers: List[Paper]) -> str:
    paper_list = make_paper_list(papers)
    abstracts = make_abstract_block(papers)
    prompt = BRIEF_USER.format(paper_list=paper_list, abstracts=abstracts)

    r = openai_client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role":"system","content":BRIEF_SYSTEM},
            {"role":"user","content":prompt},
        ],
        temperature=0.25,
        max_tokens=1200,
    )
    return r.choices[0].message.content or ""

def answer_question(openai_client, chat_model: str, embed_model: str, question: str) -> str:
    index = st.session_state.get("paper_vectors")
    if not index:
        return "No paper index yet — fetch papers first."

    qv = get_or_embed(openai_client, embed_model, [question])[0]
    hits = top_k(index, qv, k=8)

    ctx_lines = []
    for score, meta, txt in hits:
        pid = meta["pid"]
        ctx_lines.append(f"[{pid}] {meta['title']}\nURL: {meta['abs_url']}\nEvidence: {txt}\n")

    context = "\n".join(ctx_lines)

    r = openai_client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role":"system","content":CHAT_SYSTEM},
            {"role":"user","content":CHAT_USER.format(question=question, context=context)},
        ],
        temperature=0.25,
        max_tokens=900,
    )
    return r.choices[0].message.content or ""

# Settings + OpenAI
try:
    settings = get_settings()
    clients = make_clients(settings.openai_api_key)
except Exception as e:
    st.error(str(e))
    st.stop()

with st.sidebar:
    st.markdown("### Controls")
    category = st.selectbox("arXiv category", ["cs.AI", "cs.CL", "cs.LG", "cs.IR", "cs.CV", "stat.ML"], index=0)
    max_results = st.slider("Max papers", 10, 50, 20, step=5)
    keywords = st.text_input("Optional keywords (no URL needed)", value="agents tool use multimodal")
    use_web_signals = st.toggle("Add optional web signals (Perplexity)", value=False)
    debug = st.toggle("Debug mode", value=False)

    chat_model = st.text_input("OpenAI chat model", value=settings.openai_chat_model)
    embed_model = st.text_input("OpenAI embedding model", value=settings.openai_embed_model)

    if use_web_signals and not settings.perplexity_api_key:
        st.warning("PERPLEXITY_API_KEY not set. Web signals will be skipped.")

colL, colR = st.columns([1.1, 0.9], gap="large")

with colL:
    st.markdown("### 1) Fetch trending papers (no URLs to paste)")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fetch_btn = st.button("📥 Fetch Papers", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if fetch_btn:
        with st.spinner("Fetching latest arXiv papers…"):
            try:
                papers = fetch_papers(category=category, max_results=max_results, keyword_query=keywords)
                st.session_state["papers"] = papers
                st.session_state["briefing"] = ""
                st.session_state["web_signals"] = ""
                st.session_state["chat"] = []
                build_paper_index(clients.openai, embed_model, papers)
                st.success(f"Loaded {len(papers)} papers.")
            except Exception as e:
                st.error(f"Failed to fetch papers: {e}")

    papers: List[Paper] = st.session_state.get("papers", [])
    if papers:
        st.markdown("### 2) Paper list")
        for i, p in enumerate(papers, start=1):
            title_line = join_nonempty([f"P{i}", clip(p.title, 110)])
            with st.expander(title_line, expanded=(i <= 2)):
                st.markdown(f"**arXiv:** {p.arxiv_id}")
                st.markdown(f"**Published:** {p.published or 'n/a'}")
                st.markdown(f"**Authors:** {', '.join(p.authors[:8])}{'…' if len(p.authors) > 8 else ''}")
                st.markdown(f"**Abstract:** {p.summary}")
                st.markdown(f"**Links:** {p.abs_url}  |  {p.pdf_url}")

        st.markdown("### 3) Industry Briefing")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        brief_btn = st.button("🧠 Generate Briefing", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if brief_btn:
            with st.spinner("Synthesizing briefing from abstracts…"):
                try:
                    st.session_state["briefing"] = generate_briefing(clients.openai, chat_model, papers)
                    st.success("Briefing ready.")
                except Exception as e:
                    st.error(f"Failed to generate briefing: {e}")

        if st.session_state.get("briefing"):
            st.markdown(st.session_state["briefing"])

        if use_web_signals and papers and settings.perplexity_api_key:
            st.markdown("### 4) Optional web signals (Perplexity)")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            ws_btn = st.button("🌐 Fetch Web Signals", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if ws_btn:
                with st.spinner("Pulling recent web signals…"):
                    try:
                        theme_seed = st.session_state.get("briefing") or ("Themes: " + (keywords or category))
                        st.session_state["web_signals"] = web_signals(
                            settings.perplexity_api_key,
                            model=settings.pplx_model,
                            theme_summary=theme_seed[:3500],
                        )
                        st.success("Web signals ready.")
                    except PerplexityError as e:
                        st.error(f"Perplexity failed: {e}")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

            if st.session_state.get("web_signals"):
                st.markdown(st.session_state["web_signals"])

        if debug:
            st.markdown("### Debug")
            st.write(f"papers={len(papers)}")
            st.write(f"index_ready={st.session_state.get('paper_vectors') is not None}")

with colR:
    st.markdown("### 5) Chat with papers (RAG + citations)")
    if not papers:
        st.info("Fetch papers first.")
    else:
        for m in st.session_state["chat"]:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        q = st.chat_input("Ask: 'What are the top agent patterns and what should I build next?'")
        if q:
            st.session_state["chat"].append({"role":"user","content":q})
            with st.chat_message("user"):
                st.markdown(q)

            with st.chat_message("assistant"):
                with st.spinner("Retrieving evidence from papers + answering…"):
                    try:
                        ans = answer_question(clients.openai, chat_model, embed_model, q)
                    except Exception as e:
                        ans = f"Sorry — error: {e}"
                st.markdown(ans)

            st.session_state["chat"].append({"role":"assistant","content":ans})

st.markdown("---")
st.caption("ArxivPulse pulls live research from arXiv, synthesizes an industry briefing with OpenAI, and optionally adds web signals with Perplexity. Never commit your API keys.")
