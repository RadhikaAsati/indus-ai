from fastapi import FastAPI
from backend.routes.upload import router as upload_router


app = FastAPI(
    title="INDUS AI",
    description="Industrial Investigation Engine",
    version="1.0.0"
)
app.include_router(upload_router)

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