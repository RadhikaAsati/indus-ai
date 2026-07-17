from fastapi import APIRouter

from backend.services.investigation import collect_evidence
from backend.services.evidence_analyzer import analyze_evidence
from backend.services.entity_linker import link_entities

router = APIRouter()


@router.get("/investigation")
def investigate(query: str):

    # Step 1: Retrieve relevant evidence
    evidence = collect_evidence(query)

    # Step 2: Analyze each chunk
    analyzed = analyze_evidence(evidence)

    # Step 3: Connect entities across documents
    linked_entities = link_entities(analyzed)

    # Step 4: Add linked entities to the response
    analyzed["linked_entities"] = linked_entities

    return analyzed