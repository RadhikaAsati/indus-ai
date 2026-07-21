from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.test import router as test_router
from backend.routes.vector_test import router as vector_router
from backend.routes.investigation import router as investigation_router
from backend.routes.document_test import router as document_test_router
from backend.routes.index_documents import router as index_router
from backend.routes import memory
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="INDUS AI",
    description="Industrial Investigation Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(test_router)
app.include_router(vector_router)
app.include_router(investigation_router)
app.include_router(document_test_router)
app.include_router(index_router)
app.include_router(memory.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to INDUS AI 🚀",
        "status": "running"
    }
@app.get("/hello")
def hello():
    return {
        "message": "Hello Radhika! 🎉"
    }