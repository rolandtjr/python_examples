import asyncio
import functools
import inspect
import logging
import random
import time
from logging_utils import setup_logging
from rich.console import Console

console = Console()
setup_logging()
logger = logging.getLogger("menu")

def retry(max_retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            retries, current_delay = 0, delay
            while retries <= max_retries:
                if logger:
                    logger.debug(f"Retrying {retries + 1}/{max_retries} for '{func.__name__}' after {current_delay}s due to '{exceptions}'.")
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if retries == max_retries:
                        if logger:
                            logger.exception(f"❌ Max retries reached for '{func.__name__}': {e}")
                        raise
                    if logger:
                        logger.warning(
                            f"🔄 Retry {retries + 1}/{max_retries} for '{func.__name__}' after {current_delay}s due to '{e}'."
                        )
                    await asyncio.sleep(current_delay)
                    retries += 1
                    current_delay *= backoff

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            retries, current_delay = 0, delay
            while retries <= max_retries:
                if logger:
                    logger.debug(f"Retrying {retries + 1}/{max_retries} for '{func.__name__}' after {current_delay}s due to '{exceptions}'.")
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

        return async_wrapper if is_coroutine else sync_wrapper
    return decorator

@retry(max_retries=10, delay=1, spinner_text="Trying risky thing...")
def might_fail():
    time.sleep(4)
    if random.random() < 0.6:
        raise ValueError("Simulated failure")
    return "🎉 Success!"

result = might_fail()
print(result)
