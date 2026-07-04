from fastapi import APIRouter, UploadFile, File
from backend.services.pdf_reader import extract_text
import shutil
import os

router = APIRouter()

UPLOAD_FOLDER = "backend/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_path)

    return {
        "message": "File uploaded successfully!",
        "filename": file.filename,
        "characters": len(text),
        "preview": text[:500]
    }