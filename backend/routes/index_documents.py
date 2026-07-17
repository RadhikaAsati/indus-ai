from fastapi import APIRouter
import os

from backend.services.pdf_reader import extract_text
from backend.services.chunker import split_text
from backend.services.embeddings import create_embeddings
from backend.services.vector_store import store_chunks

router = APIRouter()


UPLOAD_FOLDER = "backend/uploads"


@router.post("/index-documents")
def index_documents():

    indexed_files = []

    total_chunks = 0

    for filename in os.listdir(UPLOAD_FOLDER):

        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        text = extract_text(pdf_path)

        chunks = split_text(text)

        embeddings = create_embeddings(chunks)

        store_chunks(
            chunks,
            embeddings,
            filename
        )

        indexed_files.append(filename)

        total_chunks += len(chunks)

    return {

        "message": "All documents indexed successfully.",

        "documents_indexed": len(indexed_files),

        "total_chunks": total_chunks,

        "files": indexed_files
    }