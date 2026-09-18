"""Central configuration for the HREA RAG application.

Everything is overridable through environment variables so the same code runs
on a laptop demo and on a server without edits.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _env(name, default):
    return os.environ.get(name, default)


# --- Storage -------------------------------------------------------------
DATA_DIR = _env("HREA_DATA_DIR", os.path.join(BASE_DIR, "data"))
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")
COLLECTION_NAME = _env("HREA_COLLECTION", "hrea_documents")

# --- Embedding model -----------------------------------------------------
# all-MiniLM-L6-v2 is small (~80 MB), fast and runs fully offline on CPU.
# Swap to e.g. "BAAI/bge-small-en-v1.5" for higher quality (see README).
EMBEDDING_MODEL = _env("HREA_EMBED_MODEL", "all-MiniLM-L6-v2")

# --- Chunking ------------------------------------------------------------
CHUNK_SIZE = int(_env("HREA_CHUNK_SIZE", "800"))        # characters
CHUNK_OVERLAP = int(_env("HREA_CHUNK_OVERLAP", "150"))  # characters

# --- Retrieval -----------------------------------------------------------
TOP_K = int(_env("HREA_TOP_K", "5"))
# Reciprocal Rank Fusion constant (standard value from the literature).
RRF_K = int(_env("HREA_RRF_K", "60"))
# How many candidates each retriever contributes before fusion.
CANDIDATE_POOL = int(_env("HREA_CANDIDATE_POOL", "20"))

# --- Upload limits -------------------------------------------------------
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".html", ".htm", ".csv", ".txt", ".md"}
MAX_CONTENT_LENGTH = int(_env("HREA_MAX_MB", "64")) * 1024 * 1024


def ensure_dirs():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(CHROMA_DIR, exist_ok=True)
