from fastapi import FastAPI

app = FastAPI(title="Syllabus to Plan")

@app.get("/")
def health_check():
    return {"status": "ok"}
