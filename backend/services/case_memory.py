import json
import uuid
from datetime import datetime

import chromadb

from backend.services.embeddings import create_embeddings


# ---------------------------------------------------------
# CHROMA CONNECTION
# ---------------------------------------------------------

client = chromadb.PersistentClient(
    path="backend/chroma_db"
)

# IMPORTANT:
# Keep organizational memory separate from original documents.
memory_collection = client.get_or_create_collection(
    name="case_memories"
)


# ---------------------------------------------------------
# BUILD SAFE MEMORY
# ---------------------------------------------------------

def build_case_memory(question, case_file):
    """
    Create a safe organizational memory from an investigation.

    Confirmed facts, hypotheses, gaps, and lessons are stored
    separately so that uncertain reasoning does not become fact.
    """

    confirmed_facts = []

    for item in case_file.get("confirmed_facts", []):
        confirmed_facts.append(
            {
                "finding": item.get("finding", ""),
                "sources": item.get("sources", [])
            }
        )

    hypotheses = []

    for item in case_file.get("root_cause_hypotheses", []):
        hypotheses.append(
            {
                "hypothesis": item.get("hypothesis", ""),
                "confidence": item.get("confidence", "LOW"),
                "verification_needed": item.get(
                    "verification_needed",
                    ""
                ),
                "sources": item.get("sources", [])
            }
        )

    unresolved_gaps = []

    for item in case_file.get(
        "contradictions_and_gaps",
        []
    ):
        unresolved_gaps.append(
            {
                "issue": item.get("issue", ""),
                "needed_evidence": item.get(
                    "needed_evidence",
                    ""
                )
            }
        )

    source_documents = set()

    # Collect source document names only from cited evidence.
    for fact in confirmed_facts:

        for source in fact.get("sources", []):

            document = source.get("document")

            if document:
                source_documents.add(document)

    for hypothesis in hypotheses:

        for source in hypothesis.get("sources", []):

            document = source.get("document")

            if document:
                source_documents.add(document)

    memory = {
        "case_id": f"CASE-{uuid.uuid4().hex[:8].upper()}",

        "created_at": datetime.now().isoformat(),

        "original_question": question,

        "case_title": case_file.get(
            "case_title",
            "Untitled Investigation"
        ),

        "executive_assessment": case_file.get(
            "executive_assessment",
            ""
        ),

        # Directly supported findings
        "confirmed_facts": confirmed_facts,

        # Historical observations that may matter later
        "historical_warning_signals": case_file.get(
            "historical_warning_signals",
            []
        ),

        # Never merge hypotheses with confirmed facts
        "hypotheses": hypotheses,

        # Things that remain unresolved
        "unresolved_gaps": unresolved_gaps,

        # Preserve the investigation's uncertainty
        "investigation_confidence": case_file.get(
            "investigation_confidence",
            {}
        ),

        # Reusable lesson, while keeping uncertainty
        "organizational_memory_summary": case_file.get(
            "organizational_memory_summary",
            ""
        ),

        "source_documents": sorted(
            list(source_documents)
        )
    }

    return memory


# ---------------------------------------------------------
# CREATE SEARCHABLE MEMORY TEXT
# ---------------------------------------------------------

