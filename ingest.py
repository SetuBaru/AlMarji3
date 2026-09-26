import sys

import chromadb
import ollama
import pandas as pd
from tqdm import tqdm

from config import (
    HADITH_CSV,
    QURAN_TAFSEER_CSV,
    CHROMA_DIR,
    HADITH_COLLECTION,
    QURAN_COLLECTION,
    EMBEDDING_MODEL,
    OLLAMA_HOST,
    EMBED_BATCH_SIZE,
)


# ============================================================
# Helpers
# ============================================================

def clean_string(value):
    """
    Safely convert a value to a stripped string.
    """

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value).strip()


def clean_text(value):
    """
    Normalize whitespace in textual fields.
    """

    text = clean_string(value)

    return " ".join(text.split())


def get_ollama_client():
    """
    Create and verify Ollama client.
    """

    client = ollama.Client(
        host=OLLAMA_HOST
    )

    client.list()

    return client


def get_chroma_client():
    """
    Open persistent Chroma database.
    """

    return chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


def recreate_collection(
    client,
    collection_name,
    description,
):
    """
    Delete and recreate a specific collection.
    """

    try:
        client.delete_collection(
            collection_name
        )

        print(
            f"Deleted existing collection: "
            f"{collection_name}"
        )

    except Exception:
        pass

    return client.create_collection(
        name=collection_name,
        metadata={
            "description": description,
            "embedding_model": EMBEDDING_MODEL,
        },
    )


# ============================================================
# Batch embedding
# ============================================================

def embed_and_store(
    ollama_client,
    collection,
    records,
    description,
):

    print(
        f"\nEmbedding {len(records):,} "
        f"{description} records..."
    )

    for start in tqdm(
        range(
            0,
            len(records),
            EMBED_BATCH_SIZE,
        ),
        desc=description,
    ):

        batch = records[
            start:start + EMBED_BATCH_SIZE
        ]

        documents = [
            record["document"]
            for record in batch
        ]

        response = ollama_client.embed(
            model=EMBEDDING_MODEL,
            input=documents,
        )

        embeddings = response[
            "embeddings"
        ]

        collection.add(
            ids=[
                record["id"]
                for record in batch
            ],
            documents=documents,
            embeddings=embeddings,
            metadatas=[
                record["metadata"]
                for record in batch
            ],
        )


# ============================================================
# Hadith ingestion
#
# DO NOT RUN unless rebuilding the Hadith DB intentionally.
# ============================================================

def ingest_hadith(
    ollama_client,
    chroma_client,
):

    print("\n" + "=" * 70)
    print("HADITH")
    print("=" * 70)

    print(f"Loading: {HADITH_CSV}")

    df = pd.read_csv(
        HADITH_CSV,
        encoding="utf-8-sig",
        low_memory=False,
    )

    print(f"Rows: {len(df):,}")

    records = []
    skipped = 0

    # --------------------------------------------------------
    # Cross-reference records that are not useful as
    # standalone Hadith.
    # --------------------------------------------------------

    useless_patterns = [
        "see previous hadith",
        "see the previous hadith",
        "see previous hadeeth",
        "see the previous hadeeth",
        "see previous tradition",
        "see the previous tradition",

        "a hadith like this is narrated",
        "a hadith like this was narrated",
        "a hadith like this is transmitted",
        "a hadith like this was transmitted",

        "a similar hadith is narrated",
        "a similar hadith was narrated",
        "a similar hadith is transmitted",
        "a similar hadith was transmitted",

        "the same hadith is narrated",
        "the same hadith was narrated",
        "the same hadith is transmitted",
        "the same hadith was transmitted",

        "this hadith has been narrated",
        "this hadith was narrated",
        "this hadith has been transmitted",
        "this hadith was transmitted",

        "the same tradition is narrated",
        "the same tradition was narrated",

        "a similar tradition is narrated",
        "a similar tradition was narrated",

        "the above hadith",
        "the preceding hadith",
        "the foregoing hadith",
    ]

    for index, row in df.iterrows():

        text = clean_text(
            row.get("text_en")
        )

        # ----------------------------------------------------
        # Skip empty English Hadith
        # ----------------------------------------------------

        if not text:
            skipped += 1
            continue

        normalized = text.lower()

        # ----------------------------------------------------
        # Skip cross-reference-only Hadith
        # ----------------------------------------------------

        if any(
            pattern in normalized
            for pattern in useless_patterns
        ):
            skipped += 1
            continue

        # ----------------------------------------------------
        # Additional short cross-reference detection
        # ----------------------------------------------------

        words = normalized.split()

        if len(words) < 30:

            reference_terms = [
                "similar",
                "same",
                "previous",
                "preceding",
                "above",
                "narrated",
                "transmitted",
                "authority",
                "version",
                "chain",
            ]

            reference_count = sum(
                1
                for term in reference_terms
                if term in normalized
            )

            if reference_count >= 2:
                skipped += 1
                continue

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        source = clean_string(
            row.get("source")
        )

        chapter = clean_string(
            row.get("chapter")
        )

        metadata = {
            "type": "hadith",

            "hadith_id": clean_string(
                row.get("hadith_id")
            ),

            "source": source,

            "chapter_no": clean_string(
                row.get("chapter_no")
            ),

            "hadith_no": clean_string(
                row.get("hadith_no")
            ),

            "chapter": chapter,

            "chain_indx": clean_string(
                row.get("chain_indx")
            ),
        }

        records.append({
            "id": f"hadith_{index}",
            "document": text,
            "metadata": metadata,
        })

    print(
        f"Valid Hadith: {len(records):,}"
    )

    print(
        f"Skipped: {skipped:,}"
    )

    collection = recreate_collection(
        chroma_client,
        HADITH_COLLECTION,
        "English Hadith",
    )

    embed_and_store(
        ollama_client,
        collection,
        records,
        "Hadith",
    )

    print(
        f"Stored: {collection.count():,}"
    )


