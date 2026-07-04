from fastapi import APIRouter

from backend.services.investigation import collect_evidence
from backend.services.evidence_analyzer import analyze_evidence

router = APIRouter()


@router.get("/investigation")
def investigate(query: str):

    evidence = collect_evidence(query)

    analyzed = analyze_evidence(evidence)

    return analyzed