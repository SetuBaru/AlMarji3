import logging
import os

import pandas as pd

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
)

from flask_cors import CORS

from config import (
    QURAN_TAFSEER_CSV,
)

from rag import IslamicRAG


# ============================================================
# Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "AlMarji3-API"
)


# ============================================================
# Flask
# ============================================================

app = Flask(
    __name__,
    static_folder=".",
)

CORS(app)


# ============================================================
# RAG singleton
# ============================================================

rag_instance = None


def get_rag():
    """
    Initialize the retrieval engine once.

    IMPORTANT:
    IslamicRAG is retrieval-only.

    Ollama is used by rag.py only for embeddings.
    No chat/generation model is called.
    """

    global rag_instance

    if rag_instance is None:

        try:

            logger.info(
                "Initializing retrieval engine..."
            )

            rag_instance = IslamicRAG()

            logger.info(
                "Retrieval engine ready."
            )

        except Exception:

            logger.exception(
                "Could not initialize retrieval engine."
            )

            rag_instance = None

    return rag_instance


# ============================================================
# Quran dataframe
#
# This is used only by the direct Quran API endpoints.
# It is NOT used for answer generation.
# ============================================================

quran_df = None


def load_quran_dataframe():
    """
    Load Quran + Tafsir CSV for direct Quran endpoints.
    """

    global quran_df

    try:

        if not os.path.exists(
            str(QURAN_TAFSEER_CSV)
        ):

            logger.warning(
                "Quran CSV not found: %s",
                QURAN_TAFSEER_CSV,
            )

            return

        quran_df = pd.read_csv(
            QURAN_TAFSEER_CSV,
            encoding="utf-8-sig",
            low_memory=False,
        )

        logger.info(
            "Loaded Quran dataset: %s rows",
            f"{len(quran_df):,}",
        )

    except Exception:

        logger.exception(
            "Could not load Quran CSV."
        )

        quran_df = None


load_quran_dataframe()


# ============================================================
# Helpers
# ============================================================

def safe_distance(value):
    """
    Convert Chroma distance to float.

    Missing distances are sorted last.
    """

    if value is None:
        return float("inf")

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return float("inf")


def clean_metadata(metadata):
    """
    Ensure metadata is always a dictionary.
    """

    if isinstance(
        metadata,
        dict,
    ):
        return metadata

    return {}


def format_quran_answer(
    item,
    number,
):
    """
    Format one retrieved Quran document.

    IMPORTANT:
    The actual document text is copied directly from
    ChromaDB. Nothing is summarized or rewritten.
    """

    metadata = clean_metadata(
        item.get("metadata")
    )

    document = str(
        item.get(
            "text",
            ""
        )
        or ""
    ).strip()

    surah_name = str(
        metadata.get(
            "surah_name",
            "Quran",
        )
        or "Quran"
    )

    surah = str(
        metadata.get(
            "surah",
            "?",
        )
        or "?"
    )

    ayah = str(
        metadata.get(
            "ayah",
            "?",
        )
        or "?"
    )

    return (
        f"### {number}. Quran — "
        f"{surah_name} ({surah}:{ayah})\n\n"
        f"{document}"
    )


def format_hadith_answer(
    item,
    number,
):
    """
    Format one retrieved Hadith document.

    IMPORTANT:
    The Hadith text is copied directly from ChromaDB.
    Nothing is summarized or rewritten.
    """

    metadata = clean_metadata(
        item.get("metadata")
    )

    document = str(
        item.get(
            "text",
            ""
        )
        or ""
    ).strip()

    source = str(
        metadata.get(
            "source",
            "Hadith",
        )
        or "Hadith"
    )

    hadith_no = str(
        metadata.get(
            "hadith_no",
            "Unknown",
        )
        or "Unknown"
    )

    chapter = str(
        metadata.get(
            "chapter",
            "",
        )
        or ""
    ).strip()

    header = (
        f"### {number}. "
        f"{source} — "
        f"Hadith {hadith_no}"
    )

    if chapter:

        return (
            f"{header}\n\n"
            f"**Chapter:** {chapter}\n\n"
            f"{document}"
        )

    return (
        f"{header}\n\n"
        f"{document}"
    )


