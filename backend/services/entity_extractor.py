import re


def extract_entities(text):
    """
    Extract important industrial entities from text.
    """

    patterns = {

        "machines": r"\b[A-Z]{2,5}-\d+\b",

        "work_orders": r"\bMWO-\d{4}-\d+\b",

        "issue_ids": r"\bINV-ISSUE-\d{4}-\d+\b",

        "departments": (
            r"\b("
            r"Maintenance|Production|Quality|Stores|"
            r"Safety|Operations|Engineering"
            r")\b"
        ),

        "dates": (
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|"
            r"\b\d{1,2}-[A-Za-z]{3}-\d{4}\b|"
            r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\b"
        ),

        "times": (
            r"\b\d{1,2}:\d{2}\s?(?:AM|PM)?\b"
        ),

        "people": (
            r"\b(?:Mr|Ms|Mrs|Dr)\.?\s+[A-Z][a-z]+"
        )
    }

    entities = {}

    for key, pattern in patterns.items():
        entities[key] = sorted(
            list(
                set(
                    re.findall(
                        pattern,
                        text,
                        flags=re.IGNORECASE
                    )
                )
            )
        )

    return entities