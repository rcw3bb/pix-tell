"""
Service module for image analysis in pix_tell.

This module provides the analyze_image function for analyzing and describing images.

Author: Ron Webb
Since: 1.0.0
"""

import io
import os
import re
from typing import Optional

import requests
import transformers
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor, pipeline

from .util import setup_logger, load_model_config


logger = setup_logger(__name__)

_config = load_model_config()
_VQA_MODEL_ID = _config.get(
    "models", "vqa_model_id", fallback="Salesforce/blip-vqa-base"
)
_CAPTION_MODEL_ID = _config.get(
    "models", "caption_model_id", fallback="Salesforce/blip-image-captioning-large"
)


def _configure_transformers_logging() -> None:
    """Configure transformers logging to reduce verbosity."""
    try:
        transformers.logging.set_verbosity_error()
    except ImportError as import_error:
        logger.warning("transformers logging could not be set: %s", import_error)


def _validate_image_path(image_path: str) -> bool:
    """
    Validate image path and check if it's a URL or local file.

    Args:
        image_path: Path to the image file to validate

    Returns:
        True if the path is a URL, False if it's a local file

    Raises:
        ValueError: If the image path is empty
        FileNotFoundError: If the local image file doesn't exist
    """
    if not image_path:
        logger.error("Image path cannot be empty")
        raise ValueError("Image path cannot be empty")

    url_pattern = re.compile(r"^https?://", re.IGNORECASE)
    is_url = bool(url_pattern.match(image_path))

    if not is_url and not os.path.isfile(image_path):
        logger.error("Image file not found: %s", image_path)
        raise FileNotFoundError(f"Image file not found: {image_path}")

    return is_url


def _load_image(image_path: str, is_url: bool) -> Image.Image:
    """
    Load an image from a URL or local file.

    Args:
        image_path: Path to the image file
        is_url: True if the path is a URL, False if it's a local file

    Returns:
        PIL Image object

    Raises:
        requests.RequestException: If URL cannot be accessed
        IOError: If image cannot be opened
    """
    if is_url:
        response = requests.get(image_path, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    return Image.open(image_path)


def _perform_vqa(image: Image.Image, question: str) -> str:
    """
    Perform visual question answering on an image.

    Args:
        image: PIL Image object
        question: Question to ask about the image

    Returns:
        Answer to the question

    Raises:
        ValueError: If the VQA model returns unexpected response
    """
    vqa = pipeline(
        "visual-question-answering",
        model=_VQA_MODEL_ID,
        tokenizer=_VQA_MODEL_ID,
        image_processor=BlipProcessor.from_pretrained(_VQA_MODEL_ID, use_fast=True),
    )
    result = vqa(image, question=question)

    if isinstance(result, list) and result and "answer" in result[0]:
        answer = result[0]["answer"]
        logger.info("VQA result: %s", answer)
        return answer

    raise ValueError(f"Model: {_VQA_MODEL_ID} - Unexpected VQA response: {result}")


def _perform_captioning(image: Image.Image) -> str:
    """
    Generate a caption for an image.

    Args:
        image: PIL Image object

    Returns:
        Generated caption

    Raises:
        ValueError: If the captioning model returns unexpected response
    """
    processor = BlipProcessor.from_pretrained(_CAPTION_MODEL_ID, use_fast=True)
    model = BlipForConditionalGeneration.from_pretrained(_CAPTION_MODEL_ID)

    captioner = pipeline(
        "image-to-text",
        model=model,
        tokenizer=_CAPTION_MODEL_ID,
        image_processor=processor,
    )
    result = captioner(image, max_new_tokens=50)

    if isinstance(result, list) and result and "generated_text" in result[0]:
        caption = result[0]["generated_text"]
        logger.info("Caption result: %s", caption)
        return caption

    raise ValueError(
        f"Model: {_CAPTION_MODEL_ID} - Unexpected captioning response: {result}"
    )


def analyze_image(image_path: str, question: Optional[str] = None) -> str:
    """
    Analyze an image and return a description or answer a question using the Hugging Face BLIP model.

    Args:
        image_path: Path to the image file to analyze
        question: Optional question to ask about the image

    Returns:
        A string description or answer about the image

    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the image format is not supported or model fails
    """
    _configure_transformers_logging()

    try:
        is_url = _validate_image_path(image_path)
        image = _load_image(image_path, is_url)

        if question:
            return _perform_vqa(image, question)
        return _perform_captioning(image)

    except (FileNotFoundError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Image analysis exception: %r", exc)
        raise ValueError(f"Image analysis exception: {repr(exc)}") from exc
