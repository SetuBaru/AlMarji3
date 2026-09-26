import chromadb
import ollama

from config import (
    CHROMA_DIR,
    HADITH_COLLECTION,
    QURAN_COLLECTION,
    EMBEDDING_MODEL,
    OLLAMA_HOST,
    HADITH_TOP_K,
    QURAN_TOP_K,
)


# ============================================================
# Constants
# ============================================================

MAX_TOP_K = 20


# ============================================================
# Islamic Retrieval Engine
# ============================================================

class IslamicRAG:
    """
    Retrieval-only Quran + Hadith semantic search.

    IMPORTANT:
    This class does NOT generate answers.

    Ollama is used only for creating query embeddings.
    ChromaDB is used for retrieving relevant Quran/Hadith
    documents.

    There is no ollama.chat(), no LLM generation, and no
    synthesized religious answer.
    """

    # ========================================================
    # Initialization
    # ========================================================

    def __init__(self):

        # ====================================================
        # Ollama
        #
        # Ollama is ONLY used for embeddings.
        # ====================================================

        self.ollama = ollama.Client(
            host=OLLAMA_HOST
        )

        # Verify Ollama is available
        self.ollama.list()

        # ====================================================
        # ChromaDB
        # ====================================================

        self.chroma = (
            chromadb.PersistentClient(
                path=str(CHROMA_DIR)
            )
        )

        # ====================================================
        # Collections
        # ====================================================

        self.hadith_collection = (
            self.chroma.get_collection(
                HADITH_COLLECTION
            )
        )

        self.quran_collection = (
            self.chroma.get_collection(
                QURAN_COLLECTION
            )
        )

    # ========================================================
    # Source routing
    # ========================================================

    def detect_source(
        self,
        question,
    ):
        """
        Automatically determine which collection(s)
        should be searched.

        Returns:
            "hadith"
            "quran"
            "both"
        """

        q = (
            str(question)
            .lower()
            .strip()
        )

        # ====================================================
        # Hadith indicators
        # ====================================================

        hadith_terms = [
            "hadith",
            "hadeeth",
            "hadiths",
            "hadeeths",
            "sunnah",

            "prophet said",
            "prophet say",
            "prophet says",

            "what did the prophet say",
            "what does the prophet say",

            "messenger said",
            "messenger say",
            "messenger says",

            "what did the messenger say",
            "what does the messenger say",
        ]

        # ====================================================
        # Quran indicators
        # ====================================================

        quran_terms = [
            "quran",
            "qur'an",
            "koran",

            "ayah",
            "ayat",

            "surah",
            "surat",

            "quran verse",
            "quran verses",

            "allah says",
            "allah say",
            "allah said",

            "what does allah say",
            "what did allah say",
            "what allah says",

            "god says",
            "god say",
            "god said",

            "what does god say",
            "what did god say",
            "what god says",
        ]

        wants_hadith = any(
            term in q
            for term in hadith_terms
        )

        wants_quran = any(
            term in q
            for term in quran_terms
        )

        # ====================================================
        # Routing
        # ====================================================

        if (
            wants_hadith
            and wants_quran
        ):
            return "both"

        if wants_hadith:
            return "hadith"

        if wants_quran:
            return "quran"

        # General Islamic question:
        # search both collections.
        return "both"

    # ========================================================
    # Dynamic Hadith count
    # ========================================================

    def get_hadith_top_k(
        self,
        question,
    ):
        """
        If the user explicitly requests ONE Hadith,
        return one result.

        Otherwise return HADITH_TOP_K.
        """

        q = (
            str(question)
            .lower()
            .strip()
        )

        singular_patterns = [
            "a hadith",
            "a hadeeth",

            "one hadith",
            "one hadeeth",

            "give me a hadith",
            "give me a hadeeth",

            "show me a hadith",
            "show me a hadeeth",

            "provide a hadith",
            "provide a hadeeth",

            "tell me a hadith",
            "tell me a hadeeth",
        ]

        if any(
            pattern in q
            for pattern in singular_patterns
        ):
            return 1

        return HADITH_TOP_K

    # ========================================================
    # Embedding
    # ========================================================

    def embed_query(
        self,
        query,
    ):
        """
        Convert the user's query into an embedding.

        This is the ONLY Ollama model operation used
        by this retrieval engine.
        """

        response = self.ollama.embed(
            model=EMBEDDING_MODEL,
            input=query,
        )

        embeddings = response.get(
            "embeddings"
        )

        if not embeddings:

            raise RuntimeError(
                "Ollama returned no embeddings."
            )

        return embeddings[0]

    # ========================================================
    # Hadith quality filtering
    # ========================================================

    @staticmethod
    def is_useless_document(
        document,
    ):
        """
        Detect Hadith records that cannot stand alone.

        Examples:

        "See previous hadith."

        "A hadith like this is transmitted on the
        authority of Nafi'."

        These records may be valid in the original books,
        but are poor standalone RAG retrieval results.
        """

        if not document:
            return True

        normalized = (
            str(document)
            .lower()
            .strip()
        )

        # ====================================================
        # Extremely short records
        # ====================================================

        if len(normalized) < 10:
            return True

        # ====================================================
        # Known cross-reference patterns
        # ====================================================

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

        if any(
            pattern in normalized
            for pattern in useless_patterns
        ):
            return True

        # ====================================================
        # Generic short cross-reference detector
        # ====================================================

        words = normalized.split()

        if len(words) < 30:

            reference_words = [
                "similar",
                "same",
                "previous",
                "narrated",
                "transmitted",
                "authority",
                "above",
                "preceding",
                "version",
                "chain",
            ]

            reference_count = sum(
                1
                for word in reference_words
                if word in normalized
            )

            if reference_count >= 2:
                return True

        return False

    # ========================================================
    # Query Chroma collection
    # ========================================================

    def query_collection(
        self,
        collection,
        embedding,
        top_k,
        filter_useless=False,
    ):
        """
        Search a ChromaDB collection.

        We retrieve more candidates than top_k because
        some Hadith results may be incomplete
        cross-reference records.

        Example:

            top_k = 3

            candidate_count = 15

        Chroma retrieves 15 candidates internally.

        After filtering, ONLY the best 3 valid documents
        are returned.
        """

        collection_count = (
            collection.count()
        )

        if collection_count == 0:
            return []

        # ====================================================
        # Retrieve additional candidates
        # ====================================================

        candidate_count = max(
            top_k * 5,
            top_k,
        )

        candidate_count = min(
            candidate_count,
            collection_count,
        )

        # ====================================================
        # Chroma query
        # ====================================================

        response = collection.query(
            query_embeddings=[
                embedding
            ],
            n_results=candidate_count,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        documents = (
            response.get(
                "documents"
            )
            or [[]]
        )[0]

        metadatas = (
            response.get(
                "metadatas"
            )
            or [[]]
        )[0]

        distances = (
            response.get(
                "distances"
            )
            or [[]]
        )[0]

        # ====================================================
        # Build results
        # ====================================================

        items = []

        for (
            document,
            metadata,
            distance,
        ) in zip(
            documents,
            metadatas,
            distances,
        ):

            # ================================================
            # Filter incomplete Hadith records
            # ================================================

            if (
                filter_useless
                and self.is_useless_document(
                    document
                )
            ):
                continue

            items.append({
                "document": document,
                "metadata": (
                    metadata or {}
                ),
                "distance": distance,
            })

            # ================================================
            # Final result count
            #
            # candidate_count may be 25, but top_k=5 means
            # ONLY 5 results are returned.
            # ================================================

            if len(items) >= top_k:
                break

        return items

    # ========================================================
    # Retrieval
    # ========================================================

    def retrieve(
        self,
        question,
        source=None,
        top_k=None,
    ):
        """
        Retrieve source documents ONLY.

        No answer generation occurs.

        Parameters
        ----------
        question:
            User's search query.

        source:
            None / "auto"
                Automatically determine source.

            "quran"
                Search Quran only.

            "hadith"
                Search Hadith only.

            "both"
                Search Quran and Hadith.

            "all"
                Alias for "both".

        top_k:
            Maximum number of results returned PER
            searched collection.

            If None, configured defaults are used.
        """

        # ====================================================
        # Validate question
        # ====================================================

        question = (
            str(question)
            .strip()
        )

        if not question:

            raise ValueError(
                "Question cannot be empty."
            )

        # ====================================================
        # Determine route
        # ====================================================

        if source is not None:

            source = (
                str(source)
                .lower()
                .strip()
            )

        if source in {
            None,
            "",
            "auto",
        }:

            route = self.detect_source(
                question
            )

        elif source in {
            "quran",
            "hadith",
            "both",
            "all",
        }:

            route = source

        else:

            raise ValueError(
                "Invalid source. "
                "Expected auto, quran, "
                "hadith, both, or all."
            )

        # "all" and "both" are equivalent
        if route == "all":
            route = "both"

        # ====================================================
        # Determine result counts
        # ====================================================

        if top_k is not None:

            try:

                requested_top_k = int(
                    top_k
                )

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    "top_k must be an integer."
                )

            requested_top_k = max(
                1,
                min(
                    requested_top_k,
                    MAX_TOP_K,
                ),
            )

            quran_top_k = (
                requested_top_k
            )

            hadith_top_k = (
                requested_top_k
            )

        else:

            quran_top_k = (
                QURAN_TOP_K
            )

            # Preserve your existing behavior:
            # "Give me a hadith..." -> one Hadith.
            hadith_top_k = (
                self.get_hadith_top_k(
                    question
                )
            )

        # ====================================================
        # Create ONE embedding
        # ====================================================

        embedding = self.embed_query(
            question
        )

        # ====================================================
        # Result object
        # ====================================================

        results = {
            "route": route,
            "quran": [],
            "hadith": [],
        }

        # ====================================================
        # Quran retrieval
        # ====================================================

        if route in {
            "quran",
            "both",
        }:

            results["quran"] = (
                self.query_collection(
                    collection=(
                        self.quran_collection
                    ),
                    embedding=embedding,
                    top_k=quran_top_k,
                    filter_useless=False,
                )
            )

        # ====================================================
        # Hadith retrieval
        # ====================================================

        if route in {
            "hadith",
            "both",
        }:

            results["hadith"] = (
                self.query_collection(
                    collection=(
                        self.hadith_collection
                    ),
                    embedding=embedding,
                    top_k=hadith_top_k,
                    filter_useless=True,
                )
            )

        return results

    # ========================================================
    # Compatibility query method
    # ========================================================

    def query(
        self,
        question,
        source=None,
        top_k=None,
    ):
        """
        Compatibility wrapper for code that calls rag.query().

        IMPORTANT:
        This still performs retrieval ONLY.

        There is deliberately no "answer" field because no
        answer has been generated.
        """

        retrieved = self.retrieve(
            question=question,
            source=source,
            top_k=top_k,
        )

        return {
            "retrieved": retrieved
        }