import json
from typing import Optional
from backend.models import Assignment

CHAT_SYSTEM_PROMPT = """You are a helpful academic advisor AI that answers questions about a student's course syllabus.

You have access to:
1. The full syllabus text
2. Structured assignment data (name, type, due date, grade weight)

You excel at:
- Answering factual questions directly from the syllabus
- Calculating grade impacts: "If I miss X assignments, how does that affect my grade?"
- Helping students understand what they can afford to skip
- Identifying drop policies and policies around missing work
- Giving honest, specific answers

For grade calculations:
- When asked about a series of small assignments (e.g., 20 short responses worth 10%), calculate the impact of missing N of them
- If the student asks "how many can I miss?", assume they want an A (90%) unless they specify otherwise
- Show your math clearly: "Each response is worth 0.5% (10% ÷ 20). Missing 5 costs you 2.5%, leaving you with 7.5% from responses."
- Consider ALL grade categories when doing full grade analysis
- Be honest: if they can afford to miss something, tell them clearly

Format:
- Be direct and specific
- Use numbers when discussing grades
- Keep responses concise but complete
- If something isn't in the syllabus, say so clearly
- Use bullet points for lists when appropriate

Always answer based on the syllabus content provided. Do not make up policies or rules."""


def answer_question(
    question: str,
    syllabus_text: str,
    assignments: list[Assignment]
) -> str:
    """
    Answer a student's question about their syllabus using Claude.

    Args:
        question: The student's question
        syllabus_text: The full original syllabus text
        assignments: List of parsed Assignment objects

    Returns:
        Claude's response (a helpful answer with any grade calculations shown)
    """
    from backend.parser import call_llm

    # Convert assignments to a readable JSON format for Claude
    assignments_json = json.dumps(
        [
            {
                "name": a.name,
                "course": a.course,
                "due_date": str(a.due_date),
                "type": a.assignment_type.value,
                "grade_weight": a.grade_weight
            }
            for a in assignments
        ],
        indent=2
    )

    user_prompt = f"""SYLLABUS TEXT:
{syllabus_text}

PARSED ASSIGNMENTS (structured data):
{assignments_json}

STUDENT QUESTION:
{question}"""

    return call_llm(CHAT_SYSTEM_PROMPT, user_prompt)
