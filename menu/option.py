"""option.py
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
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from action import BaseAction
from colors import OneColors
from hook_manager import HookManager
from menu_utils import TimingMixin, run_async

logger = logging.getLogger("menu")


class Option(BaseModel, TimingMixin):
    """Class representing an option in the menu.

    Hooks must have the signature:
        def hook(option: Option) -> None:
    where `option` is the selected option.

    Error hooks must have the signature:
        def error_hook(option: Option, error: Exception) -> None:
    where `option` is the selected option and `error` is the exception raised.
    """
    key: str
    description: str
    action: BaseAction | Callable[[], Any] = lambda: None
    color: str = OneColors.WHITE
    confirm: bool = False
    confirm_message: str = "Are you sure?"
    spinner: bool = False
    spinner_message: str = "Processing..."
    spinner_type: str = "dots"
    spinner_style: str = OneColors.CYAN
    spinner_kwargs: dict[str, Any] = Field(default_factory=dict)

    hooks: "HookManager" = Field(default_factory=HookManager)

    start_time: float | None = None
    end_time: float | None = None
    _duration: float | None = PrivateAttr(default=None)
    _result: Any | None = PrivateAttr(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __str__(self):
        return f"Option(key='{self.key}', description='{self.description}')"

    def set_result(self, result: Any) -> None:
        """Set the result of the action."""
        self._result = result

    def get_result(self) -> Any:
        """Get the result of the action."""
        return self._result

    def __call__(self, *args, **kwargs) -> Any:
        context = {
            "name": self.description,
            "duration": None,
            "args": args,
            "kwargs": kwargs,
            "option": self,
        }
        self._start_timer()
        try:
            run_async(self.hooks.trigger("before", context))
            result = self._execute_action(*args, **kwargs)
            self.set_result(result)
            context["result"] = result
            return result
        except Exception as error:
            context["exception"] = error
            run_async(self.hooks.trigger("on_error", context))
            if "exception" not in context:
                logger.info(f"✅ Recovery hook handled error for Option '{self.key}'")
                return self.get_result()
            raise
        finally:
            self._stop_timer()
            context["duration"] = self.get_duration()
            if "exception" not in context:
                run_async(self.hooks.trigger("after", context))
            run_async(self.hooks.trigger("on_teardown", context))

    def _execute_action(self, *args, **kwargs) -> Any:
        if isinstance(self.action, BaseAction):
            return self.action(*args, **kwargs)
        return self.action()

    def dry_run(self):
        print(f"[DRY RUN] Option '{self.key}' would run: {self.description}")
        if isinstance(self.action, BaseAction):
            self.action.dry_run()
        elif callable(self.action):
            print(f"[DRY RUN] Action is a raw callable: {self.action.__name__}")
        else:
            print("[DRY RUN] Action is not callable.")