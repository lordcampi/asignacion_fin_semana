import pytest

from domain.agent import Agent
from services.rule_engine import RuleEngine, RuleViolationError


def test_no_self_review_allowed() -> None:
    agent = Agent(email="a@test.com")

    with pytest.raises(RuleViolationError):
        RuleEngine.validate_no_self_review(
            reviewer=agent,
            reviewed=[agent],
        )


def test_unavailable_agent_not_allowed() -> None:
    reviewer = Agent(email="r@test.com")
    unavailable = Agent(email="u@test.com", disponible=False)

    with pytest.raises(RuleViolationError):
        RuleEngine.validate_availability([unavailable])


def test_sunday_reviewer_can_review_one_saturday_agent() -> None:
    reviewer = Agent(email="r@test.com", turno_domingo=True)
    sat_agent = Agent(email="s1@test.com")
    non_sat_agent = Agent(email="n@test.com")

    RuleEngine.validate_sunday_rule(
        reviewer=reviewer,
        reviewed=[sat_agent, non_sat_agent],
        saturday_agents={"s1@test.com"},
    )


def test_sunday_reviewer_cannot_review_two_saturday_agents() -> None:
    reviewer = Agent(email="r@test.com", turno_domingo=True)
    sat1 = Agent(email="s1@test.com")
    sat2 = Agent(email="s2@test.com")

    with pytest.raises(RuleViolationError):
        RuleEngine.validate_sunday_rule(
            reviewer=reviewer,
            reviewed=[sat1, sat2],
            saturday_agents={"s1@test.com", "s2@test.com"},
        )


def test_non_sunday_reviewer_ignores_sunday_rule() -> None:
    reviewer = Agent(email="r@test.com", turno_domingo=False)
    sat1 = Agent(email="s1@test.com")
    sat2 = Agent(email="s2@test.com")

    RuleEngine.validate_sunday_rule(
        reviewer=reviewer,
        reviewed=[sat1, sat2],
        saturday_agents={"s1@test.com", "s2@test.com"},
    )


def test_validate_assignment_combined_rules() -> None:
    reviewer = Agent(email="r@test.com", turno_domingo=True)
    sat_agent = Agent(email="s1@test.com")
    ok_agent = Agent(email="o@test.com")

    RuleEngine.validate_assignment(
        reviewer=reviewer,
        reviewed=[sat_agent, ok_agent],
        saturday_agents={"s1@test.com"},
    )