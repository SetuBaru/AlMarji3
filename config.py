from pathlib import Path


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

HADITH_CSV = DATA_DIR / "all_hadiths_clean.csv"

QURAN_TAFSEER_CSV = (
    DATA_DIR / "Quran_English_with_Tafseer.csv"
)


CHROMA_DIR = BASE_DIR / "chroma_db"


# ============================================================
# Ollama
# ============================================================

OLLAMA_HOST = "http://localhost:11434"

EMBEDDING_MODEL = "mxbai-embed-large"
LLM_MODEL = "qwen3.5:4b"


# ============================================================
# Chroma collections
# ============================================================

HADITH_COLLECTION = "hadith_en"
QURAN_COLLECTION = "quran_tafseer_en"


# ============================================================
# Retrieval
# ============================================================

HADITH_TOP_K = 5
QURAN_TOP_K = 3


# ============================================================
# Ingestion
# ============================================================

EMBED_BATCH_SIZE = 32