# Agent domain model
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


class AgentValidationError(ValueError):
    """Raised when an Agent is created with invalid data."""


@dataclass(frozen=True)
class Agent:
    """
    Domain entity representing an agent.

    Attributes:
        email (str): Unique identifier of the agent.
        disponible (bool): Whether the agent is available.
        turno_sabado (bool): Whether the agent works on Saturday.
        turno_domingo (bool): Whether the agent works on Sunday.
    """

    email: str
    disponible: bool = True
    turno_sabado: bool = False
    turno_domingo: bool = False

    def __post_init__(self) -> None:
        """
        Validates the agent data after initialization.

        Raises:
            AgentValidationError: If the email is invalid.
        """
        logger.debug("Initializing Agent: %s", self.email)

        if not self.email or "@" not in self.email:
            logger.error("Invalid agent email: %s", self.email)
            raise AgentValidationError(f"Invalid email for agent: {self.email}")

    def is_weekend_worker(self) -> bool:
        """
        Checks if the agent works on any weekend day.

        Returns:
            bool: True if works Saturday or Sunday.
        """
        return self.turno_sabado or self.turno_domingo

    def is_available_for_review(self) -> bool:
        """
        Checks if the agent can participate in reviews.

        Returns:
            bool: True if the agent is available.
        """
        return self.disponible

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the agent to a dictionary.

        Returns:
            dict[str, Any]: Agent data.
        """
        return {
            "email": self.email,
            "disponible": self.disponible,
            "turno_sabado": self.turno_sabado,
            "turno_domingo": self.turno_domingo,
        }