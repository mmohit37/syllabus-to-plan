# Syllabus to Plan

A local web application that uses AI to extract assignment deadlines from course syllabi and visualize weekly workload distribution.

---

## Problem Statement

College students manage multiple courses with varying assignment schedules across different syllabi formats (PDF, Word, plain text). Manually tracking all deadlines and understanding weekly workload distribution is time-consuming and error-prone, especially at the start of a semester.

---

## Solution

Syllabus to Plan uses Claude AI to automatically extract assignment information from syllabi and presents:

1. A chronological list of all assignments across courses
2. Weekly workload summaries with intensity scores based on assignment types

The tool accepts either pasted text or PDF uploads, processes them locally, and displays results in a simple web interface.

---

## Features

- **Multi-format input**: Paste syllabus text or upload PDF files
- **Multi-PDF support**: Upload up to 5 syllabi at once for semester-wide planning
- **Automatic extraction**: Uses Claude AI to identify assignment names, types, and due dates
- **Date normalization**: Infers current year if syllabi only specify month/day
- **Timezone-safe date handling**: Dates are parsed in local timezone to ensure displayed dates match syllabus dates exactly
- **Course code enforcement**: Requires explicit course codes to prevent misattribution
- **Chronological sorting**: All assignments sorted by due date across all courses
- **Weekly workload aggregation**: Groups assignments by week (Monday-Sunday)
- **Intensity scoring**: Weighted scores based on assignment type:
  - Exam: 3.0
  - Project: 2.5
  - Quiz: 1.5
  - Homework: 1.0
  - Other: 1.0
- **Assignment type breakdown**: Shows distribution of assignment types per week

---

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Anthropic Claude API (LLM for syllabus parsing)
- pdfplumber (PDF text extraction)
- Pydantic (data validation)

**Frontend:**
- Plain HTML/CSS/JavaScript (no frameworks)
- Served by FastAPI at root URL ("/")

