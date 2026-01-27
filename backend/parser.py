import json
from datetime import date
from typing import Optional
from backend.models import Assignment, AssignmentType


SYSTEM_PROMPT = """You are an AI assistant that extracts assignment deadlines from college course syllabi.

Your task is to parse raw syllabus text and return a JSON array of assignments.

Each assignment must have:
- name (string): the assignment name
- course (string): use the course code from the prompt header "Course: XXX" if provided, otherwise use "UNKNOWN"
- due_date (string): date in MM-DD format (e.g., "10-15") if year is not specified, or YYYY-MM-DD format (e.g., "2024-10-15") if year is explicitly stated in the syllabus
- assignment_type (string): one of "exam", "homework", "project", "quiz", "other"

Rules:
- ONLY extract assignments with clearly stated due dates
- Do NOT invent or guess dates or years
- If the syllabus says "October 15" without a year, return "10-15" (not a full year)
- If the syllabus says "October 15, 2024", return "2024-10-15"
- If a due date is ambiguous or missing, omit the assignment
- Do NOT include readings, participation, or vague "weekly work" without specific dates
- CRITICAL: Use the course code from "Course: XXX" in the prompt if provided - do NOT extract course code from syllabus content
- Return ONLY valid JSON, no commentary

Example output:
[
  {
    "name": "Problem Set 1",
    "course": "CSE 374",
    "due_date": "10-15",
    "assignment_type": "homework"
  },
  {
    "name": "Midterm Exam",
    "course": "CSE 374",
    "due_date": "2024-11-03",
    "assignment_type": "exam"
  }
]"""


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Call Claude API to process syllabus text.

    Args:
        system_prompt: Instructions for the LLM
        user_prompt: User content to process

    Returns:
        Raw text response from Claude
    """
    import os
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    return message.content[0].text


def normalize_date(date_str: str) -> date:
    """
    Normalize date string to a date object.

    If date is in MM-DD format, prepends current year.
    If date is in YYYY-MM-DD format, uses it as-is.

    Args:
        date_str: Date string in either MM-DD or YYYY-MM-DD format

    Returns:
        date object
    """
    date_str = date_str.strip()

    # Check if year is present (YYYY-MM-DD format)
    if len(date_str) == 10 and date_str[4] == '-':
        return date.fromisoformat(date_str)

    # Year not present (MM-DD format), use current year
    if len(date_str) == 5 and date_str[2] == '-':
        current_year = date.today().year
        full_date = f"{current_year}-{date_str}"
        return date.fromisoformat(full_date)

    # Try parsing as-is for other formats
    return date.fromisoformat(date_str)


def parse_syllabus(syllabus_text: str, course_code: Optional[str] = None) -> list[Assignment]:
    """
    Parse syllabus text and extract assignments.

    Args:
        syllabus_text: Raw text content of the syllabus
        course_code: Optional course code to use for all assignments (overrides LLM extraction)

    Returns:
        List of Assignment objects, or empty list if parsing fails
    """
    try:
        user_prompt = syllabus_text
        if course_code:
            user_prompt = f"Course: {course_code}\n\n{syllabus_text}"

        content = call_llm(SYSTEM_PROMPT, user_prompt)

        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        data = json.loads(content)

        assignments = []
        for item in data:
            # Normalize the date (add current year if missing)
            normalized_date = normalize_date(item["due_date"])

            # Use user-provided course code if available, otherwise use LLM extraction
            final_course = course_code if course_code else item["course"]

            assignment = Assignment(
                name=item["name"],
                course=final_course,
                due_date=normalized_date,
                assignment_type=AssignmentType(item["assignment_type"])
            )
            assignments.append(assignment)

        return assignments

    except Exception:
        return []
