from collections import defaultdict

from backend.services.embeddings import model
from backend.services.vector_store import search_chunks


INITIAL_RETRIEVAL = 25


def collect_evidence(question):
    """
    Retrieve evidence from ChromaDB and organize it by document.
    No evidence is discarded at this stage.
    """

    query_embedding = model.encode(question)

    results = search_chunks(
        query_embedding,
        n_results=INITIAL_RETRIEVAL
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    grouped_evidence = defaultdict(list)

    seen_chunks = set()

    for doc, meta, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Skip exact duplicate chunks
        if doc in seen_chunks:
            continue

        seen_chunks.add(doc)

        grouped_evidence[meta["document"]].append(
            {
                "chunk_number": meta["chunk"],
                "relevance_score": round(max(0.0, 1 - distance), 3),
                "content": doc
            }
        )

    evidence_count = sum(
        len(chunks)
        for chunks in grouped_evidence.values()
    )

    investigation_packet = {
        "question": question,

        "summary": {
            "documents_consulted": len(grouped_evidence),
            "evidence_found": evidence_count
        },

        "documents": dict(grouped_evidence)
    }

    return investigation_packet