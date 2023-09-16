#!/usr/bin/env python3
"""thread_pool.py
----------------
This module demonstrates the use of asyncio to handle asynchronous and blocking
functions in Python. The module contains three functions: a blocking function
that simulates a long-running process with `time.sleep`, an asynchronous
function that demonstrates asyncio's sleep, and a main function that runs
both the blocking and async functions concurrently using a ThreadPoolExecutor 
for the blocking function.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import time


def blocking_function():
    time.sleep(2)
    return "Blocking function completed!"


async def async_function():
    print("Async function started!")
    await asyncio.sleep(1)
    print("Async function completed!")


async def main():
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()

    async_task = asyncio.create_task(async_function())

    result = await loop.run_in_executor(executor, blocking_function)
    print(result)

    await async_task


if __name__ == "__main__":
    asyncio.run(main())
