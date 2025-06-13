"""
Unit tests for __init__.py in pix_tell.

Author: Ron Webb
Since: 1.0.0
"""

import pix_tell


def test_version_defined() -> None:
    """
    Test that __version__ is defined and correct.
    """
    assert hasattr(pix_tell, "__version__")
    assert pix_tell.__version__ == "1.0.0"
