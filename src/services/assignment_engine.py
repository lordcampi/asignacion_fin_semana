import logging
from typing import Dict, List, Set

from domain.agent import Agent
from services.rule_engine import RuleEngine, RuleViolationError
from services.balance_engine import BalanceEngine

logger = logging.getLogger(__name__)


class AssignmentError(RuntimeError):
    """Raised when no valid assignment can be generated."""


class AssignmentEngine:
    """
    Generates valid and balanced review assignments.

    Responsibilities:
    - Generate reviewer -> reviewed mappings
    - Enforce all business rules via RuleEngine
    - Balance load deterministically (fewer cases first)
    """

    def __init__(self) -> None:
        self.balance = BalanceEngine()

    def assign(
        self,
        *,
        reviewers: List[Agent],
        candidates: List[Agent],
        saturday_agents: Set[str],
        max_reviews_per_reviewer: int,
    ) -> Dict[str, List[str]]:
        """
        Generates valid and balanced assignments.

        Args:
            reviewers: Agents who perform reviews.
            candidates: Agents that can be reviewed.
            saturday_agents: Emails of agents who worked Saturday.
            max_reviews_per_reviewer: Max number of reviews per reviewer.

        Returns:
            Dict[str, List[str]]: reviewer_email -> list of reviewed emails

        Raises:
            AssignmentError: If no valid assignment can be generated.
        """
        assignments: Dict[str, List[str]] = {
            r.email: [] for r in reviewers
        }

        sorted_reviewers = self.balance.get_sorted_reviewers(reviewers)

        for reviewer in sorted_reviewers:
            logger.info("Assigning reviews for %s", reviewer.email)

            available_candidates = [
                c
                for c in candidates
                if c.email != reviewer.email
                and c.disponible
                and c.email not in assignments[reviewer.email]
            ]

            for candidate in available_candidates:
                if len(assignments[reviewer.email]) >= max_reviews_per_reviewer:
                    break

                tentative_emails = assignments[reviewer.email] + [candidate.email]
                tentative_agents = [
                    c for c in candidates if c.email in tentative_emails
                ]

                try:
                    RuleEngine.validate_assignment(
                        reviewer=reviewer,
                        reviewed=tentative_agents,
                        saturday_agents=saturday_agents,
                    )
                except RuleViolationError:
                    logger.debug(
                        "Skipping candidate %s for reviewer %s due to rule violation",
                        candidate.email,
                        reviewer.email,
                    )
                    continue

                assignments[reviewer.email].append(candidate.email)
                self.balance.register_assignment(reviewer)

        if all(len(reviews) == 0 for reviews in assignments.values()):
            logger.error("No valid assignment found for any reviewer")
            raise AssignmentError("No valid assignment found")

        return assignments