from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.parser import parse_syllabus
from backend.workload import compute_weekly_workload
from backend.models import Assignment, WeeklyWorkload
import pdfplumber


app = FastAPI(title="Syllabus to Plan")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    course: str
    text: str


class AnalyzeResponse(BaseModel):
    assignments: list[Assignment]
    weekly_workload: list[WeeklyWorkload]


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_syllabus(request: AnalyzeRequest):
    """
    Parse syllabus text and return assignments with weekly workload analysis.

    Args:
        request: Contains course code and raw syllabus text

    Returns:
        Assignments and weekly workload summaries
    """
    try:
        assignments = parse_syllabus(request.text, request.course)
        weekly_workload = compute_weekly_workload(assignments)

        return AnalyzeResponse(
            assignments=assignments,
            weekly_workload=weekly_workload
        )
    except Exception:
        return AnalyzeResponse(
            assignments=[],
            weekly_workload=[]
        )


@app.post("/analyze-pdf", response_model=AnalyzeResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    course: str = Form(...)
):
    """
    Parse syllabus PDF and return assignments with weekly workload analysis.

    Args:
        file: Uploaded PDF file
        course: Course code

    Returns:
        Assignments and weekly workload summaries
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        content = await file.read()

        # Extract text from PDF using pdfplumber
        import io
        text_content = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"

        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        # Reuse existing parsing and workload logic
        assignments = parse_syllabus(text_content, course)
        weekly_workload = compute_weekly_workload(assignments)

        return AnalyzeResponse(
            assignments=assignments,
            weekly_workload=weekly_workload
        )

    except HTTPException:
        raise
    except Exception:
        return AnalyzeResponse(
            assignments=[],
            weekly_workload=[]
        )
