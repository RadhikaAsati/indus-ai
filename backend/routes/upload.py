from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

router = APIRouter()

UPLOAD_FOLDER = "backend/uploads"

SUPPORTED_EXTENSIONS = (
    ".pdf",
    ".txt",
    ".csv",
    ".xlsx"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):
    """
    Upload a supported industrial document.

    The file is saved to backend/uploads.

    Actual text extraction, chunking,
    embedding generation and ChromaDB
    indexing are handled by /index-documents.
    """

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    # Keep only the filename.
    # This prevents directory traversal
    # through uploaded filenames.

    safe_filename = os.path.basename(
        file.filename
    )

    extension = os.path.splitext(
        safe_filename
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported formats are PDF, TXT, CSV and XLSX."
            )
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {str(error)}"
        )

    finally:

        await file.close()

    file_size = os.path.getsize(
        file_path
    )

    return {
        "message":
            "File uploaded successfully.",

        "filename":
            safe_filename,

        "file_type":
            extension.replace(
                ".",
                ""
            ).upper(),

        "size_bytes":
            file_size,

        "ready_for_indexing":
            True
    }