from collections import defaultdict


def link_entities(analyzed_packet):
    """
    Connect entities appearing across multiple documents.
    """

    linked_entities = defaultdict(
        lambda: {
            "documents": set(),
            "work_orders": set(),
            "dates": set(),
            "mentions": 0
        }
    )

    for document_name, chunks in analyzed_packet["documents"].items():

        for chunk in chunks:

            for machine in chunk.get("machines", []):

                linked_entities[machine]["documents"].add(
                    document_name
                )

                linked_entities[machine]["mentions"] += 1

                linked_entities[machine]["dates"].update(
                    chunk.get("dates", [])
                )

                linked_entities[machine]["work_orders"].update(
                    chunk.get("work_orders", [])
                )

    result = {}

    for entity, info in linked_entities.items():

        result[entity] = {

            "documents": sorted(
                list(info["documents"])
            ),

            "mentions": info["mentions"],

            "dates": sorted(
                list(info["dates"])
            ),

            "work_orders": sorted(
                list(info["work_orders"])
            )
        }

    return result