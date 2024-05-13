#!/usr/bin/env python3
from time import sleep
from random import randint
from concurrent.futures import ThreadPoolExecutor, as_completed


def add_one(number):
    print(number)
    sleep(randint(0,2))
    return number + 1


def main():
    with ThreadPoolExecutor(32) as executor:
        futures = [executor.submit(add_one, number) for number in range(10)]
        print(futures)
        for future in as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    main()
