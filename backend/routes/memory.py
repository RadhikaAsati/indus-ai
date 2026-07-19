from fastapi import APIRouter, HTTPException

from backend.routes.investigation import latest_investigation

from backend.services.case_memory import (
    save_case_memory,
    search_case_memories,
    list_case_memories
)


router = APIRouter()


@router.post("/memory/save-latest")
def save_latest_memory():
    """
    Save the latest reviewed investigation
    into permanent organizational memory.
    """

    if not latest_investigation:
        raise HTTPException(
            status_code=400,
            detail=(
                "No investigation is waiting to be saved. "
                "Run an investigation first."
            )
        )

    question = latest_investigation.get(
        "question",
        ""
    )

    case_file = latest_investigation.get(
        "case_file"
    )

    if not case_file:
        raise HTTPException(
            status_code=400,
            detail="Latest investigation has no valid case file."
        )

    memory = save_case_memory(
        question,
        case_file
    )

    # Remove it from the temporary desk after approval,
    # preventing accidental repeated saves.
    latest_investigation.clear()

    return {
        "success": True,
        "message": "Investigation saved to organizational memory.",
        "case_id": memory["case_id"],
        "case_title": memory["case_title"]
    }


@router.get("/memory/search")
def search_memory(
    query: str,
    n_results: int = 3
):
    """
    Search previously saved investigation memories.
    """

    memories = search_case_memories(
        query,
        n_results
    )

    return {
        "query": query,
        "matches_found": len(memories),
        "memories": memories
    }


@router.get("/memory/cases")
def get_saved_cases():
    """
    List all saved investigation memories.
    """

    memories = list_case_memories()

    return {
        "total_cases": len(memories),
        "cases": memories
    }