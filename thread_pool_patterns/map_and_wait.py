#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
from random import randint
from time import sleep


def add_one(number):
    sleep(randint(0, 2))
    return number + 1


def add_one_print(number):
    sleep(randint(0, 2))
    print(number)
    return number + 1


def main():
    with ThreadPoolExecutor() as executor:
        for result in executor.map(add_one, [1, 2, 3, 4, 5]):
            print(result)
    print("All done!\n")

    with ThreadPoolExecutor() as executor:
        returned_generator = executor.map(add_one_print, [1, 2, 3, 4, 5])
    print("Results in order\n")
    for result in returned_generator:
        print(result)
    print("All done!")


if __name__ == "__main__":
    main()