**Architecture:**
- In-memory processing (no database)
- CORS-enabled for local development
- Single-page application
- Backend uses Python `date` objects (not `datetime`) to avoid timezone issues

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Claude API key from [Anthropic Console](https://console.anthropic.com/)

### Installation

1. **Clone or download the project**

2. **Create and activate a virtual environment**

   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Claude API key**

   ```bash
   # macOS/Linux
   export CLAUDE_API_KEY=your-api-key-here

   # Windows (Command Prompt)
   set CLAUDE_API_KEY=your-api-key-here

   # Windows (PowerShell)
   $env:CLAUDE_API_KEY="your-api-key-here"
   ```

5. **Start the backend server**

   ```bash
   uvicorn backend.main:app --reload
   ```

   The server will start at `http://127.0.0.1:8000`

6. **Access the frontend**

   You have two options:

   **Option A: Via FastAPI (recommended)**
   - Visit `http://127.0.0.1:8000/` in your browser
   - The backend serves the frontend HTML automatically at the root URL
   - This ensures all API calls work correctly

   **Option B: Direct file access (local testing)**
   - Open `index.html` directly in your browser (double-click or right-click → Open With → Browser)
   - The frontend will make API calls to `http://127.0.0.1:8000`

   **Health check:** You can verify the backend is running by visiting `http://127.0.0.1:8000/health` - you should see `{"status": "ok"}`

---

## Usage Instructions

### Option 1: Paste Syllabus Text

1. Enter the course code (e.g., "CSE 374", "MATH 101") - **required**
2. Paste syllabus text into the textarea
3. Click "Analyze Syllabus"
4. View results: assignments list and weekly workload

**Note:** Text and course code inputs are preserved after analysis for easy editing and re-analysis.

### Option 2: Upload PDF Syllabi

1. Click "Choose File" and select a PDF syllabus
2. Enter the course code for that syllabus - **required**
3. (Optional) Click "Add Another PDF" to add more syllabi (up to 5 total)
4. For each additional PDF, select the file and enter its course code
5. Click "Analyze PDFs"
6. View results: merged assignments from all PDFs, sorted chronologically

**Note:** All PDF inputs are cleared after successful analysis. You can upload new files immediately.

### Results Display

**Assignments Section:**
- Lists all assignments chronologically
- Shows assignment name, type (color-coded badge), course, and due date
- Types: EXAM (red), PROJECT (orange), QUIZ (yellow), HOMEWORK (blue), OTHER (gray)

**Weekly Workload Section:**
- Groups assignments by week (Monday-Sunday)
- Shows assignment count and intensity score per week
- Displays breakdown by assignment type

---

## Example Workflow

**Scenario:** You're taking 3 courses and want to plan your semester workload.

1. Start the backend: `uvicorn backend.main:app --reload`
2. Open your browser and visit `http://127.0.0.1:8000/`
3. Go to "Option 2: Upload PDFs"
4. Upload syllabus PDF for CSE 374, enter "CSE 374" as course code
5. Click "Add Another PDF"
6. Upload syllabus PDF for MATH 101, enter "MATH 101" as course code
7. Click "Add Another PDF"
8. Upload syllabus PDF for ENGL 201, enter "ENGL 201" as course code
9. Click "Analyze PDFs"
10. View all 3 courses' assignments merged and sorted by date
11. Review weekly workload to identify busy weeks

---

## Limitations & Design Decisions

### By Design (MVP Scope)

- **Local only**: No deployment, runs on localhost for simplicity and cost
- **No persistence**: No database; results disappear on page refresh
- **No authentication**: Single-user local application
- **No file storage**: PDFs processed in-memory and discarded
- **Required course codes**: Prevents LLM from misattributing assignments
- **Date year inference**: Uses current year if syllabus doesn't specify (common for single-semester syllabi)

### Technical Constraints

- **LLM accuracy**: Assignment extraction quality depends on syllabus format and Claude API
- **PDF parsing**: Complex layouts or scanned images may not extract cleanly
- **API costs**: Each analysis makes a Claude API call (costs apply)
- **Max 5 PDFs**: Prevents excessive API usage and maintains reasonable response times
- **Week boundaries**: Fixed Monday-Sunday weeks (not customizable)

### Known Issues

- Syllabi without explicit dates (e.g., "Week 3" instead of "October 15") won't extract assignments
- Multi-year syllabi may have ambiguous dates if year isn't specified
- Very large PDFs (>100 pages) may exceed API token limits

---

## Future Improvements

**Potential enhancements (outside MVP scope):**

- Calendar export (iCal/Google Calendar integration)
- Persistent storage (database for saved analyses)
- Configurable week start day (Monday vs Sunday)
- Custom intensity weights per user
- Batch processing for entire academic departments
- Support for other LLM providers (OpenAI, local models)
- Syllabus templates for common course management systems
- Visual workload heatmap/calendar view
- Email reminders for upcoming deadlines
- Mobile-responsive design

---

## Submission Notes

### For Instructors and Reviewers

This is a **local MVP application** designed to demonstrate core functionality. There is no live deployment link.

**To run and review this project:**

1. Follow the Setup Instructions above
2. Obtain a Claude API key from Anthropic (free tier available)
3. Run the backend server locally with `uvicorn backend.main:app --reload`
4. Access the frontend by visiting `http://127.0.0.1:8000/` (FastAPI serves the HTML automatically)

**Why local-only?**

- **Cost control**: Deployed apps with LLM APIs incur per-request costs
- **MVP scope**: Focus on core functionality over infrastructure
- **Privacy**: Syllabi may contain course-specific information best kept local
- **Simplicity**: No need for hosting, domains, or deployment pipelines

**Testing the application:**

- Use sample syllabi (PDF or text) from your courses
- Test with 1-5 PDFs to verify multi-file handling
- Try syllabi with various date formats (with/without years)
- Verify course code enforcement (try submitting without one)

**Architecture notes:**

- Backend: `backend/` directory (FastAPI app, models, parser, workload logic)
- Frontend: `index.html` (single-file SPA)
- Tests: `backend/test_backend.py` and `backend/test_api.py`
- No build step required - pure Python and vanilla JavaScript

---

## Project Structure

```
syllabus-to-plan/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and endpoints
│   ├── models.py            # Pydantic data models
│   ├── parser.py            # LLM integration and date normalization
│   ├── workload.py          # Weekly aggregation and intensity scoring
│   ├── test_backend.py      # Unit and integration tests
│   └── test_api.py          # API endpoint tests
├── index.html               # Frontend interface
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## License

This is an educational MVP project. No license specified.
