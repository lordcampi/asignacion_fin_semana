# Entry point
import logging

from domain.agent import Agent
from services.input_manager import InputManager
from services.assignment_engine import AssignmentEngine
from output.formatter import OutputFormatter

logging.basicConfig(level=logging.INFO)


def _read_list(prompt: str) -> list[str]:
    """
    Reads a comma-separated list from input.

    Args:
        prompt: Input prompt.

    Returns:
        List of strings.
    """
    raw = input(prompt).strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",")]


def main() -> None:
    print("=== Weekend Review Assignment System ===\n")
    print("Enter emails separated by commas.\n")

    all_agents = _read_list("All agents: ")
    saturday = _read_list("Saturday agents: ")
    sunday = _read_list("Sunday agents: ")
    vacations = _read_list("Vacation / leave agents: ")

    validated = InputManager.validate_lists(
        all_agents=all_agents,
        saturday=saturday,
        sunday=sunday,
        vacations=vacations,
    )

    agents = {
        email: Agent(
            email=email,
            disponible=email not in validated["vacations"],
            turno_sabado=email in validated["saturday"],
            turno_domingo=email in validated["sunday"],
        )
        for email in validated["all_agents"]
    }

    engine = AssignmentEngine()

    # === Saturday ===
    saturday_reviewers = [
        agents[e] for e in validated["saturday"]
        if agents[e].disponible
    ]

    saturday_candidates = [
        a for a in agents.values()
        if a.disponible and not a.turno_sabado
    ]

    saturday_assignments = engine.assign(
        reviewers=saturday_reviewers,
        candidates=saturday_candidates,
        saturday_agents=set(),
        max_reviews_per_reviewer=3,
    )

    OutputFormatter.print_assignments(
        saturday_assignments,
        day="Saturday",
    )

    # === Sunday ===
    sunday_reviewers = [
        agents[e] for e in validated["sunday"]
        if agents[e].disponible
    ]

    sunday_candidates = [
        a for a in agents.values()
        if a.disponible and not a.turno_domingo
    ]

    sunday_assignments = engine.assign(
        reviewers=sunday_reviewers,
        candidates=sunday_candidates,
        saturday_agents=validated["saturday"],
        max_reviews_per_reviewer=3,
    )

    OutputFormatter.print_assignments(
        sunday_assignments,
        day="Sunday",
    )


if __name__ == "__main__":
    main()