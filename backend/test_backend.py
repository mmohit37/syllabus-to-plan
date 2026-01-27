"""
Test cases for models.py, parser.py, and workload.py
"""
from datetime import date
from backend.models import Assignment, AssignmentType, Course, WeeklyWorkload
from backend.workload import compute_weekly_workload, get_week_start
import json


def test_models():
    """Test Pydantic model validation"""
    print("Testing models.py...")

    # Test Course
    course = Course(name="Computer Science", code="CSE 374")
    assert course.name == "Computer Science"
    assert course.code == "CSE 374"
    print("  [OK] Course model works")

    # Test Assignment
    assignment = Assignment(
        name="Problem Set 1",
        course="CSE 374",
        due_date=date(2024, 10, 15),
        assignment_type=AssignmentType.HOMEWORK
    )
    assert assignment.name == "Problem Set 1"
    assert assignment.due_date == date(2024, 10, 15)
    assert assignment.assignment_type == AssignmentType.HOMEWORK
    print("  [OK] Assignment model works")

    # Test WeeklyWorkload
    workload = WeeklyWorkload(
        week_start_date=date(2024, 10, 14),
        week_end_date=date(2024, 10, 20),
        assignment_count=3,
        intensity_score=5.5,
        assignments_by_type={"homework": 2, "exam": 1}
    )
    assert workload.assignment_count == 3
    assert workload.intensity_score == 5.5
    print("  [OK] WeeklyWorkload model works")

    print("[OK] All model tests passed!\n")


def test_workload_aggregation():
    """Test workload aggregation logic"""
    print("Testing workload.py...")

    # Test get_week_start
    test_date = date(2024, 10, 17)  # Thursday
    week_start = get_week_start(test_date)
    assert week_start == date(2024, 10, 14)  # Monday
    print("  [OK] get_week_start works")

    # Test empty assignments
    result = compute_weekly_workload([])
    assert result == []
    print("  [OK] Empty assignments handled")

    # Test single week
    assignments = [
        Assignment(
            name="HW 1",
            course="CSE 374",
            due_date=date(2024, 10, 15),
            assignment_type=AssignmentType.HOMEWORK
        ),
        Assignment(
            name="Quiz 1",
            course="CSE 374",
            due_date=date(2024, 10, 17),
            assignment_type=AssignmentType.QUIZ
        ),
        Assignment(
            name="Midterm",
            course="CSE 374",
            due_date=date(2024, 10, 18),
            assignment_type=AssignmentType.EXAM
        ),
    ]

    workloads = compute_weekly_workload(assignments)
    assert len(workloads) == 1
    assert workloads[0].assignment_count == 3
    assert workloads[0].intensity_score == 5.5  # 1.0 + 1.5 + 3.0
    assert workloads[0].assignments_by_type["homework"] == 1
    assert workloads[0].assignments_by_type["quiz"] == 1
    assert workloads[0].assignments_by_type["exam"] == 1
    print("  [OK] Single week aggregation works")

    # Test multiple weeks
    assignments = [
        Assignment(
            name="HW 1",
            course="CSE 374",
            due_date=date(2024, 10, 15),
            assignment_type=AssignmentType.HOMEWORK
        ),
        Assignment(
            name="Project 1",
            course="CSE 374",
            due_date=date(2024, 10, 23),
            assignment_type=AssignmentType.PROJECT
        ),
    ]

    workloads = compute_weekly_workload(assignments)
    assert len(workloads) == 2
    assert workloads[0].week_start_date == date(2024, 10, 14)
    assert workloads[1].week_start_date == date(2024, 10, 21)
    assert workloads[0].intensity_score == 1.0
    assert workloads[1].intensity_score == 2.5
    print("  [OK] Multiple week aggregation works")

    print("[OK] All workload tests passed!\n")


def test_parser_validation():
    """Test parser JSON validation logic"""
    print("Testing parser.py validation...")

    # Simulate what parser.py does with valid JSON
    json_data = """[
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

    data = json.loads(json_data)
    assignments = []
    for item in data:
        assignment = Assignment(
            name=item["name"],
            course=item["course"],
            due_date=date.fromisoformat(item["due_date"]),
            assignment_type=AssignmentType(item["assignment_type"])
        )
        assignments.append(assignment)

    assert len(assignments) == 2
    assert assignments[0].name == "Problem Set 1"
    assert assignments[0].due_date == date(2024, 10, 15)
    assert assignments[1].assignment_type == AssignmentType.EXAM
    print("  [OK] JSON parsing and validation works")

    # Test markdown cleanup
    content = "```json\n" + json_data + "\n```"
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    data = json.loads(content)
    assert len(data) == 2
    print("  [OK] Markdown cleanup works")

    print("[OK] All parser validation tests passed!\n")


def test_integration():
    """Test full integration: parser output -> workload aggregation"""
    print("Testing integration...")

    # Simulate parser output
    assignments = [
        Assignment(
            name="HW 1",
            course="CSE 374",
            due_date=date(2024, 10, 15),
            assignment_type=AssignmentType.HOMEWORK
        ),
        Assignment(
            name="HW 2",
            course="CSE 374",
            due_date=date(2024, 10, 22),
            assignment_type=AssignmentType.HOMEWORK
        ),
        Assignment(
            name="Midterm",
            course="CSE 374",
            due_date=date(2024, 10, 24),
            assignment_type=AssignmentType.EXAM
        ),
        Assignment(
            name="Project",
            course="CSE 143",
            due_date=date(2024, 10, 25),
            assignment_type=AssignmentType.PROJECT
        ),
    ]

    # Aggregate into weekly workload
    workloads = compute_weekly_workload(assignments)

    assert len(workloads) == 2

    # Week 1: Oct 14-20 (HW 1)
    assert workloads[0].assignment_count == 1
    assert workloads[0].intensity_score == 1.0

    # Week 2: Oct 21-27 (HW 2, Midterm, Project)
    assert workloads[1].assignment_count == 3
    assert workloads[1].intensity_score == 6.5  # 1.0 + 3.0 + 2.5

    print("  [OK] Parser output -> workload aggregation works")
    print("[OK] Integration test passed!\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Running Backend Tests")
    print("=" * 50 + "\n")

    try:
        test_models()
        test_workload_aggregation()
        test_parser_validation()
        test_integration()

        print("=" * 50)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        raise
