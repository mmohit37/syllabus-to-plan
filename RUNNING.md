# Running Syllabus to Plan

## Project Structure

The backend is now configured as a proper Python package with correct imports.

```
syllabus-to-plan/
├── backend/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   ├── parser.py            # Syllabus parser
│   ├── workload.py          # Workload aggregation
│   ├── test_backend.py      # Unit tests
│   └── test_api.py          # API tests
└── requirements.txt
```

## Running the Server

From the project root directory:

```bash
uvicorn backend.main:app --reload
```

Or if uvicorn is not in PATH:

```bash
python -m uvicorn backend.main:app --reload
```

The server will start at:
- http://localhost:8000 - Health check
- http://localhost:8000/analyze - POST endpoint
- http://localhost:8000/docs - Interactive API documentation

## Running Tests

From the project root directory:

```bash
# Run backend unit tests
python -m backend.test_backend

# Run API endpoint tests
python -m backend.test_api
```

## API Usage

POST to `/analyze` with JSON body:

```json
{
  "course": "CSE 374",
  "text": "Your syllabus text here..."
}
```

Response format:

```json
{
  "assignments": [
    {
      "name": "Homework 1",
      "course": "CSE 374",
      "due_date": "2024-10-15",
      "assignment_type": "homework"
    }
  ],
  "weekly_workload": [
    {
      "week_start_date": "2024-10-14",
      "week_end_date": "2024-10-20",
      "assignment_count": 1,
      "intensity_score": 1.0,
      "assignments_by_type": {"homework": 1}
    }
  ]
}
```

## Next Steps

To enable actual syllabus parsing, implement the `call_llm()` function in `backend/parser.py` with your LLM provider:

- OpenAI (GPT-4)
- Anthropic (Claude)
- Or any other LLM API

The system prompt and validation logic are already in place.
