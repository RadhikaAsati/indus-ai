from collections import defaultdict

from backend.services.embeddings import model
from backend.services.vector_store import (
    search_chunks,
    collection
)


# Number of semantic matches used to discover
# potentially relevant documents.
INITIAL_RETRIEVAL = 25

# Maximum number of documents whose full stored
# context will be expanded.
MAX_DOCUMENTS = 8

# A document should normally appear more than once
# in semantic retrieval before we expand the whole file.
#
# This helps prevent one weak accidental chunk match from
# causing an unrelated document to be fully included.
MIN_MATCHED_CHUNKS = 2

# However, the strongest few documents should still be
# included even if they have only one strong matching chunk.
MIN_PRIMARY_DOCUMENTS = 3


def calculate_relevance(distance):
    """
    Convert Chroma distance into a simple relevance value.

    This score is used mainly for ranking/debugging.
    It should not be treated as a confidence percentage.
    """

    return round(
        max(
            0.0,
            1 - distance
        ),
        3
    )


def collect_evidence(question):
    """
    Build a fuller evidence packet using two-stage retrieval.

    Stage 1:
        Semantic search discovers the most relevant chunks
        and identifies the documents most likely to matter.

    Stage 2:
        The selected documents are expanded using all of
        their stored chunks from ChromaDB.

    This prevents important evidence from being lost simply
    because one section of a relevant document did not appear
    in the global top semantic results.
    """

    # -----------------------------------------------------
    # STAGE 1 — SEMANTIC DISCOVERY
    # -----------------------------------------------------

    query_embedding = model.encode(
        question
    )

    results = search_chunks(
        query_embedding,
        n_results=INITIAL_RETRIEVAL
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Store semantic matches by document.
    discovery_matches = defaultdict(list)

    # Use document + chunk number rather than only chunk text.
    # Two different documents may legitimately contain the
    # same sentence.
    seen_chunk_ids = set()

    for content, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        document_name = metadata.get(
            "document"
        )

        chunk_number = metadata.get(
            "chunk"
        )

        if document_name is None:
            continue

        chunk_id = (
            document_name,
            chunk_number
        )

        if chunk_id in seen_chunk_ids:
            continue

        seen_chunk_ids.add(
            chunk_id
        )

        discovery_matches[
            document_name
        ].append(
            {
                "chunk_number":
                    chunk_number,

                "relevance_score":
                    calculate_relevance(
                        distance
                    ),

                "distance":
                    distance,

                "content":
                    content
            }
        )

    # -----------------------------------------------------
    # RANK DISCOVERED DOCUMENTS
    # -----------------------------------------------------

    ranked_documents = []

    for document_name, matches in (
        discovery_matches.items()
    ):

        # Lower distance = stronger semantic match.
        best_distance = min(
            match["distance"]
            for match in matches
        )

        best_relevance = max(
            match["relevance_score"]
            for match in matches
        )

        ranked_documents.append(
            {
                "document":
                    document_name,

                "matched_chunks":
                    len(matches),

                "best_distance":
                    best_distance,

                "best_relevance":
                    best_relevance
            }
        )

    # Rank primarily by semantic strength.
    # If two documents are similarly strong,
    # repeated matching chunks help break the tie.
    ranked_documents.sort(
        key=lambda item: (
            item["best_distance"],
            -item["matched_chunks"]
        )
    )

    # -----------------------------------------------------
    # SELECT DOCUMENTS FOR FULL EXPANSION
    # -----------------------------------------------------

    selected_documents = []

    for index, document_info in enumerate(
        ranked_documents
    ):

        if len(
            selected_documents
        ) >= MAX_DOCUMENTS:

            break

        # Always keep the strongest few discovered docs.
        if index < MIN_PRIMARY_DOCUMENTS:

            selected_documents.append(
                document_info["document"]
            )

            continue

        # For remaining documents, require repeated semantic
        # evidence before expanding the whole document.
        if (
            document_info[
                "matched_chunks"
            ]
            >= MIN_MATCHED_CHUNKS
        ):

            selected_documents.append(
                document_info["document"]
            )

    # -----------------------------------------------------
    # STAGE 2 — EXPAND SELECTED DOCUMENTS
    # -----------------------------------------------------

    grouped_evidence = defaultdict(
        list
    )

    for document_name in selected_documents:

        document_data = collection.get(
            where={
                "document":
                    document_name
            },

            include=[
                "documents",
                "metadatas"
            ]
        )

        full_chunks = []

        for content, metadata in zip(
            document_data.get(
                "documents",
                []
            ),

            document_data.get(
                "metadatas",
                []
            )
        ):

            chunk_number = metadata.get(
                "chunk"
            )

            # If this chunk appeared in semantic discovery,
            # preserve its semantic relevance score.
            matched_chunk = next(
                (
                    match

                    for match in
                    discovery_matches[
                        document_name
                    ]

                    if match[
                        "chunk_number"
                    ]
                    == chunk_number
                ),

                None
            )

            relevance_score = (
                matched_chunk[
                    "relevance_score"
                ]

                if matched_chunk

                else None
            )

            full_chunks.append(
                {
                    "chunk_number":
                        chunk_number,

                    "relevance_score":
                        relevance_score,

                    "retrieval_type":
                        (
                            "semantic_match"

                            if matched_chunk

                            else "document_context"
                        ),

                    "content":
                        content
                }
            )

        # Restore original document order.
        full_chunks.sort(
            key=lambda chunk: (
                chunk[
                    "chunk_number"
                ]

                if chunk[
                    "chunk_number"
                ] is not None

                else 999999
            )
        )

        grouped_evidence[
            document_name
        ] = full_chunks

    # -----------------------------------------------------
    # BUILD INVESTIGATION SUMMARY
    # -----------------------------------------------------

    evidence_count = sum(
        len(chunks)

        for chunks in
        grouped_evidence.values()
    )

    semantic_match_count = sum(
        len(matches)

        for matches in
        discovery_matches.values()
    )

    investigation_packet = {

        "question":
            question,

        "summary": {

            # Documents appearing anywhere in initial
            # semantic discovery.
            "documents_discovered":
                len(
                    discovery_matches
                ),

            # Documents actually expanded and supplied
            # for investigation.
            "documents_consulted":
                len(
                    grouped_evidence
                ),

            # Number of chunks returned by initial
            # semantic retrieval.
            "semantic_matches_found":
                semantic_match_count,

            # Total chunks after selected documents
            # were expanded.
            "evidence_found":
                evidence_count,

            "retrieval_strategy":
                "semantic_discovery_then_document_expansion",

            "selected_documents":
                selected_documents
        },

        "documents":
            dict(
                grouped_evidence
            )
    }

    return investigation_packet