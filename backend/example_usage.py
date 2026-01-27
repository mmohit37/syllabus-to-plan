"""
Example usage of the /analyze endpoint

To run the server:
    uvicorn main:app --reload

Then run this script:
    python example_usage.py
"""
import requests


def test_analyze_endpoint():
    """Example API call to /analyze endpoint"""

    url = "http://localhost:8000/analyze"

    payload = {
        "course": "CSE 374",
        "text": """
        CSE 374 - Software Engineering
        Fall 2024

        Assignments:
        1. Homework 1 - Due October 15, 2024
           Introduction to version control

        2. Project Proposal - Due October 22, 2024
           Submit your team project proposal

        3. Midterm Exam - November 3, 2024
           Covers weeks 1-5

        4. Homework 2 - November 10, 2024
           Testing and CI/CD

        5. Final Project - December 8, 2024
           Complete implementation with documentation
        """
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        print("=" * 50)
        print("ASSIGNMENTS FOUND:")
        print("=" * 50)
        for assignment in data["assignments"]:
            print(f"- {assignment['name']} ({assignment['assignment_type']})")
            print(f"  Due: {assignment['due_date']}")
            print(f"  Course: {assignment['course']}\n")

        print("=" * 50)
        print("WEEKLY WORKLOAD:")
        print("=" * 50)
        for week in data["weekly_workload"]:
            print(f"Week of {week['week_start_date']}:")
            print(f"  Assignments: {week['assignment_count']}")
            print(f"  Intensity Score: {week['intensity_score']}")
            print(f"  By Type: {week['assignments_by_type']}\n")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server.")
        print("Make sure the server is running with: uvicorn main:app --reload")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\nNote: This will only work once you implement call_llm()")
    print("in parser.py with your LLM provider.\n")
    test_analyze_endpoint()
