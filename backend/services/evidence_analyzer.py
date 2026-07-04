import re


def analyze_evidence(investigation_packet):
    """
    Analyze retrieved evidence and extract useful industrial information.
    """

    machine_pattern = r"[A-Z]{2,5}-\d+"

    date_pattern = (
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    )

    analyzed_documents = {}

    total_machines = set()
    total_dates = set()

    for document_name, chunks in investigation_packet["documents"].items():

        analyzed_chunks = []

        for chunk in chunks:

            content = chunk["content"]

            machines = re.findall(machine_pattern, content)

            dates = re.findall(date_pattern, content)

            total_machines.update(machines)

            total_dates.update(dates)

            analyzed_chunks.append(
                {
                    **chunk,

                    "machines": machines,

                    "dates": dates,

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

        "machines_detected": sorted(
            list(total_machines)
        ),

        "dates_detected": sorted(
            list(total_dates)
        ),

        "documents": analyzed_documents
    }