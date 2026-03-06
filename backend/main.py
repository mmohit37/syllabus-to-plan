from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
def serve_frontend():
    """
    Serve the frontend UI at the root URL.
    """
    return FileResponse("index.html")


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    """
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
    files: list[UploadFile] = File(...),
    courses: list[str] = Form(...)
):
    """
    Parse syllabus PDFs and return assignments with weekly workload analysis.

    Args:
        files: List of uploaded PDF files (max 5)
        courses: List of course codes (one per file)

    Returns:
        Assignments and weekly workload summaries
    """
    # Validate number of files
    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 PDF files allowed"
        )

    # Validate course codes match number of files
    if len(courses) != len(files):
        raise HTTPException(
            status_code=400,
            detail=f"Number of course codes ({len(courses)}) must match number of files ({len(files)})"
        )

    # Validate all files are PDFs
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are supported. Invalid file: {file.filename}"
            )

    try:
        all_assignments = []

        # Process each PDF
        for file, course in zip(files, courses):
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
                    detail=f"Could not extract text from PDF: {file.filename}"
                )

            # Parse this syllabus
            assignments = parse_syllabus(text_content, course)
            all_assignments.extend(assignments)

        # Sort all assignments chronologically
        all_assignments.sort(key=lambda a: a.due_date)

        # Compute weekly workload across all courses
        weekly_workload = compute_weekly_workload(all_assignments)

        return AnalyzeResponse(
            assignments=all_assignments,
            weekly_workload=weekly_workload
        )

    except HTTPException:
        raise
    except Exception:
        return AnalyzeResponse(
            assignments=[],
            weekly_workload=[]
        )