def create_memory_text(memory):
    """
    Convert structured case memory into text for semantic search.

    Labels explicitly separate facts from hypotheses so future
    investigations do not confuse them.
    """

    parts = []

    parts.append(
        f"CASE TITLE: {memory.get('case_title', '')}"
    )

    parts.append(
        f"ORIGINAL QUESTION: "
        f"{memory.get('original_question', '')}"
    )

    parts.append("\nCONFIRMED FACTS:")

    for fact in memory.get("confirmed_facts", []):

        parts.append(
            f"- {fact.get('finding', '')}"
        )

    parts.append("\nHISTORICAL WARNING SIGNALS:")

    for signal in memory.get(
        "historical_warning_signals",
        []
    ):

        parts.append(
            f"- {signal.get('signal', '')}"
        )

    parts.append("\nUNCONFIRMED HYPOTHESES:")

    for hypothesis in memory.get(
        "hypotheses",
        []
    ):

        parts.append(
            "- "
            + hypothesis.get("hypothesis", "")
            + " | Confidence: "
            + hypothesis.get("confidence", "LOW")
            + " | Still requires verification: "
            + hypothesis.get(
                "verification_needed",
                ""
            )
        )

    parts.append("\nUNRESOLVED QUESTIONS:")

    for gap in memory.get(
        "unresolved_gaps",
        []
    ):

        parts.append(
            "- "
            + gap.get("issue", "")
            + " | Evidence needed: "
            + gap.get("needed_evidence", "")
        )

    parts.append("\nORGANIZATIONAL LESSON:")

    parts.append(
        memory.get(
            "organizational_memory_summary",
            ""
        )
    )

    return "\n".join(parts)


# ---------------------------------------------------------
# SAVE CASE MEMORY
# ---------------------------------------------------------

def save_case_memory(question, case_file):
    """
    Build, embed, and permanently store an investigation memory.
    """

    memory = build_case_memory(
        question,
        case_file
    )

    memory_text = create_memory_text(
        memory
    )
    embedding = create_embeddings(
    [memory_text]
    )[0]
    

    memory_collection.add(

        ids=[
            memory["case_id"]
        ],

        documents=[
            memory_text
        ],

        embeddings=[
            embedding.tolist()
        ],

        metadatas=[
            {
                "case_id": memory["case_id"],

                "case_title": memory["case_title"],

                "created_at": memory["created_at"],

                # Chroma metadata cannot safely hold
                # arbitrary nested Python structures.
                # Store the full memory as JSON text.
                "memory_json": json.dumps(
                    memory,
                    ensure_ascii=False
                )
            }
        ]
    )

    return memory


# ---------------------------------------------------------
# SEARCH PAST CASE MEMORIES
# ---------------------------------------------------------

def search_case_memories(
    query,
    n_results=3
):
    """
    Search previous investigation memories using semantic similarity.
    """

    # No memories yet
    if memory_collection.count() == 0:
        return []

    query_embedding = create_embeddings(
    [query]
    )[0]
    

    result_count = min(
        n_results,
        memory_collection.count()
    )

    results = memory_collection.query(

        query_embeddings=[
            query_embedding.tolist()
        ],

        n_results=result_count,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    memories = []

    if not results.get("ids"):
        return memories

    if not results["ids"][0]:
        return memories

    for i in range(
        len(results["ids"][0])
    ):

        metadata = results["metadatas"][0][i]

        try:

            structured_memory = json.loads(
                metadata.get(
                    "memory_json",
                    "{}"
                )
            )

        except json.JSONDecodeError:

            structured_memory = {}

        memories.append(
            {
                "case_id": metadata.get(
                    "case_id",
                    results["ids"][0][i]
                ),

                "case_title": metadata.get(
                    "case_title",
                    ""
                ),

                "distance": results[
                    "distances"
                ][0][i],

                "memory": structured_memory
            }
        )

    return memories


# ---------------------------------------------------------
# LIST SAVED MEMORIES
# ---------------------------------------------------------

def list_case_memories():
    """
    Return basic information about all stored investigation cases.
    """

    if memory_collection.count() == 0:
        return []

    results = memory_collection.get(
        include=["metadatas"]
    )

    memories = []

    for i in range(
        len(results.get("ids", []))
    ):

        metadata = results["metadatas"][i]

        memories.append(
            {
                "case_id": metadata.get(
                    "case_id",
                    results["ids"][i]
                ),

                "case_title": metadata.get(
                    "case_title",
                    ""
                ),

                "created_at": metadata.get(
                    "created_at",
                    ""
                )
            }
        )

    return memories