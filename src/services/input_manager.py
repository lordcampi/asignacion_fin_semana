import logging
import re
from collections.abc import Iterable
from typing import TypeAlias

logger = logging.getLogger(__name__)

EmailInput: TypeAlias = str | Iterable[str]


class InputValidationError(ValueError):
    """Raised when input data is invalid or inconsistent."""


class InputManager:
    """
    Handles loading, parsing, normalizing and validating agent input lists.

    Responsibilities:
    - Parse free-text email input.
    - Accept spaces, newlines, commas and semicolons as separators.
    - Normalize emails to lowercase.
    - Remove duplicates while preserving stable order.
    - Validate membership against the master list.
    """

    _EMAIL_SPLIT_PATTERN = re.compile(r"[\s,;]+")

    @staticmethod
    def parse_emails(raw_input: EmailInput) -> list[str]:
        """
        Parses raw email input into a normalized, de-duplicated list.

        Args:
            raw_input: Either a free-text string or an iterable of email strings.

        Returns:
            A list of normalized emails, preserving first occurrence order.

        Raises:
            InputValidationError: If raw_input has an unsupported type.
        """
        logger.debug("Parsing raw email input")

        if isinstance(raw_input, str):
            tokens = InputManager._EMAIL_SPLIT_PATTERN.split(raw_input)
        elif isinstance(raw_input, Iterable):
            tokens = []
            for item in raw_input:
                tokens.extend(InputManager._EMAIL_SPLIT_PATTERN.split(item))
        else:
            raise InputValidationError(
                f"Unsupported input type: {type(raw_input).__name__}"
            )

        normalized: list[str] = []
        seen: set[str] = set()

        for token in tokens:
            email = token.strip().lower()
            if not email:
                continue

            if email in seen:
                logger.debug("Duplicate email removed during normalization: %s", email)
                continue

            seen.add(email)
            normalized.append(email)

        logger.debug("Parsed %d unique emails", len(normalized))
        return normalized

    @staticmethod
    def find_duplicates(raw_input: EmailInput) -> list[str]:
        """
        Finds duplicated emails after normalization.

        This is useful for UI layers such as Streamlit, where duplicates can be
        removed automatically but still shown as a warning to the user.

        Args:
            raw_input: Either a free-text string or an iterable of email strings.

        Returns:
            A sorted list of duplicated normalized emails.
        """
        logger.debug("Finding duplicated emails")

        if isinstance(raw_input, str):
            tokens = InputManager._EMAIL_SPLIT_PATTERN.split(raw_input)
        else:
            tokens = []
            for item in raw_input:
                tokens.extend(InputManager._EMAIL_SPLIT_PATTERN.split(item))

        counts: dict[str, int] = {}

        for token in tokens:
            email = token.strip().lower()
            if not email:
                continue
            counts[email] = counts.get(email, 0) + 1

        duplicates = sorted(email for email, count in counts.items() if count > 1)
        logger.debug("Found duplicates: %s", duplicates)
        return duplicates

    @staticmethod
    def validate_lists(
        *,
        all_agents: EmailInput,
        saturday: EmailInput,
        sunday: EmailInput,
        vacations: EmailInput,
    ) -> dict[str, set[str]]:
        """
        Validates and normalizes all input lists.

        Args:
            all_agents: Master list of all agents.
            saturday: Agents working on Saturday.
            sunday: Agents working on Sunday.
            vacations: Agents on vacation or leave.

        Returns:
            A dictionary with normalized sets for each input category.

        Raises:
            InputValidationError: If any agent in saturday, sunday or vacations
                is not present in the master list.
        """
        logger.info("Validating input lists")

        all_agents_normalized = InputManager.parse_emails(all_agents)
        saturday_normalized = InputManager.parse_emails(saturday)
        sunday_normalized = InputManager.parse_emails(sunday)
        vacations_normalized = InputManager.parse_emails(vacations)

        all_agents_set = set(all_agents_normalized)

        groups = {
            "saturday": saturday_normalized,
            "sunday": sunday_normalized,
            "vacations": vacations_normalized,
        }

        for group_name, group_emails in groups.items():
            invalid_agents = set(group_emails) - all_agents_set

            if invalid_agents:
                logger.warning(
                    "Invalid agents in %s not present in master list: %s",
                    group_name,
                    sorted(invalid_agents),
                )
                raise InputValidationError(
                    f"Agents in {group_name} not in master list: "
                    f"{sorted(invalid_agents)}"
                )

        return {
            "all_agents": all_agents_set,
            "saturday": set(saturday_normalized),
            "sunday": set(sunday_normalized),
            "vacations": set(vacations_normalized),
        }