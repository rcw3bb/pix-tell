"""
Unit tests for service module in pix_tell.

Author: Ron Webb
Since: 1.0.0
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
import requests

import pix_tell.service as service


def test_validate_image_path_empty_raises_value_error() -> None:
    """
    Test that _validate_image_path raises ValueError for empty path.
    """
    with pytest.raises(ValueError):
        service._validate_image_path("")


def test_validate_image_path_nonexistent_file_raises_file_not_found() -> None:
    """
    Test that _validate_image_path raises FileNotFoundError for missing file.
    """
    with pytest.raises(FileNotFoundError):
        service._validate_image_path("not_a_real_file.png")


def test_validate_image_path_url_returns_true() -> None:
    """
    Test that _validate_image_path returns True for a valid URL.
    """
    url = "http://example.com/image.png"
    with patch("os.path.isfile", return_value=False):
        assert service._validate_image_path(url) is True


def test_validate_image_path_local_file_returns_false(tmp_path) -> None:
    """
    Test that _validate_image_path returns False for a valid local file.
    """
    file_path = tmp_path / "test.png"
    file_path.write_bytes(b"fake image data")
    with patch("os.path.isfile", return_value=True):
        assert service._validate_image_path(str(file_path)) is False


def test_load_image_local_file_opens_image(tmp_path) -> None:
    """
    Test that _load_image opens a local image file.
    """
    file_path = tmp_path / "test.png"
    img = Image.new("RGB", (10, 10))
    img.save(file_path)
    loaded = service._load_image(str(file_path), is_url=False)
    assert isinstance(loaded, Image.Image)


def test_load_image_url_opens_image() -> None:
    """
    Test that _load_image opens an image from a URL.
    """
    fake_image = Image.new("RGB", (10, 10))
    buf = MagicMock()
    buf.read.return_value = b"fake"
    with (
        patch("requests.get") as mock_get,
        patch("PIL.Image.open", return_value=fake_image) as mock_open,
    ):
        mock_get.return_value.content = b"fake"
        mock_get.return_value.raise_for_status = lambda: None
        img = service._load_image("http://example.com/image.png", is_url=True)
        assert isinstance(img, Image.Image)


def test_perform_vqa_returns_answer() -> None:
    """
    Test that _perform_vqa returns the answer from the pipeline.
    """
    image = Image.new("RGB", (10, 10))
    # Patch pipeline to return a mock object whose __call__ returns the expected result
    with (
        patch(
            "pix_tell.service.pipeline",
            return_value=lambda *a, **kw: [{"answer": "cat"}],
        ),
        patch("transformers.BlipProcessor.from_pretrained", return_value=MagicMock()),
    ):
        answer = service._perform_vqa(image, "What is in the image?")
        assert answer == "cat"


def test_perform_vqa_unexpected_response_raises_value_error() -> None:
    """
    Test that _perform_vqa raises ValueError for unexpected response.
    """
    image = Image.new("RGB", (10, 10))
    with (
        patch("pix_tell.service.pipeline", return_value=lambda *a, **kw: [{}]),
        patch("transformers.BlipProcessor.from_pretrained", return_value=MagicMock()),
    ):
        with pytest.raises(ValueError):
            service._perform_vqa(image, "What is in the image?")


def test_perform_captioning_returns_caption() -> None:
    """
    Test that _perform_captioning returns the caption from the pipeline.
    """
    image = Image.new("RGB", (10, 10))
    with (
        patch("transformers.BlipProcessor.from_pretrained", return_value=MagicMock()),
        patch(
            "transformers.BlipForConditionalGeneration.from_pretrained",
            return_value=MagicMock(),
        ),
        patch(
            "pix_tell.service.pipeline",
            return_value=lambda *a, **kw: [{"generated_text": "A cat on a mat."}],
        ),
    ):
        caption = service._perform_captioning(image)
        assert caption == "A cat on a mat."


def test_perform_captioning_unexpected_response_raises_value_error() -> None:
    """
    Test that _perform_captioning raises ValueError for unexpected response.
    """
    image = Image.new("RGB", (10, 10))
    with (
        patch("transformers.BlipProcessor.from_pretrained", return_value=MagicMock()),
        patch(
            "transformers.BlipForConditionalGeneration.from_pretrained",
            return_value=MagicMock(),
        ),
        patch("pix_tell.service.pipeline", return_value=lambda *a, **kw: [{}]),
    ):
        with pytest.raises(ValueError):
            service._perform_captioning(image)


def test_configure_transformers_logging_success() -> None:
    """
    Test that _configure_transformers_logging sets verbosity without error.
    """
    with patch("transformers.logging.set_verbosity_error") as mock_set:
        service._configure_transformers_logging()
        mock_set.assert_called_once()


def test_configure_transformers_logging_import_error() -> None:
    """
    Test that _configure_transformers_logging handles ImportError gracefully.
    """
    with patch(
        "transformers.logging.set_verbosity_error", side_effect=ImportError("test")
    ):
        service._configure_transformers_logging()  # Should not raise


def test_analyze_image_with_question() -> None:
    """
    Test analyze_image with question parameter.
    """
    image = Image.new("RGB", (10, 10))
    with (
        patch("pix_tell.service._validate_image_path", return_value=False),
        patch("pix_tell.service._load_image", return_value=image),
        patch("pix_tell.service._perform_vqa", return_value="Test answer"),
        patch("pix_tell.service._configure_transformers_logging"),
    ):
        result = service.analyze_image("test.jpg", question="What is this?")
        assert result == "Test answer"


def test_analyze_image_without_question() -> None:
    """
    Test analyze_image without question parameter for captioning.
    """
    image = Image.new("RGB", (10, 10))
    with (
        patch("pix_tell.service._validate_image_path", return_value=False),
        patch("pix_tell.service._load_image", return_value=image),
        patch("pix_tell.service._perform_captioning", return_value="Test caption"),
        patch("pix_tell.service._configure_transformers_logging"),
    ):
        result = service.analyze_image("test.jpg")
        assert result == "Test caption"


def test_analyze_image_handles_generic_exception() -> None:
    """
    Test analyze_image handles generic exceptions and wraps them in ValueError.
    """
    with (
        patch(
            "pix_tell.service._validate_image_path",
            side_effect=RuntimeError("Generic error"),
        ),
        patch("pix_tell.service._configure_transformers_logging"),
    ):
        with pytest.raises(ValueError) as exc_info:
            service.analyze_image("test.jpg")
        assert "Image analysis exception" in str(exc_info.value)


def test_load_image_url_request_error() -> None:
    """
    Test _load_image handles request errors for URLs.
    """
    with patch("requests.get", side_effect=requests.RequestException("Network error")):
        with pytest.raises(requests.RequestException):
            service._load_image("http://example.com/image.jpg", is_url=True)


def test_load_image_url_invalid_response() -> None:
    """
    Test _load_image handles invalid response for URLs.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    with patch("requests.get", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            service._load_image("http://example.com/image.jpg", is_url=True)


def test_load_image_local_file_not_found() -> None:
    """
    Test _load_image handles FileNotFoundError for local files.
    """
    with patch("PIL.Image.open", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError):
            service._load_image("nonexistent.jpg", is_url=False)
