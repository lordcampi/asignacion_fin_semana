# BalanceEngine service
import logging
from collections import defaultdict
from typing import Dict, List

from domain.agent import Agent

logger = logging.getLogger(__name__)


class BalanceEngine:
    """
    Keeps track of review load and provides deterministic balancing.

    Rule:
    - The agent with fewer assigned reviews is prioritized.
    - Stable tie-breaker: email ascending.
    """

    def __init__(self) -> None:
        self._counts: Dict[str, int] = defaultdict(int)

    def register_assignment(self, reviewer: Agent, count: int = 1) -> None:
        self._counts[reviewer.email] += count
        logger.debug(
            "Registered %d reviews for %s (total=%d)",
            count,
            reviewer.email,
            self._counts[reviewer.email],
        )

    def get_sorted_reviewers(self, reviewers: List[Agent]) -> List[Agent]:
        """
        Returns reviewers sorted by:
        1) Fewer current reviews
        2) Stable email order
        """
        return sorted(
            reviewers,
            key=lambda a: (self._counts[a.email], a.email),
        )

    def get_count(self, reviewer: Agent) -> int:
        return self._counts[reviewer.email]