import random
import time


def risky_task() -> str:
    if random.random() > 0.25:
        time.sleep(1)
        raise ValueError("Random failure occurred")
    return "Task succeeded!"
