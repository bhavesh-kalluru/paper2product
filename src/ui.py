from __future__ import annotations
import streamlit as st

def inject_css() -> None:
    st.markdown(
        """<style>
        .stApp{
          background:
            radial-gradient(1000px 700px at 12% 12%, rgba(34,197,94,.18), transparent 55%),
            radial-gradient(1000px 700px at 88% 15%, rgba(59,130,246,.16), transparent 55%),
            radial-gradient(900px 600px at 70% 90%, rgba(168,85,247,.12), transparent 55%);
        }
        .hero{
          border:1px solid rgba(255,255,255,.08);
          background:linear-gradient(135deg, rgba(34,197,94,.18), rgba(59,130,246,.10));
          border-radius:22px;
          padding:18px 18px 14px 18px;
          box-shadow:0 14px 34px rgba(0,0,0,.28);
        }
        .title{font-size:34px;font-weight:900;line-height:1.05;margin:0 0 6px 0;}
        .sub{font-size:14px;opacity:.88;margin:0;}
        .pill{
          display:inline-block;padding:6px 10px;border-radius:999px;
          font-size:12px;border:1px solid rgba(255,255,255,.10);
          background:rgba(255,255,255,.04);margin-right:8px;margin-top:10px;
        }
        .card{
          border:1px solid rgba(255,255,255,.08);
          background:rgba(16,22,43,.68);
          border-radius:18px;
          padding:14px 14px 10px 14px;
        }
        .kpi{
          border:1px solid rgba(255,255,255,.08);
          background:rgba(255,255,255,.03);
          border-radius:16px;
          padding:12px 12px;
        }
        div.stButton>button{
          border-radius:14px;
          padding:.65rem .9rem;
          border:1px solid rgba(255,255,255,.10);
        }
        a{text-decoration:none;}
        </style>""",
        unsafe_allow_html=True
    )

def hero() -> None:
    st.markdown(
        """<div class="hero">
          <div class="title">ArxivPulse</div>
          <p class="sub">Trending AI research → industry briefing + RAG Q&amp;A. No URLs to paste. Deployable on Render.</p>
          <span class="pill">📚 arXiv live feed</span>
          <span class="pill">🧠 RAG + citations</span>
          <span class="pill">⚡ Build ideas</span>
          <span class="pill">🌐 optional web signals</span>
        </div>""",
        unsafe_allow_html=True
    )

def sidebar_help() -> None:
    st.sidebar.markdown("### Quick starts")
    st.sidebar.markdown(
        """- Pick a category (or add keywords)  
- Click **Fetch Papers**  
- Generate **Industry Briefing**  
- Ask questions in **Chat**"""
    )
