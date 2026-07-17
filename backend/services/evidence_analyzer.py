from backend.services.entity_extractor import extract_entities


def analyze_evidence(investigation_packet):
    """
    Analyze retrieved evidence and extract useful industrial information.
    """

    analyzed_documents = {}

    summary_entities = {
        "machines": set(),
        "work_orders": set(),
        "issue_ids": set(),
        "departments": set(),
        "people": set(),
        "dates": set(),
        "times": set()
    }

    for document_name, chunks in investigation_packet["documents"].items():

        analyzed_chunks = []

        for chunk in chunks:

            content = chunk["content"]

            entities = extract_entities(content)

            # Collect entities from all chunks
            for key, values in entities.items():
                summary_entities[key].update(values)

            analyzed_chunks.append(
                {
                    **chunk,
                    **entities,
                    "contains_numbers": any(
                        c.isdigit()
                        for c in content
                    ),
                    "word_count": len(content.split())
                }
            )

        analyzed_documents[document_name] = analyzed_chunks

    return {
        "question": investigation_packet["question"],

        "summary": investigation_packet["summary"],

        "entities": {
            key: sorted(list(values))
            for key, values in summary_entities.items()
        },

        "documents": analyzed_documents
    }