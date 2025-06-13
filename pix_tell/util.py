"""
Logger utility module for pix_tell.

Author: Ron Webb
Since: 1.0.0
"""

import logging
import logging.config
import os
import configparser


def load_model_config() -> configparser.ConfigParser:
    """
    Load and return the configparser object for config.ini.

    Returns:
        ConfigParser object with loaded config.ini
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger configured using logging.ini.

    Args:
        name: The name of the logger.
    Returns:
        Configured logger instance.
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "logging.ini"
    )
    logging.config.fileConfig(config_path, disable_existing_loggers=False)
    return logging.getLogger(name)
