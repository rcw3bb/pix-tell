"""
Unit tests for app module in pix_tell.

Author: Ron Webb
Since: 1.0.0
"""

import pytest
from unittest.mock import patch, MagicMock

import pix_tell.app as app


def test_strip_quotes_if_present_removes_quotes() -> None:
    """
    Test that _strip_quotes_if_present removes surrounding quotes.
    """
    assert app._strip_quotes_if_present('"foo"') == "foo"
    assert app._strip_quotes_if_present("'bar'") == "bar"
    assert app._strip_quotes_if_present("baz") == "baz"
    assert app._strip_quotes_if_present('"baz') == '"baz'
    assert app._strip_quotes_if_present('baz"') == 'baz"'


def test_is_valid_image_path_input() -> None:
    """
    Test that _is_valid_image_path_input returns True for non-empty, False for empty.
    """
    assert app._is_valid_image_path_input("foo") is True
    assert app._is_valid_image_path_input("") is False
    assert app._is_valid_image_path_input(None) is False


def test_should_exit_image_path_input() -> None:
    """
    Test that _should_exit_image_path_input returns True for 'exit', False otherwise.
    """
    assert app._should_exit_image_path_input("exit") is True
    assert app._should_exit_image_path_input("EXIT") is True
    assert app._should_exit_image_path_input("foo") is False
    assert app._should_exit_image_path_input(None) is False


def test_detect_chat_command() -> None:
    """
    Test that _detect_chat_command returns 'exit', 'new', or None.
    """
    assert app._detect_chat_command("exit") == "exit"
    assert app._detect_chat_command("new") == "new"
    assert app._detect_chat_command("foo") is None
    assert app._detect_chat_command(None) is None


def test_handle_image_success_and_failure() -> None:
    """
    Test handle_image returns True on success, False on error.
    """
    with patch("pix_tell.app.analyze_image", return_value="caption") as mock_analyze:
        assert app.handle_image("foo.png") is True
    with patch("pix_tell.app.analyze_image", side_effect=FileNotFoundError("fail")):
        assert app.handle_image("foo.png") is False
    with patch("pix_tell.app.analyze_image", side_effect=ValueError("fail")):
        assert app.handle_image("foo.png") is False


def test_get_image_path_valid_input() -> None:
    """
    Test get_image_path with valid input.
    """
    with patch("builtins.input", return_value="test.jpg"):
        result = app.get_image_path()
        assert result == "test.jpg"


def test_get_image_path_with_quotes() -> None:
    """
    Test get_image_path strips quotes from input.
    """
    with patch("builtins.input", return_value='"test.jpg"'):
        result = app.get_image_path()
        assert result == "test.jpg"


def test_get_image_path_exit_command() -> None:
    """
    Test get_image_path with exit command returns None.
    """
    with patch("builtins.input", return_value="exit"):
        result = app.get_image_path()
        assert result is None


def test_get_image_path_empty_input_then_valid() -> None:
    """
    Test get_image_path with empty input followed by valid input.
    """
    with patch("builtins.input", side_effect=["", "test.jpg"]):
        result = app.get_image_path()
        assert result == "test.jpg"


def test_get_image_path_keyboard_interrupt() -> None:
    """
    Test get_image_path handles KeyboardInterrupt.
    """
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        result = app.get_image_path()
        assert result is None


def test_chat_loop_exit_command() -> None:
    """
    Test chat_loop with exit command returns False.
    """
    with patch("builtins.input", return_value="exit"):
        result = app.chat_loop("test.jpg")
        assert result is False


def test_chat_loop_new_command() -> None:
    """
    Test chat_loop with new command returns True.
    """
    with patch("builtins.input", return_value="new"):
        result = app.chat_loop("test.jpg")
        assert result is True


def test_chat_loop_question_and_answer() -> None:
    """
    Test chat_loop processes question and gets answer.
    """
    with (
        patch("builtins.input", side_effect=["What is this?", "exit"]),
        patch("pix_tell.app.analyze_image", return_value="A test image"),
    ):
        result = app.chat_loop("test.jpg")
        assert result is False


def test_chat_loop_empty_question() -> None:
    """
    Test chat_loop handles empty question input.
    """
    with patch("builtins.input", side_effect=["", "exit"]):
        result = app.chat_loop("test.jpg")
        assert result is False


def test_chat_loop_keyboard_interrupt() -> None:
    """
    Test chat_loop handles KeyboardInterrupt.
    """
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        result = app.chat_loop("test.jpg")
        assert result is False


def test_chat_loop_analyze_image_error() -> None:
    """
    Test chat_loop handles analyze_image error.
    """
    with (
        patch("builtins.input", side_effect=["What is this?", "exit"]),
        patch("pix_tell.app.analyze_image", side_effect=ValueError("Test error")),
    ):
        result = app.chat_loop("test.jpg")
        assert result is False


def test_main_function_keyboard_interrupt() -> None:
    """
    Test main function handles KeyboardInterrupt.
    """
    with patch("pix_tell.app.get_image_path", side_effect=KeyboardInterrupt):
        app.main()  # Should not raise exception


def test_main_function_normal_flow() -> None:
    """
    Test main function normal flow with image analysis.
    """
    with (
        patch("pix_tell.app.get_image_path", side_effect=["test.jpg", None]),
        patch("pix_tell.app.handle_image", return_value=True),
        patch("pix_tell.app.chat_loop", return_value=False),
    ):
        app.main()  # Should complete normally


def test_main_function_handle_image_failure() -> None:
    """
    Test main function when handle_image fails.
    """
    with (
        patch("pix_tell.app.get_image_path", side_effect=["bad.jpg", None]),
        patch("pix_tell.app.handle_image", return_value=False),
    ):
        app.main()  # Should complete normally
