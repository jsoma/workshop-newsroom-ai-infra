#uv run streamlit run 03-streamlit-pdf-search.py

import hashlib
import html
import pickle
import re
from pathlib import Path

import fitz
import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer


APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
INDEX_FILE = DATA_DIR / "pdf_search_index.pkl"
INDEX_VERSION = 9
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

st.set_page_config(page_title="PDF Search", layout="wide")
st.title("Local PDF Search")


@st.cache_resource
def load_model():
    return SentenceTransformer(MODEL_NAME)


def pdf_signature(pdf_files):
    details = []
    for pdf_file in pdf_files:
        stat = pdf_file.stat()
        relative_path = pdf_file.relative_to(PDF_DIR)
        details.append(f"{relative_path}:{stat.st_size}:{int(stat.st_mtime)}")
    return hashlib.sha256("\n".join(details).encode("utf-8")).hexdigest()


def clean_text(text):
    text = "".join(char if char.isprintable() or char == "\n" else " " for char in text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def page_text(page):
    blocks = page.get_text("blocks")
    paragraphs = []

    for block in sorted(blocks, key=lambda item: (item[1], item[0])):
        text = clean_text(block[4])
        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def extract_pages(pdf_files):
    rows = []
    progress = st.progress(0, text="Reading PDFs")

    for i, pdf_file in enumerate(pdf_files, start=1):
        try:
            with fitz.open(pdf_file) as doc:
                for page_number, page in enumerate(doc, start=1):
                    text = page_text(page)
                    rows.append(
                        {
                            "file": pdf_file.name,
                            "path": str(pdf_file.relative_to(APP_DIR)),
                            "page": page_number,
                            "text": text,
                        }
                    )
        except Exception as exc:
            st.warning(f"Could not read {pdf_file.name}: {exc}")

        progress.progress(i / len(pdf_files), text=f"Reading PDFs ({i}/{len(pdf_files)})")

    progress.empty()
    return pd.DataFrame(rows)


def build_index(pdf_files, model, rebuild=False):
    signature = pdf_signature(pdf_files)

    if INDEX_FILE.exists() and not rebuild:
        with INDEX_FILE.open("rb") as f:
            index = pickle.load(f)
        if index.get("version") == INDEX_VERSION and index["signature"] == signature:
            return index

    pages = extract_pages(pdf_files)
    if pages.empty:
        st.error("No searchable text was found in the PDFs.")
        st.stop()

    texts = pages["text"].tolist()

    with st.spinner("Building search index"):
        embeddings = model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    index = {
        "version": INDEX_VERSION,
        "signature": signature,
        "pages": pages,
        "embeddings": embeddings.astype("float32"),
    }

    with INDEX_FILE.open("wb") as f:
        pickle.dump(index, f)

    return index


def score_badge(score, low_score, high_score):
    if high_score == low_score:
        percent = 1
    else:
        percent = (score - low_score) / (high_score - low_score)

    low_color = np.array([244, 63, 94])
    high_color = np.array([22, 163, 74])
    color = ((1 - percent) * low_color + percent * high_color).astype(int)

    return (
        f"<span style='background: rgb({color[0]}, {color[1]}, {color[2]}); "
        "color: white; padding: 0.2rem 0.45rem; border-radius: 0.35rem; "
        "font-size: 0.85rem; font-weight: 700;'>"
        f"score {score:.3f}</span>"
    )


def result_card(row, score, low_score, high_score):
    title = html.escape(row["file"])
    url = html.escape(documentcloud_url(row["file"]), quote=True)
    badge = score_badge(score, low_score, high_score)
    text = html.escape(display_text(row["text"]))
    return (
        "<div style='position: relative;'>"
        "<div style='position: sticky; top: 3.75rem; z-index: 10; background: #0f141c; "
        "border-bottom: 1px solid #313846; padding: 0.25rem 0 0.7rem 0; "
        "margin-bottom: 0.7rem;'>"
        f"<div style='font-size: 1.35rem; font-weight: 800; margin-bottom: 0.35rem; "
        "line-height: 1.25;'>"
        f"<a href='{url}' target='_blank' rel='noopener noreferrer' "
        "style='color: #93c5fd; text-decoration: none;'>"
        f"{title} <span aria-hidden='true' style='font-size: 0.9em;'>↗</span></a></div>"
        f"<div style='display: flex; gap: 0.6rem; align-items: center; margin-bottom: 0.5rem;'>"
        f"<span style='color: #9ca3af;'>Page {int(row['page'])}</span>{badge}</div>"
        "</div>"
        "<div style='background: #172033; border: 1px solid #313846; "
        "border-radius: 0.45rem; padding: 0.8rem 0.9rem;'>"
        f"<div style='line-height: 1.55; white-space: pre-wrap;'>{text}</div>"
        "</div>"
        "</div>"
    )


def documentcloud_url(filename):
    return f"https://embed.documentcloud.org/documents/{Path(filename).stem}/"


def display_text(text):
    text = re.sub(r"(\d+\.?)[ \t]*\n(?:[ \t]*\n)*[ \t]*([A-Za-z]+)", r"\1 \2", text)

    lines = text.splitlines()
    display_lines = []
    pending_blank_lines = 0
    previous_line_was_short = False

    for line in lines:
        if not line:
            pending_blank_lines += 1
            continue

        current_line_is_short = len(line) <= 100
        if (
            display_lines
            and pending_blank_lines
            and not (previous_line_was_short and current_line_is_short)
        ):
            display_lines.append("")

        display_lines.append(line)
        pending_blank_lines = 0
        previous_line_was_short = current_line_is_short

    return "\n".join(display_lines)


pdf_files = sorted(PDF_DIR.rglob("*.pdf"))

if not pdf_files:
    st.error(f"No PDFs found in `{PDF_DIR}`.")
    st.stop()

with st.sidebar:
    st.header("Search")
    query = st.text_input("Search the PDFs")
    result_count = st.slider("Results", 5, 50, 20)
    rebuild_index = st.button("Refresh/rebuild local index")

model = load_model()
index = build_index(pdf_files, model, rebuild=rebuild_index)
pages = index["pages"]

st.caption(f"Searching {len(pdf_files):,} local PDFs and {len(pages):,} extracted pages.")

if not query.strip():
    st.info("Search for a person, company, agency, legal issue, or phrase.")
    st.stop()

query = query.strip()

query_embedding = model.encode([query], normalize_embeddings=True)[0].astype("float32")
scores = index["embeddings"] @ query_embedding

top_indexes = np.argsort(scores)[::-1][:result_count]
top_scores = scores[top_indexes]
low_score = top_scores.min()
high_score = top_scores.max()

st.subheader("Results")
st.caption("Semantic search ranks pages by meaning, so results may not contain the exact words you typed.")

for row_index in top_indexes:
    row = pages.iloc[row_index]
    score = scores[row_index]

    with st.container(border=True):
        st.html(result_card(row, score, low_score, high_score))
