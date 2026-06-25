"""HREA RAG — Flask web application.

A no-LLM Retrieval-Augmented "search" engine: upload documents, ask a
question in natural language, and instantly get back the most relevant
passages (with source, page, and how they matched). Pure retrieval using
hybrid dense + sparse search with Reciprocal Rank Fusion — fast and fully
offline, no API keys.
"""
import os
import time
import traceback

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

import config
from rag.embeddings import Embedder
from rag.ingest import ingest_file
from rag.loaders import is_supported
from rag.retriever import HybridRetriever
from rag.vector_store import VectorStore

config.ensure_dirs()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

# Built once and shared across requests (single-process dev server).
_embedder = Embedder(config.EMBEDDING_MODEL)
_store = VectorStore(config.CHROMA_DIR, config.COLLECTION_NAME)
_retriever = HybridRetriever(_embedder, _store)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/documents")
def documents():
    return jsonify(
        {
            "documents": _store.sources(),
            "total_chunks": _store.count(),
            "embedding_model": config.EMBEDDING_MODEL,
        }
    )


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "No files provided."}), 400

    summaries, skipped = [], []
    t0 = time.perf_counter()
    for f in files:
        if not f.filename:
            continue
        if not is_supported(f.filename):
            skipped.append(f.filename)
            continue
        filename = secure_filename(f.filename)
        dest = os.path.join(config.UPLOAD_DIR, filename)
        f.save(dest)
        try:
            summaries.append(ingest_file(dest, _retriever))
        except Exception as exc:  # surface a clean message, keep server alive
            traceback.print_exc()
            skipped.append(f"{f.filename} ({exc})")

    return jsonify(
        {
            "indexed": summaries,
            "skipped": skipped,
            "total_chunks": _store.count(),
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
        }
    )


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Empty question."}), 400
    if _store.count() == 0:
        return jsonify({"error": "No documents indexed yet. Upload something first."}), 400

    top_k = int(data.get("top_k") or config.TOP_K)
    result = _retriever.search(question, top_k=top_k)
    return jsonify(result)


@app.route("/reset", methods=["POST"])
def reset():
    _store.reset()
    _retriever.rebuild_sparse()
    return jsonify({"ok": True, "total_chunks": _store.count()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=False)
