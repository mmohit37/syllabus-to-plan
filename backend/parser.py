import json
from datetime import date
from typing import Optional
from backend.models import Assignment, AssignmentType


SYSTEM_PROMPT = """You are an AI assistant that extracts assignment deadlines from college course syllabi.

Your task is to parse raw syllabus text and return a JSON array of assignments.

Each assignment must have:
- name (string): the assignment name
- course (string): course code like "CSE 374"
- due_date (string): ISO date format YYYY-MM-DD
- assignment_type (string): one of "exam", "homework", "project", "quiz", "other"

Rules:
- ONLY extract assignments with clearly stated due dates
- Do NOT invent or guess dates
- If a due date is ambiguous or missing, omit the assignment
- Do NOT include readings, participation, or vague "weekly work" without specific dates
- Infer course code from syllabus context if not explicitly provided
- Return ONLY valid JSON, no commentary

Example output:
[
  {
    "name": "Problem Set 1",
    "course": "CSE 374",
    "due_date": "2024-10-15",
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


def parse_syllabus(syllabus_text: str, course_code: Optional[str] = None) -> list[Assignment]:
    """
    Parse syllabus text and extract assignments.

    Args:
        syllabus_text: Raw text content of the syllabus
        course_code: Optional course code to help with extraction

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
            assignment = Assignment(
                name=item["name"],
                course=item["course"],
                due_date=date.fromisoformat(item["due_date"]),
                assignment_type=AssignmentType(item["assignment_type"])
            )
            assignments.append(assignment)

        return assignments

    except Exception:
        return []
