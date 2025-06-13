"""
Main entry point for the pix_tell application.

This module provides the main entry point and core functionality for analyzing
and describing images with natural language.

Author: Ron Webb
Since: 1.0.0
"""

from . import __version__
from .util import setup_logger
from .service import analyze_image

logger = setup_logger(__name__)


def main() -> None:
    """
    Main entry point for the application as a chat loop.

    This function starts an interactive chat to analyze and describe images.
    """
    print(
        f"pix-tell v{__version__}: An intelligent AI-powered image analysis application\n"
    )
    logger.info("pix-tell v%s chat started", __version__)

    try:
        while True:
            image_path = get_image_path()
            if image_path is None:
                return
            if handle_image(image_path):
                if not chat_loop(image_path):
                    return
    except KeyboardInterrupt:
        print("\nExiting pix-tell chat.")
        logger.info("pix-tell chat exited by user (KeyboardInterrupt)")
        return


def get_image_path() -> str | None:
    """
    Prompt the user for an image path or URL.
    Returns the path or URL, or None if the user exits.
    """
    while True:
        image_path_input = _prompt_image_path_input()
        if image_path_input is None:
            return None
        if _should_exit_image_path_input(image_path_input):
            print("Exiting pix-tell chat.")
            logger.info("pix-tell chat exited by user before image selection")
            return None
        image_path_input = _strip_quotes_if_present(image_path_input)
        if _is_valid_image_path_input(image_path_input):
            return image_path_input
        print("Please enter a valid image path or URL.")


def _prompt_image_path_input() -> str | None:
    """
    Prompt the user for an image path or URL, handling KeyboardInterrupt.

    Returns:
        The input string, or None if interrupted.
    """
    user_input = None
    try:
        user_input = input(
            "\033[92mEnter the path or URL of the image to analyze (or 'exit' to quit): \033[0m"
        )
        user_input = user_input.strip()
    except KeyboardInterrupt:
        print("\nExiting pix-tell chat.")
        logger.info(
            "pix-tell chat exited by user before image selection (KeyboardInterrupt)"
        )
        return None
    return user_input


def _should_exit_image_path_input(image_path_input: str) -> bool:
    """
    Check if the user input is an exit command.

    Args:
        image_path_input: The user input string to check.

    Returns:
        True if the input is an exit command, False otherwise.
    """
    is_exit = False
    if image_path_input is not None:
        if image_path_input.lower() == "exit":
            is_exit = True
    return is_exit


def _strip_quotes_if_present(image_path_input: str) -> str:
    """
    Remove surrounding single or double quotes from the input if present.

    Args:
        image_path_input: The user input string to process.

    Returns:
        The input string with surrounding quotes removed if present.
    """
    if image_path_input:
        first_char = image_path_input[0]
        last_char = image_path_input[-1]
        if first_char == last_char:
            if first_char in {'"', "'"}:
                stripped = image_path_input[1:-1]
                stripped = stripped.strip()
                return stripped
    return image_path_input


def _is_valid_image_path_input(image_path_input: str) -> bool:
    """
    Check if the image path input is non-empty after stripping.

    Args:
        image_path_input: The user input string to validate.

    Returns:
        True if the input is non-empty, False otherwise.
    """
    is_valid = False
    if image_path_input is not None:
        if len(image_path_input) > 0:
            is_valid = True
    return is_valid


def handle_image(image_path: str) -> bool:
    """
    Validate and caption the image. Returns True if successful, False otherwise.

    Args:
        image_path: The path or URL of the image to analyze.

    Returns:
        True if the image was successfully loaded and captioned, False otherwise.
    """
    try:
        caption = analyze_image(image_path)
        print(f"\033[93mCaption:\033[0m {caption}\n")
        logger.info("Image loaded and captioned: %s", image_path)
        return True
    except (FileNotFoundError, ValueError) as error:
        logger.error("Error loading image: %s", error)
        print(f"Error: {error}\nPlease try again.")
        return False


def _get_question_input() -> str | None:
    """
    Prompt the user for a question about the image, handling KeyboardInterrupt.

    Returns:
        The input string, or None if interrupted.
    """
    try:
        question_input = input(
            "\033[96mAsk a question about the image (or type 'exit' to quit, 'new' for another image): \033[0m"
        ).strip()
        return question_input
    except KeyboardInterrupt:
        print("\nExiting pix-tell chat.")
        logger.info("pix-tell chat exited by user after Q&A (KeyboardInterrupt)")
        return None


def _process_question(image_path: str, question_input: str) -> None:
    """
    Process the user's question about the image, print and log the answer or error.

    Args:
        image_path: The path or URL of the image to analyze.
        question_input: The user's question.
    """
    try:
        answer = analyze_image(image_path, question=question_input)
        print(f"{answer}\n")
        logger.info("Q: %s | A: %s", question_input, answer)
    except (FileNotFoundError, ValueError) as error:
        logger.error("Error: %s", error)
        print(f"Error: {error}\n")


def _detect_chat_command(question_input: str) -> str | None:
    """
    Detect if the input is a chat command ('exit' or 'new').

    Args:
        question_input: The user input string to check.

    Returns:
        'exit', 'new', or None.
    """
    if question_input is not None:
        lowered = question_input.lower()
        if lowered == "exit":
            return "exit"
        if lowered == "new":
            return "new"
    return None


def chat_loop(image_path: str) -> bool:
    """
    Chat loop for asking questions about the image.

    Args:
        image_path: The path or URL of the image to analyze.

    Returns:
        True if the user wants to analyze another image, False to exit.
    """
    while True:
        question_input = _get_question_input()
        if question_input is None:
            return False
        command = _detect_chat_command(question_input)
        if command == "exit":
            print("Exiting pix-tell chat.")
            logger.info("pix-tell chat exited by user after Q&A")
            return False
        if command == "new":
            logger.info("pix-tell chat: user requested new image")
            return True
        question_input = _strip_quotes_if_present(question_input)
        if question_input:
            _process_question(image_path, question_input)
        else:
            print(
                "Please enter a question, 'new' for another image, or 'exit' to quit."
            )