def build_retrieval_answer(
    results,
    limit=3,
):
    """
    Build the center-chat response from retrieved documents.

    THIS IS NOT LLM GENERATION.

    It simply takes the top N ChromaDB results and formats
    their existing text.

    No summarization.
    No paraphrasing.
    No synthesis.
    """

    top_results = results[
        :limit
    ]

    if not top_results:

        return (
            "No relevant references found."
        ), []

    parts = []

    for number, item in enumerate(
        top_results,
        start=1,
    ):

        item_type = (
            item.get(
                "type",
                ""
            )
            .lower()
        )

        if item_type == "quran":

            formatted = (
                format_quran_answer(
                    item,
                    number,
                )
            )

        elif item_type == "hadith":

            formatted = (
                format_hadith_answer(
                    item,
                    number,
                )
            )

        else:

            # Unknown type:
            # still return the exact retrieved document.

            document = str(
                item.get(
                    "text",
                    ""
                )
                or ""
            ).strip()

            formatted = (
                f"### {number}. Source\n\n"
                f"{document}"
            )

        parts.append(
            formatted
        )

    answer = "\n\n---\n\n".join(
        parts
    )

    return (
        answer,
        top_results,
    )


# ============================================================
# Frontend
# ============================================================

@app.route("/")
def index():

    return send_from_directory(
        ".",
        "index.html",
    )


# ============================================================
# Health
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"],
)
def health():

    rag = get_rag()

    quran_count = None
    hadith_count = None

    if rag is not None:

        try:

            quran_count = (
                rag.quran_collection
                .count()
            )

            hadith_count = (
                rag.hadith_collection
                .count()
            )

        except Exception:

            logger.exception(
                "Could not read collection counts."
            )

    return jsonify({

        "status": (
            "online"
            if rag is not None
            else "degraded"
        ),

        "rag_available": (
            rag is not None
        ),

        "engine": (
            "retrieval_only"
        ),

        "generation_enabled": False,

        "collections": {

            "quran": (
                quran_count
            ),

            "hadith": (
                hadith_count
            ),
        },

        "quran_csv_loaded": (
            quran_df is not None
        ),
    })


# ============================================================
# API documentation
# ============================================================

@app.route(
    "/api/docs",
    methods=["GET"],
)
def api_docs():

    return jsonify({

        "title": (
            "Al-Marji3 Islamic "
            "Knowledge Retrieval API"
        ),

        "version": "3.1.0",

        "engine": (
            "retrieval_only"
        ),

        "generation_enabled": False,

        "description": (
            "Semantic retrieval across indexed "
            "Quran, Tafsir and Hadith sources. "
            "No LLM-generated religious answer "
            "is produced."
        ),

        "query": {

            "endpoint": (
                "/api/query"
            ),

            "method": "POST",

            "body": {

                "question": (
                    "string"
                ),

                "source": (
                    "auto | quran | "
                    "hadith | both"
                ),

                "top_k": (
                    "integer 1-20"
                ),
            },

            "example": {

                "question": (
                    "What does the Quran "
                    "say about patience?"
                ),

                "source": "quran",

                "top_k": 5,
            },

            "response": {

                "answer": (
                    "Top 3 exact retrieved "
                    "references formatted for "
                    "the chat interface."
                ),

                "retrieved": (
                    "All retrieved evidence."
                ),

                "answer_sources": (
                    "The 3 records shown "
                    "in answer."
                ),
            },
        },
    })


# ============================================================
# Main RAG retrieval endpoint
# ============================================================

