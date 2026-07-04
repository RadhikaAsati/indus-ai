from fastapi import APIRouter

from backend.services.pdf_reader import extract_text
from backend.services.chunker import split_text
from backend.services.embeddings import create_embeddings
from backend.services.vector_store import store_chunks

router = APIRouter()


@router.get("/vector-test")
def vector_test():

    pdf_path = "backend/uploads/sample.pdf"

    text = extract_text(pdf_path)

    chunks = split_text(text)

    embeddings = create_embeddings(chunks)

    store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_name="sample.pdf"
    )

    return {
        "message": "Vector database test completed successfully!",
        "chunks_stored": len(chunks)
    }