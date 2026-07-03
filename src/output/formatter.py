# OutputFormatter
from typing import Dict, List


class OutputFormatter:
    """
    Formats and displays assignment results.
    """

    @staticmethod
    def print_assignments(assignments: Dict[str, List[str]], day: str) -> None:
        """
        Prints assignments to console.

        Args:
            assignments: reviewer_email -> list of reviewed emails
            day: Day label (e.g. 'Saturday', 'Sunday')
        """
        print(f"\n=== Assignments for {day} ===")

        for reviewer, reviewed in assignments.items():
            reviewed_str = ", ".join(reviewed) if reviewed else "—"
            print(f"{reviewer} -> {reviewed_str}")