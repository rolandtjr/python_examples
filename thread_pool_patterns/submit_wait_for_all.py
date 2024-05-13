#!/usr/bin/env python3
from time import sleep
from random import randint
from concurrent.futures import ThreadPoolExecutor, wait, Future

results: list[int] = []


def add_one(number: int) -> int:
    print(number)
    sleep(randint(0, 2))
    return number + 1


def main() -> None:
    executor = ThreadPoolExecutor(32)
    futures: list[Future] = [executor.submit(add_one, number) for number in range(10)]
    wait(futures)
    print("Done waiting!")
    for future in futures:
        print(future.result())
    print("All done!")

    futures: list[Future] = [executor.submit(add_one, number) for number in range(10)]
    executor.shutdown()
    print("Done waiting!")
    for future in futures:
        print(future.result())
    print("All done!")

    with ThreadPoolExecutor() as executor:
        futures: list[Future] = [
            executor.submit(add_one, number) for number in range(10)
        ]
    print("Done waiting!")
    for future in futures:
        print(future.result())
    print("All done!")


if __name__ == "__main__":
    main()
