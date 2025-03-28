"""action.py

Any Action or Option is callable and supports the signature:
    result = thing(*args, **kwargs)

This guarantees:
- Hook lifecycle (before/after/error/teardown)
- Timing
- Consistent return values
"""
from __future__ import annotations

import asyncio
import logging
import time
import inspect
from abc import ABC, abstractmethod
from typing import Optional

from hook_manager import HookManager
from menu_utils import TimingMixin, run_async


logger = logging.getLogger("menu")


class BaseAction(ABC, TimingMixin):
    """Base class for actions. They are the building blocks of the menu.
    Actions can be simple functions or more complex actions like
    `ChainedAction` or `ActionGroup`. They can also be run independently
    or as part of a menu."""
    def __init__(self, name: str, hooks: Optional[HookManager] = None):
        self.name = name
        self.hooks = hooks or HookManager()
        self.start_time: float | None = None
        self.end_time: float | None = None
        self._duration: float | None = None

    def __call__(self, *args, **kwargs):
        context = {
            "name": self.name,
            "duration": None,
            "args": args,
            "kwargs": kwargs,
            "action": self
        }
        self._start_timer()
        try:
            run_async(self.hooks.trigger("before", context))
            result = self._run(*args, **kwargs)
            context["result"] = result
            return result
        except Exception as error:
            context["exception"] = error
            run_async(self.hooks.trigger("on_error", context))
            if "exception" not in context:
                logger.info(f"✅ Recovery hook handled error for Action '{self.name}'")
                return context.get("result")
            raise
        finally:
            self._stop_timer()
            context["duration"] = self.get_duration()
            if "exception" not in context:
                run_async(self.hooks.trigger("after", context))
            run_async(self.hooks.trigger("on_teardown", context))

    @abstractmethod
    def _run(self, *args, **kwargs):
        raise NotImplementedError("_run must be implemented by subclasses")

    async def run_async(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self._run):
            return await self._run(*args, **kwargs)

        return await asyncio.to_thread(self.__call__, *args, **kwargs)

    def __await__(self):
        return self.run_async().__await__()

    @abstractmethod
    def dry_run(self):
        raise NotImplementedError("dry_run must be implemented by subclasses")

    def __str__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"

    def __repr__(self):
        return str(self)


class Action(BaseAction):
    def __init__(self, name: str, fn, rollback=None, hooks=None):
        super().__init__(name, hooks)
        self.fn = fn
        self.rollback = rollback

    def _run(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self.fn):
            return asyncio.run(self.fn(*args, **kwargs))
        return self.fn(*args, **kwargs)

    def dry_run(self):
        print(f"[DRY RUN] Would run: {self.name}")


class ChainedAction(BaseAction):
    def __init__(self, name: str, actions: list[BaseAction], hooks=None):
        super().__init__(name, hooks)
        self.actions = actions

    def _run(self, *args, **kwargs):
        rollback_stack = []
        for action in self.actions:
            try:
                result = action(*args, **kwargs)
                rollback_stack.append(action)
            except Exception:
                self._rollback(rollback_stack, *args, **kwargs)
                raise
        return None

    def dry_run(self):
        print(f"[DRY RUN] ChainedAction '{self.name}' with steps:")
        for action in self.actions:
            action.dry_run()

    def _rollback(self, rollback_stack, *args, **kwargs):
        for action in reversed(rollback_stack):
            if hasattr(action, "rollback") and action.rollback:
                try:
                    print(f"↩️ Rolling back {action.name}")
                    action.rollback(*args, **kwargs)
                except Exception as e:
                    print(f"⚠️ Rollback failed for {action.name}: {e}")


class ActionGroup(BaseAction):
    def __init__(self, name: str, actions: list[BaseAction], hooks=None):
        super().__init__(name, hooks)
        self.actions = actions
        self.results = []
        self.errors = []

    def _run(self, *args, **kwargs):
        asyncio.run(self._run_async(*args, **kwargs))

    def dry_run(self):
        print(f"[DRY RUN] ActionGroup '{self.name}' (parallel execution):")
        for action in self.actions:
            action.dry_run()

    async def _run_async(self, *args, **kwargs):
        async def run(action):
            try:
                result = await asyncio.to_thread(action, *args, **kwargs)
                self.results.append((action.name, result))
            except Exception as e:
                self.errors.append((action.name, e))

        await self.hooks.trigger("before", name=self.name)

        await asyncio.gather(*[run(a) for a in self.actions])

        if self.errors:
            await self.hooks.trigger("on_error", name=self.name, errors=self.errors)
        else:
            await self.hooks.trigger("after", name=self.name, results=self.results)

        await self.hooks.trigger("on_teardown", name=self.name)



# if __name__ == "__main__":
#     # Example usage
#     def build(): print("Build!")
#     def test(): print("Test!")
#     def deploy(): print("Deploy!")


#     pipeline = ChainedAction("CI/CD", [
#         Action("Build", build),
#         Action("Test", test),
#         ActionGroup("Deploy Parallel", [
#             Action("Deploy A", deploy),
#             Action("Deploy B", deploy)
#         ])
#     ])

#     pipeline()
# Sample functions
def sync_hello():
    time.sleep(1)
    return "Hello from sync function"

async def async_hello():
    await asyncio.sleep(1)
    return "Hello from async function"


# Example usage
async def main():
    sync_action = Action("sync_hello", sync_hello)
    async_action = Action("async_hello", async_hello)

    print("⏳ Awaiting sync action...")
    result1 = await sync_action
    print("✅", result1)

    print("⏳ Awaiting async action...")
    result2 = await async_action
    print("✅", result2)

    print(f"⏱️ sync took {sync_action.get_duration():.2f}s")
    print(f"⏱️ async took {async_action.get_duration():.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
