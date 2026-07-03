import pytest

from services.input_manager import InputManager, InputValidationError


def test_parse_emails_from_spaces() -> None:
    result = InputManager.parse_emails(
        "a@test.com b@test.com c@test.com"
    )

    assert result == ["a@test.com", "b@test.com", "c@test.com"]


def test_parse_emails_from_newlines() -> None:
    result = InputManager.parse_emails(
        """
        a@test.com
        b@test.com
        c@test.com
        """
    )

    assert result == ["a@test.com", "b@test.com", "c@test.com"]


def test_parse_emails_from_commas_spaces_and_newlines() -> None:
    result = InputManager.parse_emails(
        """
        A@TEST.COM, b@test.com
        c@test.com d@test.com
        """
    )

    assert result == [
        "a@test.com",
        "b@test.com",
        "c@test.com",
        "d@test.com",
    ]


def test_parse_emails_removes_duplicates_preserving_order() -> None:
    result = InputManager.parse_emails(
        """
        b@test.com
        a@test.com
        b@test.com
        c@test.com
        a@test.com
        """
    )

    assert result == ["b@test.com", "a@test.com", "c@test.com"]


def test_find_duplicates() -> None:
    result = InputManager.find_duplicates(
        """
        a@test.com
        b@test.com
        A@TEST.COM
        c@test.com
        b@test.com
        """
    )

    assert result == ["a@test.com", "b@test.com"]


def test_validate_lists_with_free_text_inputs() -> None:
    result = InputManager.validate_lists(
        all_agents="""
            a@test.com
            b@test.com c@test.com
            d@test.com
        """,
        saturday="a@test.com b@test.com",
        sunday="""
            c@test.com
        """,
        vacations="d@test.com",
    )

    assert result["all_agents"] == {
        "a@test.com",
        "b@test.com",
        "c@test.com",
        "d@test.com",
    }
    assert result["saturday"] == {"a@test.com", "b@test.com"}
    assert result["sunday"] == {"c@test.com"}
    assert result["vacations"] == {"d@test.com"}


def test_validate_lists_removes_duplicates_without_error() -> None:
    result = InputManager.validate_lists(
        all_agents="""
            a@test.com
            a@test.com
            b@test.com
        """,
        saturday="""
            a@test.com
            a@test.com
        """,
        sunday="b@test.com",
        vacations="",
    )

    assert result["all_agents"] == {"a@test.com", "b@test.com"}
    assert result["saturday"] == {"a@test.com"}
    assert result["sunday"] == {"b@test.com"}
    assert result["vacations"] == set()


def test_agent_not_in_master_list_raises() -> None:
    with pytest.raises(InputValidationError):
        InputManager.validate_lists(
            all_agents="a@test.com",
            saturday="b@test.com",
            sunday="",
            vacations="",
        )


def test_parse_iterable_input() -> None:
    result = InputManager.parse_emails(
        [" A@TEST.COM ", "b@test.com c@test.com"]
    )

    assert result == ["a@test.com", "b@test.com", "c@test.com"]