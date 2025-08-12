import logging
import os
from datetime import datetime

def setup_logger(name, log_level=logging.INFO, console_output=True):
    """
    Setup a logger with customizable configuration
    
    Args:
        name (str): Name of the logger (usually __name__)
        log_level: Logging level (default: logging.INFO)
        console_output (bool): Whether to output to console (default: True)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name, log_level=logging.INFO, console_output=True):
    """
    Get a configured logger instance
    
    Args:
        name (str): Name of the logger (usually __name__)
        log_level: Logging level (default: logging.INFO)
        console_output (bool): Whether to output to console (default: True)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name, log_level, console_output)

# Default logger configuration
def get_default_logger(name):
    """
    Get a logger with default configuration (INFO level, console output only)
    
    Args:
        name (str): Name of the logger (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return get_logger(
        name=name,
        log_level=logging.INFO,
        console_output=True
    )

# Utility function to change log level at runtime
def set_log_level(logger_name, level):
    """
    Change the log level of an existing logger
    
    Args:
        logger_name (str): Name of the logger to modify
        level: New logging level
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

# Example usage:
if __name__ == "__main__":
    # Test the logger
    test_logger = get_default_logger("test")
    test_logger.info("Logger test successful!")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
