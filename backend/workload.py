from datetime import date, timedelta
from collections import defaultdict
from backend.models import Assignment, AssignmentType, WeeklyWorkload


TYPE_WEIGHTS = {
    AssignmentType.EXAM: 3.0,
    AssignmentType.PROJECT: 2.5,
    AssignmentType.QUIZ: 1.5,
    AssignmentType.HOMEWORK: 1.0,
    AssignmentType.OTHER: 1.0,
}


def get_week_start(d: date) -> date:
    """
    Get the Monday of the week containing the given date.

    Args:
        d: Any date

    Returns:
        The Monday of that week
    """
    days_since_monday = d.weekday()
    return d - timedelta(days=days_since_monday)


def compute_weekly_workload(assignments: list[Assignment]) -> list[WeeklyWorkload]:
    """
    Aggregate assignments into weekly workload summaries.

    Args:
        assignments: List of Assignment objects

    Returns:
        List of WeeklyWorkload objects sorted chronologically
    """
    if not assignments:
        return []

    weeks = defaultdict(list)

    for assignment in assignments:
        week_start = get_week_start(assignment.due_date)
        weeks[week_start].append(assignment)

    workloads = []

    for week_start in sorted(weeks.keys()):
        week_assignments = weeks[week_start]
        week_end = week_start + timedelta(days=6)

        assignment_count = len(week_assignments)

        intensity_score = sum(
            TYPE_WEIGHTS[assignment.assignment_type]
            for assignment in week_assignments
        )

        assignments_by_type = defaultdict(int)
        for assignment in week_assignments:
            type_name = assignment.assignment_type.value
            assignments_by_type[type_name] += 1

        workload = WeeklyWorkload(
            week_start_date=week_start,
            week_end_date=week_end,
            assignment_count=assignment_count,
            intensity_score=intensity_score,
            assignments_by_type=dict(assignments_by_type)
        )
        workloads.append(workload)

    return workloads
