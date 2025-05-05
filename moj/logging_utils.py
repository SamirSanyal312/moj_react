# moj/logging_utils.py
import logging
import functools
from flask import current_app

def log_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_app.config.get("DEBUG_LOGGING", False):
            logging.debug(
                f"Entering {func.__module__}.{func.__name__} args={args}, kwargs={kwargs}"
            )
        result = func(*args, **kwargs)
        if current_app.config.get("DEBUG_LOGGING", False):
            logging.debug(
                f"Exiting {func.__module__}.{func.__name__} return={result}"
            )
        return result
    return wrapper
