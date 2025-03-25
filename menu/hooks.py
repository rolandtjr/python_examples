import time
import logging
import random
import functools
from menu import Menu, Option

logger = logging.getLogger("menu")

def timing_before_hook(option: Option) -> None:
    option._start_time = time.perf_counter()


def timing_after_hook(option: Option) -> None:
    option._end_time = time.perf_counter()
    option._duration = option._end_time - option._start_time


def timing_error_hook(option: Option, _: Exception) -> None:
    option._end_time = time.perf_counter()
    option._duration = option._end_time - option._start_time


def log_before(option: Option) -> None:
    logger.info(f"🚀 Starting action '{option.description}' (key='{option.key}')")


def log_after(option: Option) -> None:
    if option._duration is not None:
        logger.info(f"✅ Completed '{option.description}' (key='{option.key}') in {option._duration:.2f}s")
    else:
        logger.info(f"✅ Completed '{option.description}' (key='{option.key}')")


def log_error(option: Option, error: Exception) -> None:
    if option._duration is not None:
        logger.error(f"❌ Error '{option.description}' (key='{option.key}') after {option._duration:.2f}s: {error}")
    else:
        logger.error(f"❌ Error '{option.description}' (key='{option.key}'): {error}")


class CircuitBreakerOpen(Exception):
    """Exception raised when the circuit breaker is open."""


class CircuitBreaker:
    def __init__(self, max_failures=3, reset_timeout=10):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.open_until = None

    def before_hook(self, option: Option):
        if self.open_until:
            if time.time() < self.open_until:
                raise CircuitBreakerOpen(f"🔴 Circuit open for '{option.description}' until {time.ctime(self.open_until)}.")
            else:
                logger.info(f"🟢 Circuit closed again for '{option.description}'.")
                self.failures = 0
                self.open_until = None

    def error_hook(self, option: Option, error: Exception):
        self.failures += 1
        logger.warning(f"⚠️ CircuitBreaker: '{option.description}' failure {self.failures}/{self.max_failures}.")
        if self.failures >= self.max_failures:
            self.open_until = time.time() + self.reset_timeout
            logger.error(f"🔴 Circuit opened for '{option.description}' until {time.ctime(self.open_until)}.")

    def after_hook(self, option: Option):
        self.failures = 0

    def is_open(self):
        return self.open_until is not None and time.time() < self.open_until

    def reset(self):
        self.failures = 0
        self.open_until = None
        logger.info("🔄 Circuit reset.")


class RetryHandler:
    def __init__(self, max_retries=2, delay=1, backoff=2):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff

    def retry_on_error(self, option: Option, error: Exception):
        retries_done = 0
        current_delay = self.delay
        last_error = error

        while retries_done < self.max_retries:
            try:
                retries_done += 1
                logger.info(f"🔄 Retrying '{option.description}' ({retries_done}/{self.max_retries}) in {current_delay}s due to '{error}'...")
                time.sleep(current_delay)
                result = option.action()
                print(result)
                option.set_result(result)
                logger.info(f"✅ Retry succeeded for '{option.description}' on attempt {retries_done}.")
                option.after_action.run_hooks(option)
                return
            except Exception as retry_error:
                logger.warning(f"⚠️ Retry attempt {retries_done} for '{option.description}' failed due to '{retry_error}'.")
                last_error = retry_error
                current_delay *= self.backoff

        logger.exception(f"❌ '{option.description}' failed after {self.max_retries} retries.")
        raise last_error


def retry(max_retries=3, delay=1, backoff=2, exceptions=(Exception,), logger=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries, current_delay = 0, delay
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if retries == max_retries:
                        if logger:
                            logger.exception(f"❌ Max retries reached for '{func.__name__}': {e}")
                        raise
                    if logger:
                        logger.warning(
                            f"🔄 Retry {retries + 1}/{max_retries} for '{func.__name__}' after {current_delay}s due to '{e}'."
                        )
                    time.sleep(current_delay)
                    retries += 1
                    current_delay *= backoff
        return wrapper
    return decorator


def setup_hooks(menu):
    menu.add_before(timing_before_hook)
    menu.add_after(timing_after_hook)
    menu.add_on_error(timing_error_hook)
    menu.add_before(log_before)
    menu.add_after(log_after)
    menu.add_on_error(log_error)


if __name__ == "__main__":
    def risky_task():
        if random.random() > 0.1:
            time.sleep(1)
            raise ValueError("Random failure occurred")
        print("Task succeeded!")
    breaker = CircuitBreaker(max_failures=2, reset_timeout=10)
    retry_handler = RetryHandler(max_retries=30, delay=2, backoff=2)

    menu = Menu(never_confirm=True)
    menu.add_before(timing_before_hook)
    menu.add_after(timing_after_hook)
    menu.add_on_error(timing_error_hook)
    menu.add_before(log_before)
    menu.add_after(log_after)
    menu.add_on_error(log_error)
    menu.add_option(
        key="CR",
        description="Retry with CircuitBreaker",
        action=risky_task,
        before_hooks=[breaker.before_hook],
        after_hooks=[breaker.after_hook],
        error_hooks=[retry_handler.retry_on_error, breaker.error_hook],
    )
    menu.run()
