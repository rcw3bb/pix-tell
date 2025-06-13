"""
Unit tests for util module in pix_tell.

Author: Ron Webb
Since: 1.0.0
"""

import os
import logging
import configparser
import pytest

import pix_tell.util as util


def test_setup_logger_returns_logger() -> None:
    """
    Test that setup_logger returns a Logger instance.
    """
    logger = util.setup_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    logger.info("Logger setup test message.")


def test_load_model_config_returns_configparser() -> None:
    """
    Test that load_model_config returns a ConfigParser instance and loads config.ini.
    """
    config = util.load_model_config()
    assert isinstance(config, configparser.ConfigParser)
    assert config.has_section("models")
    assert config.has_option("models", "vqa_model_id")
    assert config.has_option("models", "caption_model_id")
