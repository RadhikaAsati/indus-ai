from fastapi import FastAPI

app = FastAPI(
    title="INDUS AI",
    description="Industrial Investigation Engine",
    version="1.0.0"
)

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