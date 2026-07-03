import logging
from dataclasses import dataclass
from typing import Final

import streamlit as st

from domain.agent import Agent
from services.assignment_engine import AssignmentEngine
from services.input_manager import InputManager, InputValidationError

logger = logging.getLogger(__name__)

MAX_REVIEWS_PER_REVIEWER: Final[int] = 3


class DashboardError(RuntimeError):
    """Raised when dashboard assignment generation fails."""


@dataclass(frozen=True)
class DashboardAssignments:
    """Assignment result for the Streamlit dashboard.

    Attributes:
        saturday: Saturday assignments.
        sunday: Sunday assignments.
    """

    saturday: dict[str, list[str]]
    sunday: dict[str, list[str]]


def _build_agents(validated: dict[str, set[str]]) -> dict[str, Agent]:
    """Builds Agent entities from validated input data.

    Args:
        validated: Validated input sets returned by InputManager.

    Returns:
        Dictionary mapping email to Agent.
    """
    return {
        email: Agent(
            email=email,
            disponible=email not in validated["vacations"],
            turno_sabado=email in validated["saturday"],
            turno_domingo=email in validated["sunday"],
        )
        for email in sorted(validated["all_agents"])
    }


def generate_dashboard_assignments(
    *,
    all_agents_raw: str,
    saturday_raw: str,
    sunday_raw: str,
    vacations_raw: str,
) -> DashboardAssignments:
    """Generates Saturday and Sunday assignments from dashboard raw inputs.

    Args:
        all_agents_raw: Raw free-text master agent list.
        saturday_raw: Raw free-text Saturday agent list.
        sunday_raw: Raw free-text Sunday agent list.
        vacations_raw: Raw free-text vacation or leave agent list.

    Returns:
        DashboardAssignments with Saturday and Sunday assignments.

    Raises:
        InputValidationError: If input validation fails.
        DashboardError: If assignment generation fails unexpectedly.
    """
    logger.info("Generating dashboard assignments")

    validated = InputManager.validate_lists(
        all_agents=all_agents_raw,
        saturday=saturday_raw,
        sunday=sunday_raw,
        vacations=vacations_raw,
    )

    agents = _build_agents(validated)

    saturday_reviewers = [
        agents[email]
        for email in sorted(validated["saturday"])
        if agents[email].disponible
    ]
    saturday_candidates = [
        agent
        for agent in agents.values()
        if agent.disponible and not agent.turno_sabado
    ]

    sunday_reviewers = [
        agents[email]
        for email in sorted(validated["sunday"])
        if agents[email].disponible
    ]
    sunday_candidates = [
        agent
        for agent in agents.values()
        if agent.disponible and not agent.turno_domingo
    ]

    engine = AssignmentEngine()

    try:
        saturday_assignments = (
            engine.assign(
                reviewers=saturday_reviewers,
                candidates=saturday_candidates,
                saturday_agents=set(),
                max_reviews_per_reviewer=MAX_REVIEWS_PER_REVIEWER,
            )
            if saturday_reviewers
            else {}
        )

        sunday_assignments = (
            engine.assign(
                reviewers=sunday_reviewers,
                candidates=sunday_candidates,
                saturday_agents=validated["saturday"],
                max_reviews_per_reviewer=MAX_REVIEWS_PER_REVIEWER,
            )
            if sunday_reviewers
            else {}
        )
    except Exception as exc:
        logger.exception("Failed to generate dashboard assignments")
        raise DashboardError("Could not generate assignments") from exc

    return DashboardAssignments(
        saturday=saturday_assignments,
        sunday=sunday_assignments,
    )


def assignments_to_rows(assignments: dict[str, list[str]]) -> list[dict[str, str]]:
    """Converts assignments into table rows.

    Args:
        assignments: Mapping reviewer email to reviewed email list.

    Returns:
        List of table rows.
    """
    rows: list[dict[str, str]] = []

    for reviewer, reviewed_agents in assignments.items():
        if not reviewed_agents:
            rows.append(
                {
                    "Revisor": reviewer,
                    "Revisado": "—",
                }
            )
            continue

        for reviewed in reviewed_agents:
            rows.append(
                {
                    "Revisor": reviewer,
                    "Revisado": reviewed,
                }
            )

    return rows


def _show_duplicate_warnings(
    *,
    all_agents_raw: str,
    saturday_raw: str,
    sunday_raw: str,
    vacations_raw: str,
) -> None:
    """Shows duplicate warnings in Streamlit UI.

    Args:
        all_agents_raw: Raw master agent list.
        saturday_raw: Raw Saturday agent list.
        sunday_raw: Raw Sunday agent list.
        vacations_raw: Raw vacation or leave agent list.
    """
    duplicate_groups = {
        "Todos los agentes": InputManager.find_duplicates(all_agents_raw),
        "Turno sábado": InputManager.find_duplicates(saturday_raw),
        "Turno domingo": InputManager.find_duplicates(sunday_raw),
        "Vacaciones / licencia": InputManager.find_duplicates(vacations_raw),
    }

    for label, duplicates in duplicate_groups.items():
        if duplicates:
            st.warning(
                f"Duplicados eliminados automáticamente en '{label}': "
                f"{', '.join(duplicates)}"
            )


def run_app() -> None:
    """Runs the Streamlit dashboard."""
    st.set_page_config(
        page_title="Asignador de revisiones fin de semana",
        layout="wide",
    )

    st.title("Asignador de revisiones de fin de semana")
    st.caption(
        "Pega los correos separados por espacios, saltos de línea, comas "
        "o cualquier combinación."
    )

    with st.form("assignment_form"):
        all_agents_raw = st.text_area(
            "Todos los agentes",
            height=160,
            placeholder="correo1@empresa.com correo2@empresa.com",
        )

        col1, col2 = st.columns(2)

        with col1:
            saturday_raw = st.text_area(
                "Agentes turno sábado",
                height=140,
            )

        with col2:
            sunday_raw = st.text_area(
                "Agentes turno domingo",
                height=140,
            )

        vacations_raw = st.text_area(
            "Agentes en vacaciones / licencia",
            height=120,
        )

        submitted = st.form_submit_button("Generar asignaciones")

    if not submitted:
        return

    try:
        _show_duplicate_warnings(
            all_agents_raw=all_agents_raw,
            saturday_raw=saturday_raw,
            sunday_raw=sunday_raw,
            vacations_raw=vacations_raw,
        )

        result = generate_dashboard_assignments(
            all_agents_raw=all_agents_raw,
            saturday_raw=saturday_raw,
            sunday_raw=sunday_raw,
            vacations_raw=vacations_raw,
        )
    except InputValidationError as exc:
        logger.warning("Input validation failed: %s", exc)
        st.error(str(exc))
        return
    except DashboardError as exc:
        logger.error("Dashboard generation failed: %s", exc)
        st.error(str(exc))
        return

    st.subheader("Asignaciones sábado")
    saturday_rows = assignments_to_rows(result.saturday)
    if saturday_rows:
        st.table(saturday_rows)
    else:
        st.info("No hay agentes asignados para sábado.")

    st.subheader("Asignaciones domingo")
    sunday_rows = assignments_to_rows(result.sunday)
    if sunday_rows:
        st.table(sunday_rows)
    else:
        st.info("No hay agentes asignados para domingo.")


if __name__ == "__main__":
    run_app()