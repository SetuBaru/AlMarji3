from rag import IslamicRAG


# ============================================================
# Determine source type
# ============================================================

def determine_source_type(metadata):

    source_type = metadata.get(
        "type"
    )

    if source_type:
        return source_type

    # ========================================================
    # Backwards compatibility
    #
    # Older Hadith records may not contain:
    # "type": "hadith"
    # ========================================================

    if "hadith_no" in metadata:
        return "hadith"

    if (
        "surah" in metadata
        and "ayah" in metadata
    ):
        return "quran"

    return "unknown"


# ============================================================
# Print one result
# ============================================================

def print_item(
    item,
    number,
):

    metadata = item.get(
        "metadata",
        {}
    )

    source_type = determine_source_type(
        metadata
    )

    print(
        f"\n[{number}] "
        f"{source_type.upper()}"
    )

    distance = item.get(
        "distance"
    )

    if distance is not None:

        print(
            f"Distance: "
            f"{distance:.4f}"
        )

    # ========================================================
    # Quran
    # ========================================================

    if source_type == "quran":

        print(
            f"Surah: "
            f"{metadata.get('surah_name', 'Unknown')}"
        )

        print(
            f"Reference: "
            f"{metadata.get('surah', '?')}:"
            f"{metadata.get('ayah', '?')}"
        )

    # ========================================================
    # Hadith
    # ========================================================

    elif source_type == "hadith":

        print(
            f"Source: "
            f"{metadata.get('source', 'Unknown')}"
        )

        print(
            f"Hadith No: "
            f"{metadata.get('hadith_no', 'Unknown')}"
        )

        chapter = metadata.get(
            "chapter"
        )

        if chapter:

            print(
                f"Chapter: {chapter}"
            )

    # ========================================================
    # Document
    # ========================================================

    document = item.get(
        "document",
        ""
    )

    if document:

        print()
        print(document)


# ============================================================
# Print retrieval
# ============================================================

def print_retrieval(
    retrieved,
):

    print("\n")
    print("=" * 70)
    print("RETRIEVED SOURCES")
    print("=" * 70)

    route = retrieved.get(
        "route",
        "unknown",
    )

    print(
        f"\nQuery route: "
        f"{route.upper()}"
    )

    # ========================================================
    # Quran
    # ========================================================

    quran_results = retrieved.get(
        "quran",
        [],
    )

    if quran_results:

        print("\n--- Quran ---")

        for i, item in enumerate(
            quran_results,
            start=1,
        ):

            print_item(
                item,
                i,
            )

    # ========================================================
    # Hadith
    # ========================================================

    hadith_results = retrieved.get(
        "hadith",
        [],
    )

    if hadith_results:

        print("\n--- Hadith ---")

        for i, item in enumerate(
            hadith_results,
            start=1,
        ):

            print_item(
                item,
                i,
            )

    # ========================================================
    # No results
    # ========================================================

    if (
        not quran_results
        and not hadith_results
    ):

        print(
            "\nNo relevant sources were retrieved."
        )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("ALMARJI3")
    print("QURAN + HADITH RAG")
    print("=" * 70)

    print("\nInitializing...")

    try:

        rag = IslamicRAG()

    except Exception as e:

        print(
            "\nCould not initialize RAG."
        )

        print(
            f"Error: {e}"
        )

        return

    print("Ready.")

    print(
        "\nAsk a question about "
        "the Quran or Hadith."
    )

    print(
        "Type 'exit' or 'quit' to stop."
    )

    # ========================================================
    # Interactive loop
    # ========================================================

    while True:

        print("\n" + "-" * 70)

        question = input(
            "\nQuestion: "
        ).strip()

        if not question:
            continue

        if question.lower() in {
            "exit",
            "quit",
        }:

            print("\nGoodbye.")
            break

        try:

            # =================================================
            # Run RAG
            # =================================================

            result = rag.query(
                question
            )

            retrieved = result.get(
                "retrieved",
                {},
            )

            print_retrieval(
                retrieved
            )

        except KeyboardInterrupt:

            print("\n\nGoodbye.")
            break

        except Exception as e:

            print(
                "\nError while processing "
                "the question:"
            )

            print(
                f"{type(e).__name__}: {e}"
            )


if __name__ == "__main__":
    main()