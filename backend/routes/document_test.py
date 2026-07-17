from fastapi import APIRouter

from backend.services.investigation import collect_evidence
from backend.services.document_understanding import build_document_profiles

router = APIRouter()


@router.get("/document-test")
def document_test(query: str):

    investigation_packet = collect_evidence(query)

    investigation_packet = build_document_profiles(
        investigation_packet
    )

    return investigation_packet["document_profiles"]