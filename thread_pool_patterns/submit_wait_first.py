#!/usr/bin/env python3
from time import sleep
from random import randint
from concurrent.futures import ThreadPoolExecutor, Future, wait, FIRST_COMPLETED

results: list[int] = []

def add_one(number: int) -> int:
    sleep(randint(0,2))
    return number + 1


def main() -> None:
    executor = ThreadPoolExecutor(32)
    futures: list[Future] = [executor.submit(add_one, number) for number in range(10)]
    done, not_done = wait(futures, return_when=FIRST_COMPLETED)
    executor.shutdown(wait=False, cancel_futures=True)
    print(done.pop().result())


if __name__ == "__main__":
    main()
