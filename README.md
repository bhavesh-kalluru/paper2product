# ArxivPulse — Trending AI Research → Industry Briefing (Streamlit + RAG)

**ArxivPulse** pulls **live trending papers from arXiv** (no URLs to paste), generates an **industry briefing**, and lets you chat using **RAG** with **paper citations** like **[P3]**.

Optional: add **web signals** via Perplexity — but the app works even if Perplexity is not configured.

---

## Run locally (macOS + PyCharm)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: add OPENAI_API_KEY (Perplexity optional)

streamlit run app.py
```

---

## Docker

```bash
docker build -t arxivpulse .
docker run --rm -p 8501:8501 \
  -e OPENAI_API_KEY="..." \
  -e PERPLEXITY_API_KEY="..." \
  arxivpulse
```

---

## Deploy on Render
Use the included `render.yaml` with Render Blueprint.

---

## Git: ignore `.env`
`.gitignore` already ignores `.env` and `.env.*`

If you accidentally committed `.env`:
```bash
git rm --cached .env
git commit -m "Stop tracking .env"
```

---

## About the Author
Bhavesh Kalluru  
- **5 years of experience**
- Actively looking for **full‑time GenAI / AI Engineer roles (USA)**

Links:
- GitHub: https://github.com/bhavesh-kalluru
- LinkedIn: https://www.linkedin.com/in/bhaveshkalluru/
- Portfolio: https://kbhavesh.com

