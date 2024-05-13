#!/usr/bin/env python3
import timeit
from time import sleep
from random import randint
from concurrent.futures import ThreadPoolExecutor, Future

results: list[int] = []


def add_one(number: int) -> int:
    sleep(randint(0, 2))
    result = number + 1
    return result


def aggregate_results(future: Future):
    results.append(future.result())


def first_method():
    with ThreadPoolExecutor(32) as executor:
        futures = [executor.submit(add_one, number) for number in range(10)]
        for future in futures:
            future.add_done_callback(aggregate_results)


def second_method():
    futures = []
    with ThreadPoolExecutor(32) as executor:
        for number in range(10):
            futures.append(executor.submit(add_one, number))
            futures[-1].add_done_callback(aggregate_results)


def main():
    print(timeit.timeit(first_method, number=1))
    print(results)
    print("All done!\n")
    results.clear()
    print(timeit.timeit(second_method, number=1))
    print(results)
    print("All done!")


if __name__ == "__main__":
    main()
