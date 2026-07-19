from collections import defaultdict


KEYWORDS = {
    "pressure": [
        "pressure",
        "bar",
        "fluctuation",
        "drop",
        "relief valve",
        "gauge"
    ],

    "hydraulic": [
        "hydraulic",
        "fluid",
        "oil",
        "pump",
        "seal",
        "ram"
    ],

    "production": [
        "production",
        "output",
        "batch",
        "units",
        "cycle",
        "pace"
    ],

    "maintenance": [
        "maintenance",
        "inspection",
        "repair",
        "work order",
        "pm",
        "scheduled"
    ],

    "inventory": [
        "stock",
        "issue slip",
        "inventory",
        "stores",
        "requested",
        "issued",
        "remaining"
    ],

    "quality": [
        "quality",
        "inspection",
        "qa",
        "sampling",
        "rejections"
    ]
}


def build_reasoning(analyzed_packet):
    """
    Build investigation clues from evidence.
    """

    reasoning = defaultdict(list)

    for document_name, chunks in analyzed_packet["documents"].items():

        for chunk in chunks:

            text = chunk["content"].lower()

            clue = {
                "document": document_name,
                "chunk": chunk["chunk_number"],
                "relevance": chunk["relevance_score"],
                "machines": chunk.get("machines", []),
                "dates": chunk.get("dates", []),
                "times": chunk.get("times", []),
                "summary": chunk["content"][:180].replace("\n", " ")
            }

            for category, words in KEYWORDS.items():

                if any(word in text for word in words):
                    reasoning[category].append(clue)

    return {
        key: sorted(
            value,
            key=lambda x: x["relevance"],
            reverse=True
        )
        for key, value in reasoning.items()
    }