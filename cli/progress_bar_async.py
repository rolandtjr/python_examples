#!/usr/bin/env python
""" progress_bar.py
This module demonstrates how to use the prompt_toolkit ProgressBar to display
the progress of a list of tasks. The progress bar is only updated when tasks
are done not when started.

Tasks use asyncio for concurrency.
"""
import asyncio
import os
import signal
from random import randint
from threading import Lock

import aiohttp
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import ProgressBar

from in_put import confirm_async as confirm
from in_put import custom_formatters, get_toolbar, style


class Forge:
    """ Forge class
    This class demonstrates how to use the prompt_toolkit ProgressBar to display
    the progress of a list of tasks. The progress bar is only updated when tasks
    are done not when started.
    """
    kb = KeyBindings()
    cancel = False
    def __init__(self):
        self.lock = Lock()
        self.tasks_done = 0
        self.fast_tasks_done = 0
        self.slow_tasks_done = 0
        self.fast_task_count = randint(50, 400)
        self.slow_task_count = randint(50, 100)
        self.total_tasks = self.fast_task_count + self.slow_task_count

    @kb.add("q")
    def _(event):
        cancel = True

    @kb.add("f")
    def _(event):
        print("f")

    @kb.add("x")
    def _(event):
        os.kill(os.getpid(), signal.SIGINT)

    async def save_data(self, data):
        with open("data.txt", "a") as file:
            file.write(f"{data}\n")
        await asyncio.sleep(randint(5, 15))
        self.slow_tasks_done += 1

    async def send_data(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:5597/fast", data=data) as result:
                if await result.text() == "Data saved!":
                    self.fast_tasks_done += 1

    async def fast_task(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5597/fast") as result:
                return await self.send_data(await result.text())

    async def slow_task(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5597/slow") as result:
                return await self.save_data(await result.text())

    async def run(self):
        """ Keeps track of the progress of a list of tasks using a seperate progress bar
        for each task. The progress bar is only update when tasks are done not when started.
        """
        slow_tasks = []
        fast_tasks = []

        # Print number of fast, slow, and total tasks
        print(f"Fast tasks: {self.fast_task_count}")
        print(f"Slow tasks: {self.slow_task_count}")
        print(f"Total tasks: {self.total_tasks}")
        with patch_stdout():
            with ProgressBar(
                title="Forge",
                formatters=custom_formatters,
                style=style,
                bottom_toolbar=get_toolbar,
                key_bindings=self.kb,
            ) as pb:
                task_progress = pb(range(self.total_tasks), label="Tasks")
                slow_progress = pb(range(self.slow_task_count), label="Slow tasks")
                for _ in range(self.slow_task_count):
                    slow_tasks.append(asyncio.create_task(self.slow_task()))

                fast_progress = pb(range(self.fast_task_count), label="Fast tasks")
                for _ in range(self.fast_task_count):
                    fast_tasks.append(asyncio.create_task(self.fast_task()))

                while not (fast_progress.done and slow_progress.done):
                    await asyncio.sleep(0.1)
                    slow_progress.items_completed = self.slow_tasks_done
                    fast_progress.items_completed = self.fast_tasks_done
                    task_progress.items_completed = self.slow_tasks_done + self.fast_tasks_done
                    if self.fast_tasks_done == self.fast_task_count:
                        fast_progress.done = True
                    if self.slow_tasks_done == self.slow_task_count:
                        slow_progress.done = True

        result = await confirm("Do you want to print the data?")

        if result:
            with open("data.txt", "r") as file:
                print(file.read())


def main():
    forge = Forge()
    asyncio.run(forge.run())


if __name__ == "__main__":
    main()
