import pytest

from domain.agent import Agent, AgentValidationError


def test_create_valid_agent() -> None:
    agent = Agent(
        email="agent@test.com",
        disponible=True,
        turno_sabado=True,
        turno_domingo=False,
    )

    assert agent.email == "agent@test.com"
    assert agent.disponible is True
    assert agent.turno_sabado is True
    assert agent.turno_domingo is False


def test_invalid_email_raises_error() -> None:
    with pytest.raises(AgentValidationError):
        Agent(email="invalid-email")


def test_is_weekend_worker_true() -> None:
    agent = Agent(email="agent@test.com", turno_domingo=True)
    assert agent.is_weekend_worker() is True


def test_is_weekend_worker_false() -> None:
    agent = Agent(email="agent@test.com")
    assert agent.is_weekend_worker() is False


def test_is_available_for_review() -> None:
    agent = Agent(email="agent@test.com", disponible=False)
    assert agent.is_available_for_review() is False


def test_to_dict() -> None:
    agent = Agent(
        email="agent@test.com",
        disponible=True,
        turno_sabado=False,
        turno_domingo=True,
    )

    data = agent.to_dict()

    assert data == {
        "email": "agent@test.com",
        "disponible": True,
        "turno_sabado": False,
        "turno_domingo": True,
    }
