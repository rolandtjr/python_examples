import logging
from rich.traceback import install
from logging_utils import setup_logging
from menu import Menu
from hooks import setup_hooks, CircuitBreaker, RetryHandler
from task import risky_task

install(show_locals=True, width=120)
setup_logging()

logger = logging.getLogger("menu")

menu = Menu(title="Main Menu", never_confirm=True)
setup_hooks(menu)
breaker = CircuitBreaker(max_failures=2, reset_timeout=10)
retry_handler = RetryHandler(max_retries=30, delay=2, backoff=2)
menu.add_option(
    "1",
    "Run Risky Task",
    risky_task,
    before_hooks=[breaker.before_hook],
    after_hooks=[breaker.after_hook],
    error_hooks=[retry_handler.retry_on_error, breaker.error_hook],
)


if __name__ == "__main__":
    result = menu.run_headless("1")
    logger.info(f"Headless execution returned: {result}")
