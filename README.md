# HREA RAG — High Refractory Entropy Alloy Document Search

A fast, **no-LLM** Retrieval-Augmented search engine. Upload your documents
(PDF, DOCX, PPTX, HTML, CSV, TXT, MD), ask a question in natural language, and instantly get the
most relevant passages back — with the source file, page number, and *how* each
passage matched. No API keys, no cloud calls, fully offline.

Built for the **High Refractory Entropy Alloy (RHEA)** research domain, but it
works on any collection of documents.

> Why "no LLM"? This system does **retrieval only** — it finds and ranks the
> exact passages that answer your question. There is no generative model
> hallucinating an answer; you read the source text directly. That makes it
> fast, cheap, reproducible, and citable.

## Retrieval strategy (the interesting part)

It uses **hybrid retrieval**, the current best-practice for high-quality search
without a language model:

1. **Dense / semantic search** — documents are chunked and embedded with the
   `all-MiniLM-L6-v2` model (ONNX runtime, bundled with **ChromaDB** — no
   PyTorch, ~80 MB) and stored in a ChromaDB vector database. This finds
   passages by *meaning* (e.g. "what keeps the crystal structure stable"
   matches text about "BCC phase stabilization").
2. **Sparse / keyword search** — a **BM25** index catches exact technical
   tokens that embeddings can miss (alloy formulas like `MoNbTaW`, `BCC`,
   specific temperatures).
3. **Reciprocal Rank Fusion (RRF)** — the two ranked lists are merged with
   `score = Σ 1 / (k + rank)`. RRF needs no score normalization or tuning and
   reliably beats either retriever alone.

Each result shows its RRF score, semantic similarity, BM25 score, and whether
it was found by semantic search, keyword search, or both.

## Quick start

```bash
# 1. (recommended) create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. run
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

1. Drag in one or more documents and click **Index files**
   (the first run downloads the ~80 MB embedding model — one time only).
2. Type a question and hit **Search**.

A sample document is included at
[`sample_docs/refractory_high_entropy_alloys_primer.md`](sample_docs/refractory_high_entropy_alloys_primer.md)
— upload it and try:

- *"What stabilizes the BCC phase in refractory high-entropy alloys?"*
- *"How do you improve room-temperature ductility?"*
- *"What is the yield strength of MoNbTaW at high temperature?"*

## Project layout

```
app.py                 Flask app + routes
config.py              All settings (env-overridable)
rag/
  loaders.py           PDF / DOCX / PPTX / HTML / CSV / TXT / MD loading (keeps page numbers)
  chunking.py          Recursive, overlap-aware text splitting
  embeddings.py        ChromaDB ONNX all-MiniLM-L6-v2 wrapper (lazy-loaded)
  vector_store.py      ChromaDB persistent vector store (cosine)
  bm25_index.py        In-memory BM25 sparse index
  retriever.py         Hybrid dense+sparse retrieval with RRF
  ingest.py            file -> chunks -> embeddings -> store pipeline
templates/ , static/   Web UI
sample_docs/           Example RHEA document
```

## Configuration

All settings live in `config.py` and can be overridden with environment
variables, e.g.:

| Variable | Default | Meaning |
|---|---|---|
| `HREA_CHUNK_SIZE` | `800` | chunk size in characters |
| `HREA_CHUNK_OVERLAP` | `150` | overlap between chunks |
| `HREA_TOP_K` | `5` | results returned |
| `HREA_RRF_K` | `60` | RRF constant |

## API

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/upload` | POST | multipart `files` | per-file chunk counts |
| `/query` | POST | JSON `{question, top_k}` | ranked passages + timing |
| `/documents` | GET | — | indexed sources + counts |
| `/reset` | POST | — | clears the index |

## Notes

- Uploaded files and the vector DB are stored under `data/` (git-ignored).
- This ships the Flask development server. For production use a WSGI server
  (e.g. `waitress-serve --port=5000 app:app`).

## License

MIT
