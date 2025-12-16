from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import xml.etree.ElementTree as ET
import httpx

ARXIV_API = "https://export.arxiv.org/api/query"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

@dataclass
class Paper:
    arxiv_id: str
    title: str
    summary: str
    published: str
    updated: str
    authors: List[str]
    abs_url: str
    pdf_url: str

def _text(el: Optional[ET.Element]) -> str:
    return (el.text or "").strip() if el is not None else ""

def fetch_papers(
    *,
    category: str,
    max_results: int = 20,
    keyword_query: str | None = None,
    timeout_s: float = 25.0,
) -> List[Paper]:
    q = f"cat:{category}"
    if keyword_query and keyword_query.strip():
        words = [w for w in keyword_query.strip().split() if w]
        if words:
            q += " AND " + " AND ".join([f'all:"{w}"' for w in words])

    params = {
        "search_query": q,
        "start": 0,
        "max_results": int(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    with httpx.Client(timeout=timeout_s, headers={"User-Agent": "ArxivPulse/1.0 (Streamlit app)"}) as client:
        r = client.get(ARXIV_API, params=params)
        r.raise_for_status()

    root = ET.fromstring(r.text)

    papers: List[Paper] = []
    for entry in root.findall("atom:entry", NS):
        id_url = _text(entry.find("atom:id", NS))
        arxiv_id = id_url.rsplit("/", 1)[-1]

        title = _text(entry.find("atom:title", NS)).replace("\n", " ")
        summary = _text(entry.find("atom:summary", NS)).replace("\n", " ")
        published = _text(entry.find("atom:published", NS))
        updated = _text(entry.find("atom:updated", NS))

        authors = []
        for a in entry.findall("atom:author", NS):
            authors.append(_text(a.find("atom:name", NS)))

        abs_url = id_url
        pdf_url = ""
        for link in entry.findall("atom:link", NS):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
                break
        if not pdf_url and abs_url:
            pdf_url = abs_url.replace("/abs/", "/pdf/") + ".pdf"

        papers.append(Paper(
            arxiv_id=arxiv_id,
            title=title,
            summary=summary,
            published=published,
            updated=updated,
            authors=authors,
            abs_url=abs_url,
            pdf_url=pdf_url,
        ))

    return papers