@app.route(
    "/api/query",
    methods=["POST"],
)
def query():
    """
    Main semantic retrieval endpoint.

    Flow:

        question
            ↓
        source routing
            ↓
        Ollama embedding
            ↓
        ChromaDB
            ↓
        retrieved records
            ↓
        sort by distance
            ↓
        top 3 formatted as "answer"

    There is NO LLM answer generation.
    """

    # ========================================================
    # Parse request
    # ========================================================

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    # ========================================================
    # Question
    # ========================================================

    question = str(
        data.get(
            "question",
            ""
        )
        or ""
    ).strip()

    if not question:

        return jsonify({

            "success": False,

            "error": (
                "Question parameter "
                "is required."
            ),

        }), 400

    # ========================================================
    # Source
    # ========================================================

    requested_source = str(
        data.get(
            "source",
            "auto",
        )
        or "auto"
    ).strip().lower()

    valid_sources = {
        "auto",
        "quran",
        "hadith",
        "both",
        "all",
    }

    if (
        requested_source
        not in valid_sources
    ):

        return jsonify({

            "success": False,

            "error": (
                "source must be one of: "
                "auto, quran, hadith, "
                "both, all."
            ),

        }), 400

    # ========================================================
    # Normalize source
    # ========================================================

    if requested_source == "all":

        requested_source = "both"

    # None means:
    # let rag.py automatically detect the route.

    rag_source = (
        None
        if requested_source == "auto"
        else requested_source
    )

    # ========================================================
    # top_k
    #
    # This controls the evidence panel.
    #
    # The main answer is independently limited to TOP 3.
    # ========================================================

    try:

        top_k = int(
            data.get(
                "top_k",
                5,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        return jsonify({

            "success": False,

            "error": (
                "top_k must be "
                "an integer."
            ),

        }), 400

    top_k = max(
        1,
        min(
            top_k,
            20,
        ),
    )

    # ========================================================
    # Initialize retrieval engine
    # ========================================================

    rag = get_rag()

    if rag is None:

        # IMPORTANT:
        #
        # There is deliberately no fallback answer here.
        #
        # If the real retrieval engine is unavailable,
        # report the error rather than fabricate content.

        return jsonify({

            "success": False,

            "error": (
                "The retrieval engine "
                "is unavailable."
            ),

            "engine": (
                "retrieval_only"
            ),

            "generation_enabled": False,

        }), 503

    # ========================================================
    # Retrieve
    # ========================================================

    try:

        logger.info(
            "Retrieval query | "
            "source=%s | "
            "top_k=%s | "
            "question=%s",
            requested_source,
            top_k,
            question,
        )

        retrieved = rag.retrieve(
            question=question,
            source=rag_source,
            top_k=top_k,
        )

    except Exception as e:

        logger.exception(
            "RAG retrieval failed."
        )

        return jsonify({

            "success": False,

            "error": str(e),

            "engine": (
                "retrieval_only"
            ),

            "generation_enabled": False,

        }), 500

    # ========================================================
    # Format Quran records
    # ========================================================

    quran_items = []

    for item in retrieved.get(
        "quran",
        [],
    ):

        metadata = clean_metadata(
            item.get(
                "metadata"
            )
        )

        quran_items.append({

            "type": "quran",

            # ================================================
            # Exact document returned from ChromaDB
            # ================================================

            "text": (
                item.get(
                    "document",
                    ""
                )
                or ""
            ),

            "metadata": metadata,

            "distance": item.get(
                "distance"
            ),
        })

    # ========================================================
    # Format Hadith records
    # ========================================================

    hadith_items = []

    for item in retrieved.get(
        "hadith",
        [],
    ):

        metadata = clean_metadata(
            item.get(
                "metadata"
            )
        )

        hadith_items.append({

            "type": "hadith",

            # ================================================
            # Exact document returned from ChromaDB
            # ================================================

            "text": (
                item.get(
                    "document",
                    ""
                )
                or ""
            ),

            "metadata": metadata,

            "distance": item.get(
                "distance"
            ),
        })

    # ========================================================
    # Combine
    # ========================================================

    combined = (
        quran_items
        + hadith_items
    )

    # ========================================================
    # Global ranking
    #
    # Lower Chroma distance = closer semantic match.
    #
    # This is especially important for route="both".
    #
    # Example:
    #
    # Quran     0.30
    # Hadith    0.32
    # Quran     0.35
    # Hadith    0.40
    #
    # The top 3 are selected globally.
    # ========================================================

    combined.sort(
        key=lambda item: (
            safe_distance(
                item.get(
                    "distance"
                )
            )
        )
    )

    # ========================================================
    # Build TOP 3 answer
    #
    # IMPORTANT:
    #
    # This is formatting, NOT generation.
    #
    # build_retrieval_answer() copies the retrieved
    # ChromaDB documents into a Markdown string.
    # ========================================================

    answer, answer_sources = (
        build_retrieval_answer(
            combined,
            limit=3,
        )
    )

    # ========================================================
    # Log result
    # ========================================================

    logger.info(
        "Retrieval complete | "
        "route=%s | "
        "quran=%s | "
        "hadith=%s | "
        "total=%s | "
        "answer_sources=%s",
        retrieved.get(
            "route"
        ),
        len(
            quran_items
        ),
        len(
            hadith_items
        ),
        len(
            combined
        ),
        len(
            answer_sources
        ),
    )

    # ========================================================
    # Response
    # ========================================================

    return jsonify({

        "success": True,

        "question": question,

        # ====================================================
        # Main chat card
        #
        # EXACT TOP 3 RETRIEVED REFERENCES.
        # Not generated by an LLM.
        # ====================================================

        "answer": answer,

        # ====================================================
        # Route
        # ====================================================

        "route": retrieved.get(
            "route",
            requested_source,
        ),

        # ====================================================
        # Counts
        # ====================================================

        "count": len(
            combined
        ),

        "quran_count": len(
            quran_items
        ),

        "hadith_count": len(
            hadith_items
        ),

        # ====================================================
        # Full evidence
        #
        # Your right-hand "Retrieved Evidence" panel can use
        # this array.
        # ====================================================

        "retrieved": combined,

        # ====================================================
        # Exact three records displayed in the center answer.
        # ====================================================

        "answer_sources": (
            answer_sources
        ),

        # ====================================================
        # Explicit engine information
        # ====================================================

        "engine": (
            "retrieval_only"
        ),

        "generation_enabled": False,
    })


# ============================================================
# Direct Quran keyword search
#
# This searches the CSV directly.
# It does NOT use an LLM.
# ============================================================

@app.route(
    "/api/quran/search",
    methods=["GET"],
)
def search_quran():

    query_text = str(
        request.args.get(
            "q",
            ""
        )
        or ""
    ).strip()

    if not query_text:

        return jsonify({

            "success": False,

            "error": (
                "Query parameter "
                "'q' is required."
            ),

        }), 400

    if quran_df is None:

        return jsonify({

            "success": False,

            "error": (
                "Quran dataset "
                "is unavailable."
            ),

        }), 503

    # ========================================================
    # Limit
    # ========================================================

    try:

        limit = int(
            request.args.get(
                "limit",
                10,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        limit = 10

    limit = max(
        1,
        min(
            limit,
            50,
        ),
    )

    try:

        # ====================================================
        # Search available columns
        # ====================================================

        mask = pd.Series(
            False,
            index=quran_df.index,
        )

        for column in [
            "Verse",
            "Tafseer",
            "Name",
        ]:

            if (
                column
                in quran_df.columns
            ):

                mask = (
                    mask
                    |
                    quran_df[
                        column
                    ].astype(
                        str
                    ).str.contains(
                        query_text,
                        case=False,
                        na=False,
                    )
                )

        matches = (
            quran_df[
                mask
            ]
            .head(
                limit
            )
        )

        results = []

        for _, row in (
            matches.iterrows()
        ):

            surah = (
                row.get(
                    "Surah"
                )
            )

            ayah = (
                row.get(
                    "Ayat"
                )
            )

            if pd.notna(
                surah
            ):

                try:
                    surah = int(
                        surah
                    )
                except Exception:
                    surah = str(
                        surah
                    )

            else:
                surah = None

            if pd.notna(
                ayah
            ):

                try:
                    ayah = int(
                        ayah
                    )
                except Exception:
                    ayah = str(
                        ayah
                    )

            else:
                ayah = None

            verse = row.get(
                "Verse",
                "",
            )

            tafseer = row.get(
                "Tafseer",
                "",
            )

            name = row.get(
                "Name",
                "",
            )

            if pd.isna(
                verse
            ):
                verse = ""

            if pd.isna(
                tafseer
            ):
                tafseer = ""

            if pd.isna(
                name
            ):
                name = ""

            results.append({

                "type": "quran",

                "surah_name": str(
                    name
                ),

                "surah": surah,

                "ayah": ayah,

                "verse": str(
                    verse
                ),

                "tafseer": str(
                    tafseer
                ),
            })

        return jsonify({

            "success": True,

            "query": query_text,

            "count": len(
                results
            ),

            "results": results,
        })

    except Exception as e:

        logger.exception(
            "Direct Quran search failed."
        )

        return jsonify({

            "success": False,

            "error": str(e),

        }), 500


# ============================================================
# Get complete Surah
# ============================================================

@app.route(
    "/api/quran/surah/<int:surah_id>",
    methods=["GET"],
)
def get_surah(
    surah_id,
):

    if quran_df is None:

        return jsonify({

            "success": False,

            "error": (
                "Quran dataset "
                "is unavailable."
            ),

        }), 503

    if not (
        1
        <= surah_id
        <= 114
    ):

        return jsonify({

            "success": False,

            "error": (
                "Surah must be "
                "between 1 and 114."
            ),

        }), 400

    try:

        rows = quran_df[
            pd.to_numeric(
                quran_df["Surah"],
                errors="coerce",
            )
            == surah_id
        ]

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e),

        }), 500

    if rows.empty:

        return jsonify({

            "success": False,

            "error": (
                "Surah not found."
            ),

        }), 404

    name = rows.iloc[0].get(
        "Name",
        "",
    )

    if pd.isna(
        name
    ):
        name = ""

    verses = []

    for _, row in (
        rows.iterrows()
    ):

        ayah = row.get(
            "Ayat"
        )

        try:

            ayah = int(
                ayah
            )

        except Exception:

            ayah = str(
                ayah
            )

        verse = row.get(
            "Verse",
            "",
        )

        tafseer = row.get(
            "Tafseer",
            "",
        )

        if pd.isna(
            verse
        ):
            verse = ""

        if pd.isna(
            tafseer
        ):
            tafseer = ""

        verses.append({

            "ayah": ayah,

            "verse": str(
                verse
            ),

            "tafseer": str(
                tafseer
            ),
        })

    return jsonify({

        "success": True,

        "surah_id": surah_id,

        "surah_name": str(
            name
        ),

        "total_verses": len(
            verses
        ),

        "verses": verses,
    })


# ============================================================
# Collection information
# ============================================================

@app.route(
    "/api/collections",
    methods=["GET"],
)
def collections():

    rag = get_rag()

    if rag is None:

        return jsonify({

            "success": False,

            "error": (
                "Retrieval engine "
                "is unavailable."
            ),

        }), 503

    try:

        quran_count = (
            rag.quran_collection
            .count()
        )

        hadith_count = (
            rag.hadith_collection
            .count()
        )

        return jsonify({

            "success": True,

            "collections": [

                {
                    "id": "quran",
                    "name": (
                        "Quran + Tafsir"
                    ),
                    "count": (
                        quran_count
                    ),
                },

                {
                    "id": "hadith",
                    "name": (
                        "English Hadith"
                    ),
                    "count": (
                        hadith_count
                    ),
                },
            ],
        })

    except Exception as e:

        logger.exception(
            "Could not retrieve "
            "collection information."
        )

        return jsonify({

            "success": False,

            "error": str(e),

        }), 500


# ============================================================
# Static files
#
# Keep this LAST so it does not interfere with /api routes.
# ============================================================

@app.route(
    "/<path:path>"
)
def static_files(
    path,
):

    return send_from_directory(
        ".",
        path,
    )


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8000,
        )
    )

    print()
    print("=" * 70)
    print("ALMARJI3")
    print("QURAN + HADITH RETRIEVAL API")
    print("=" * 70)
    print()
    print(
        f"Server: http://localhost:{port}"
    )
    print(
        "Mode: Retrieval only"
    )
    print(
        "LLM generation: DISABLED"
    )
    print(
        "Main answer: Top 3 retrieved sources"
    )
    print()

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )