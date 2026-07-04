from fastapi import APIRouter
from backend.services.pdf_reader import extract_text
from backend.services.chunker import split_text

router = APIRouter()


@router.get("/test-chunks")
def test_chunks():
    pdf_path = "backend/uploads/Assignment module 1.pdf"

    text = extract_text(pdf_path)

    chunks = split_text(text)

    return {
        "total_chunks": len(chunks),
        "first_chunk": chunks[0],
        "first_chunk_length": len(chunks[0])
    }