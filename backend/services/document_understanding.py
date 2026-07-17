import re
from collections import Counter


# Very common words that don't help us understand a document
STOP_WORDS = {
    "the", "and", "for", "with", "from", "this", "that",
    "have", "has", "had", "are", "was", "were", "will",
    "shall", "into", "onto", "your", "their", "there",
    "which", "when", "where", "while", "been", "being",
    "after", "before", "using", "used", "over", "under",
    "within", "about", "report", "page", "department",
    "machine", "system", "document"
}


# Vocabulary used only for document classification
DOCUMENT_TYPES = {

    "Maintenance": [
        "maintenance",
        "repair",
        "inspection",
        "lubrication",
        "bearing",
        "motor",
        "pump",
        "replacement",
        "breakdown"
    ],

    "Production": [
        "production",
        "operator",
        "shift",
        "batch",
        "manufacturing",
        "output",
        "assembly"
    ],

    "Inventory": [
        "inventory",
        "stock",
        "warehouse",
        "issue",
        "receipt",
        "material",
        "store"
    ],

    "Quality": [
        "quality",
        "inspection",
        "defect",
        "rejected",
        "accepted",
        "measurement",
        "testing"
    ],

    "Safety": [
        "safety",
        "hazard",
        "incident",
        "ppe",
        "risk",
        "accident"
    ]
}


def extract_dates(text):
    """
    Extract dates from text.
    """

    pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"

    return re.findall(pattern, text)


def extract_keywords(text):

    words = re.findall(r"[A-Za-z]{4,}", text.lower())

    filtered = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    counts = Counter(filtered)

    return [
        word
        for word, _
        in counts.most_common(10)
    ]


def classify_document(text):

    text = text.lower()

    scores = {}

    for category, vocabulary in DOCUMENT_TYPES.items():

        score = 0

        for word in vocabulary:

            score += text.count(word)

        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Unknown"

    return best_category


def build_document_profiles(investigation_packet):

    profiles = {}

    for document_name, chunks in investigation_packet["documents"].items():

        combined_text = ""

        for chunk in chunks:
            combined_text += chunk["content"] + "\n"

        profile = {

            "document_name": document_name,

            "document_type": classify_document(combined_text),

            "chunk_count": len(chunks),

            "dates": sorted(
                list(
                    set(
                        extract_dates(combined_text)
                    )
                )
            ),

            "keywords": extract_keywords(combined_text),

            "retrieved_chunks": [
                chunk["chunk_number"]
                for chunk in chunks
            ]
        }

        profiles[document_name] = profile

    investigation_packet["document_profiles"] = profiles

    return investigation_packet