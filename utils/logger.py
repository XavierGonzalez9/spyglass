import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Tuple

def setup_logging(log_dir: str = "Reports") -> Tuple:
    """
    Setup centralized logging configuration for the application.
    
    Args:
        log_dir: Directory to store log files (default: "Reports")
    
    Returns:
        Tuple of (app_logger, keystroke_logger, log_file, keystroke_log_file)
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    log_file = os.path.join(log_dir, f'spyglass_{timestamp}.log')
    keystroke_log_file = os.path.join(log_dir, f'keystrokes_{timestamp}.log')
    
    # Setup app logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.DEBUG)
    app_logger.handlers.clear()
    
    # Setup keystroke logger
    keystroke_logger = logging.getLogger('keystrokes')
    keystroke_logger.setLevel(logging.INFO)
    keystroke_logger.handlers.clear()
    
    # Formatter for all handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # ===== APP LOGGER HANDLERS =====
    # File handler for app logger
    app_file_handler = logging.FileHandler(log_file, encoding='utf-8')
    app_file_handler.setFormatter(formatter)
    app_logger.addHandler(app_file_handler)
    
    # Console handler for app logger
    app_console_handler = logging.StreamHandler()
    app_console_handler.setFormatter(formatter)
    app_logger.addHandler(app_console_handler)
    
    # ===== KEYSTROKE LOGGER HANDLERS =====
    # File handler for keystroke logger
    keystroke_file_handler = logging.FileHandler(keystroke_log_file, encoding='utf-8')
    keystroke_file_handler.setFormatter(formatter)
    keystroke_logger.addHandler(keystroke_file_handler)
    
    # ===== ROOT LOGGER CONFIGURATION =====
    logging.root.handlers = []
    logging.root.addHandler(app_file_handler)
    logging.root.addHandler(app_console_handler)
    logging.root.setLevel(logging.DEBUG)
    
    return app_logger, keystroke_logger, log_file, keystroke_log_file

def get_app_logger() -> logging.Logger:
    """Get the application logger instance."""
    return logging.getLogger('app')

def get_keystroke_logger() -> logging.Logger:
    """Get the keystroke logger instance."""
    return logging.getLogger('keystrokes')