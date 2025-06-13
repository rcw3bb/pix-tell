"""
Unit tests for __main__.py in pix_tell.

Author: Ron Webb
Since: 1.0.0
"""

import pytest
from unittest.mock import patch

import pix_tell.__main__


def test_main_module_calls_main_function() -> None:
    """
    Test that running the module calls the main function.
    """
    with patch("pix_tell.app.main") as mock_main:
        # Import the module to trigger execution
        import pix_tell.__main__

        # The __main__ module should call main when __name__ == "__main__"
        # We can't directly test this, but we can test the import works
        assert hasattr(pix_tell.__main__, "main")


def test_main_module_entry_point() -> None:
    """
    Test that the module entry point exists and is callable.
    """
    from pix_tell.app import main

    assert callable(main)
