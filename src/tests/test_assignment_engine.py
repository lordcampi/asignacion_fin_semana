from domain.agent import Agent
from services.assignment_engine import AssignmentEngine, AssignmentError


def test_balanced_assignment_prefers_less_loaded_agent() -> None:
    engine = AssignmentEngine()

    reviewers = [
        Agent(email="a@test.com"),
        Agent(email="b@test.com"),
    ]

    candidates = [
        Agent(email="c@test.com"),
        Agent(email="d@test.com"),
    ]

    result = engine.assign(
        reviewers=reviewers,
        candidates=candidates,
        saturday_agents=set(),
        max_reviews_per_reviewer=1,
    )

    # Both reviewers should get exactly one review
    assert len(result["a@test.com"]) == 1
    assert len(result["b@test.com"]) == 1


def test_sunday_rule_enforced() -> None:
    engine = AssignmentEngine()

    reviewer = Agent(email="r@test.com", turno_domingo=True)
    sat1 = Agent(email="s1@test.com")
    sat2 = Agent(email="s2@test.com")

    result = engine.assign(
        reviewers=[reviewer],
        candidates=[sat1, sat2],
        saturday_agents={"s1@test.com", "s2@test.com"},
        max_reviews_per_reviewer=2,
    )

    # Sunday reviewer can only review ONE Saturday agent
    assert len(result["r@test.com"]) == 1


def test_no_assignment_raises_error() -> None:
    engine = AssignmentEngine()

    reviewer = Agent(email="a@test.com")
    candidate = Agent(email="a@test.com")  # self-review only

    try:
        engine.assign(
            reviewers=[reviewer],
            candidates=[candidate],
            saturday_agents=set(),
            max_reviews_per_reviewer=1,
        )
    except AssignmentError:
        assert True
    else:
        assert False
