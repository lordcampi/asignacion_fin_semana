import logging
from typing import Iterable, Set

from domain.agent import Agent

logger = logging.getLogger(__name__)


class RuleViolationError(ValueError):
    """Raised when a business rule is violated."""


class RuleEngine:
    """
    Applies business rules to review assignments.

    Scope:
    - No self-review
    - No review of unavailable agents
    - Sunday rule:
      A Sunday reviewer may review at most ONE agent
      who worked on Saturday.
    """

    @staticmethod
    def validate_no_self_review(
        reviewer: Agent,
        reviewed: Iterable[Agent],
    ) -> None:
        """
        Ensures an agent does not review themselves.

        Args:
            reviewer: The reviewing agent.
            reviewed: Agents being reviewed.

        Raises:
            RuleViolationError: If self-review is detected.
        """
        for agent in reviewed:
            if agent.email == reviewer.email:
                raise RuleViolationError(
                    f"Agent {reviewer.email} cannot review themselves"
                )

    @staticmethod
    def validate_availability(
        reviewed: Iterable[Agent],
    ) -> None:
        """
        Ensures all reviewed agents are available.

        Args:
            reviewed: Agents being reviewed.

        Raises:
            RuleViolationError: If any agent is unavailable.
        """
        unavailable = [a.email for a in reviewed if not a.disponible]
        if unavailable:
            raise RuleViolationError(
                f"Unavailable agents cannot be reviewed: {unavailable}"
            )

    @staticmethod
    def validate_sunday_rule(
        *,
        reviewer: Agent,
        reviewed: Iterable[Agent],
        saturday_agents: Set[str],
    ) -> None:
        """
        Enforces the Sunday rule:
        A Sunday reviewer may review at most ONE agent
        who worked on Saturday.

        Args:
            reviewer: The reviewing agent.
            reviewed: Agents being reviewed.
            saturday_agents: Emails of agents who worked Saturday.

        Raises:
            RuleViolationError: If the rule is violated.
        """
        if not reviewer.turno_domingo:
            return

        saturday_reviewed = [
            a.email for a in reviewed if a.email in saturday_agents
        ]

        if len(saturday_reviewed) > 1:
            logger.debug(
                "Sunday rule violated by %s: %s",
                reviewer.email,
                saturday_reviewed,
            )
            raise RuleViolationError(
                f"Sunday reviewer {reviewer.email} "
                f"cannot review more than one Saturday agent "
                f"(found {len(saturday_reviewed)})"
            )

    @staticmethod
    def validate_assignment(
        *,
        reviewer: Agent,
        reviewed: Iterable[Agent],
        saturday_agents: Set[str],
    ) -> None:
        """
        Validates all business rules for an assignment.

        Args:
            reviewer: The reviewing agent.
            reviewed: Agents being reviewed.
            saturday_agents: Emails of Saturday agents.

        Raises:
            RuleViolationError: If any rule is violated.
        """
        RuleEngine.validate_no_self_review(reviewer, reviewed)
        RuleEngine.validate_availability(reviewed)
        RuleEngine.validate_sunday_rule(
            reviewer=reviewer,
            reviewed=reviewed,
            saturday_agents=saturday_agents,
        )