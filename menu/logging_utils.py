import logging
from rich.logging import RichHandler

def setup_logging(
    log_filename: str = "menu.log",
    console_log_level: int = logging.DEBUG,
    file_log_level: int = logging.DEBUG,
):
    """Set up logging configuration with separate console and file handlers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    console_handler = RichHandler(
        rich_tracebacks=True,
        show_time=True,
        show_level=True,
        show_path=False,
        markup=True,
        log_time_format="[%Y-%m-%d %H:%M:%S]",
    )
    console_handler.setLevel(console_log_level)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(file_log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    menu_logger = logging.getLogger("menu")
    menu_logger.setLevel(console_log_level)

    menu_logger.propagate = True
