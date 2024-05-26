#!/usr/bin/env python3
import timeit
from functools import partial
from time import sleep
from typing import List
from random import randint
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, Future

from prompt_toolkit.shortcuts import ProgressBar
from pydantic import BaseModel

results: List[int] = []


class Result(BaseModel):
    result: int

    def __repr__(self) -> str:
        return f"Result: {self.result} {id(self)}"


class Requests:
    requests: Dict[str, Result] = {}
    odd_requests: Dict[str, Result] = {}
    even_requests: Dict[str, Result] = {}

    def __repr__(self) -> str:
        return f"Requests: {self.requests}\nOdd requests: {self.odd_requests}\nEven requests: {self.even_requests}"


def add_one(number: int) -> int:
    sleep(randint(0, 2))
    result = number + 1
    return result


def aggregate_results(future: Future):
    results.append(future.result())


def first_method():
    with ProgressBar() as pb:
        with ThreadPoolExecutor(32) as executor:
            futures = [executor.submit(add_one, number) for number in range(10)]
            for future in pb(futures, label="Processing tasks..."):
                future.add_done_callback(aggregate_results)


def second_method():
    futures = []
    with ThreadPoolExecutor(32) as executor:
        for number in range(10):
            futures.append(executor.submit(add_one, number))
            futures[-1].add_done_callback(aggregate_results)


def add_one_result(result: Result) -> Result:
    result.result += 1
    return result


def add_one_fut(future: Future):
    result = future.result()
    if result.result % 2 == 0:
        Requests.even_requests[str(result.result)] = result
    else:
        Requests.odd_requests[str(result.result)] = result


def third_method():
    for number in range(10):
        result = Result(result=randint(0, 100))
        Requests.requests[str(number)] = result
        if result.result % 2 == 0:
            Requests.even_requests[str(result.result)] = result
        else:
            Requests.odd_requests[str(result.result)] = result

    futures = []
    with ThreadPoolExecutor(32) as executor:
        for _, request in Requests.requests.items():
            future = executor.submit(add_one_result, request)
            future.add_done_callback(add_one_fut)
            futures.append(future)

    print("Done waiting!")
    print(Requests.requests)
    print("odd:", Requests.odd_requests)
    print("even:", Requests.even_requests)
    print("All done!")


def main():
    print(timeit.timeit(first_method, number=1))
    print(results)
    print("All done!\n")
    results.clear()
    print(timeit.timeit(second_method, number=1))
    print(results)
    print("All done!")

    third_method()


if __name__ == "__main__":
    main()