# ============================================================
# Quran + Tafsir ingestion
# ============================================================

def ingest_quran(
    ollama_client,
    chroma_client,
):

    print("\n" + "=" * 70)
    print("QURAN + TAFSIR")
    print("=" * 70)

    print(
        f"Loading: {QURAN_TAFSEER_CSV}"
    )

    df = pd.read_csv(
        QURAN_TAFSEER_CSV,
        encoding="utf-8-sig",
        low_memory=False,
    )

    print(f"Rows: {len(df):,}")

    records = []
    skipped = 0

    for index, row in df.iterrows():

        name = clean_string(
            row.get("Name")
        )

        surah = clean_string(
            row.get("Surah")
        )

        ayah = clean_string(
            row.get("Ayat")
        )

        verse = clean_text(
            row.get("Verse")
        )

        tafseer = clean_text(
            row.get("Tafseer")
        )

        # ----------------------------------------------------
        # Skip completely empty records
        # ----------------------------------------------------

        if not verse and not tafseer:
            skipped += 1
            continue

        # ----------------------------------------------------
        # Document sent to embedding model
        # ----------------------------------------------------

        document = f"""
Quran Verse:
{verse}

Tafsir:
{tafseer}
""".strip()

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        metadata = {
            "type": "quran",
            "surah_name": name,
            "surah": surah,
            "ayah": ayah,
        }

        records.append({
            "id": f"quran_{surah}_{ayah}_{index}",
            "document": document,
            "metadata": metadata,
        })

    print(
        f"Valid Quran verses: "
        f"{len(records):,}"
    )

    print(
        f"Skipped: {skipped:,}"
    )

    collection = recreate_collection(
        chroma_client,
        QURAN_COLLECTION,
        "English Quran with Tafsir",
    )

    embed_and_store(
        ollama_client,
        collection,
        records,
        "Quran",
    )

    print(
        f"Stored: {collection.count():,}"
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("ISLAMIC KNOWLEDGE RAG INGESTION")
    print("=" * 70)

    # --------------------------------------------------------
    # Ollama
    # --------------------------------------------------------

    try:

        ollama_client = (
            get_ollama_client()
        )

        print("Ollama is available.")

    except Exception as e:

        print(
            "Could not connect to Ollama."
        )

        print(e)

        sys.exit(1)

    # --------------------------------------------------------
    # ChromaDB
    # --------------------------------------------------------

    chroma_client = (
        get_chroma_client()
    )

    # ========================================================
    # Hadith
    #
    # IMPORTANT:
    #
    # Your Hadith collection is already embedded.
    # Leave this commented out unless you intentionally want
    # to rebuild it.
    #
    # Rebuilding it may take a long time.
    # ========================================================

    # ingest_hadith(
    #     ollama_client,
    #     chroma_client,
    # )

    # ========================================================
    # Quran + Tafsir
    # ========================================================
    #
    # If Quran is already successfully embedded, you can also
    # comment this out to avoid rebuilding it.
    # ========================================================

    # ingest_quran(
    #    ollama_client,
    #    chroma_client,
    # )

    print("\n" + "=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()