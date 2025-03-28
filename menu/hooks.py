import functools
import logging
import random
import time

from hook_manager import HookContext
from menu_utils import run_async

logger = logging.getLogger("menu")


def log_before(context: dict) -> None:
    name = context.get("name", "<unnamed>")
    option = context.get("option")
    if option:
        logger.info(f"🚀 Starting action '{option.description}' (key='{option.key}')")
    else:
        logger.info(f"🚀 Starting action '{name}'")


def log_after(context: dict) -> None:
    name = context.get("name", "<unnamed>")
    duration = context.get("duration")
    if duration is not None:
        logger.info(f"✅ Completed '{name}' in {duration:.2f}s")
    else:
        logger.info(f"✅ Completed '{name}'")


def log_error(context: dict) -> None:
    name = context.get("name", "<unnamed>")
    error = context.get("exception")
    duration = context.get("duration")
    if duration is not None:
        logger.error(f"❌ Error '{name}' after {duration:.2f}s: {error}")
    else:
        logger.error(f"❌ Error '{name}': {error}")


class CircuitBreakerOpen(Exception):
    """Exception raised when the circuit breaker is open."""


class CircuitBreaker:
    def __init__(self, max_failures=3, reset_timeout=10):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.open_until = None

    def before_hook(self, context: HookContext):
        name = context.get("name", "<unnamed>")
        if self.open_until:
            if time.time() < self.open_until:
                raise CircuitBreakerOpen(f"🔴 Circuit open for '{name}' until {time.ctime(self.open_until)}.")
            else:
                logger.info(f"🟢 Circuit closed again for '{name}'.")
                self.failures = 0
                self.open_until = None

    def error_hook(self, context: HookContext):
        name = context.get("name", "<unnamed>")
        self.failures += 1
        logger.warning(f"⚠️ CircuitBreaker: '{name}' failure {self.failures}/{self.max_failures}.")
        if self.failures >= self.max_failures:
            self.open_until = time.time() + self.reset_timeout
            logger.error(f"🔴 Circuit opened for '{name}' until {time.ctime(self.open_until)}.")

    def after_hook(self, context: HookContext):
        self.failures = 0

    def is_open(self):
        return self.open_until is not None and time.time() < self.open_until

    def reset(self):
        self.failures = 0
        self.open_until = None
        logger.info("🔄 Circuit reset.")


class RetryHandler:
    def __init__(self, max_retries=5, delay=1, backoff=2):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff

    def retry_on_error(self, context: HookContext):
        name = context.get("name", "<unnamed>")
        error = context.get("exception")
        option = context.get("option")
        action = context.get("action")

        retries_done = 0
        current_delay = self.delay
        last_error = error

        if not (option or action):
            logger.warning(f"⚠️ RetryHandler: No Option or Action in context for '{name}'. Skipping retry.")
            return

        target = option or action

        while retries_done < self.max_retries:
            try:
                retries_done += 1
                logger.info(f"🔄 Retrying '{name}' ({retries_done}/{self.max_retries}) in {current_delay}s due to '{last_error}'...")
                time.sleep(current_delay)
                result = target(*context.get("args", ()), **context.get("kwargs", {}))
                if option:
                    option.set_result(result)

                context["result"] = result
                context["duration"] = target.get_duration() or 0.0
                context.pop("exception", None)

                logger.info(f"✅ Retry succeeded for '{name}' on attempt {retries_done}.")

                if hasattr(target, "hooks"):
                    run_async(target.hooks.trigger("after", context))

                return
            except Exception as retry_error:
                logger.warning(f"⚠️ Retry attempt {retries_done} for '{name}' failed due to '{retry_error}'.")
                last_error = retry_error
                current_delay *= self.backoff

        logger.exception(f"❌ '{name}' failed after {self.max_retries} retries.")
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
    menu.add_before(log_before)
    menu.add_after(log_after)
    menu.add_on_error(log_error)


if __name__ == "__main__":
    from menu import Menu
    def risky_task():
        if random.random() > 0.1:
            time.sleep(1)
            raise ValueError("Random failure occurred")
        print("Task succeeded!")
    breaker = CircuitBreaker(max_failures=2, reset_timeout=10)
    retry_handler = RetryHandler(max_retries=30, delay=2, backoff=2)

    menu = Menu(never_confirm=True)
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
