from fastapi import APIRouter

from backend.services.investigation import collect_evidence
from backend.services.evidence_analyzer import analyze_evidence
from backend.services.timeline_builder import build_timeline
from backend.services.llm_service import generate_investigation_case


router = APIRouter()


# Temporarily holds the latest generated investigation.
# It is NOT permanent organizational memory yet.
latest_investigation = {}


@router.get("/investigation")
def investigate(query: str):

    # 1. Retrieve relevant evidence
    evidence = collect_evidence(query)

    # 2. Organize and analyze evidence
    analyzed = analyze_evidence(evidence)

    # 3. Build timeline
    timeline = build_timeline(analyzed)

    analyzed["timeline"] = timeline

    # 4. Let Gemini reason over the evidence
    llm_result = generate_investigation_case(analyzed)

    # 5. Keep successful result temporarily
    # until a user approves it for permanent memory.
    if llm_result.get("success"):

        latest_investigation.clear()

        latest_investigation.update(
            {
                "question": query,
                "case_file": llm_result["case_file"]
            }
        )

    return {
        "investigation_packet": analyzed,
        "reasoning_result": llm_result
    }