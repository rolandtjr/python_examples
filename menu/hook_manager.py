"""hook_manager.py"""
from __future__ import annotations

import inspect
import logging
from typing import (Any, Awaitable, Callable, Dict, List, Optional, TypedDict,
                    Union, TYPE_CHECKING)

if TYPE_CHECKING:
    from action import BaseAction
    from option import Option


logger = logging.getLogger("menu")


class HookContext(TypedDict, total=False):
    name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    result: Any | None
    exception: Exception | None
    option: Option | None
    action: BaseAction | None


Hook = Union[Callable[[HookContext], None], Callable[[HookContext], Awaitable[None]]]


class HookManager:
    def __init__(self):
        self._hooks: Dict[str, List[Hook]] = {
            "before": [],
            "after": [],
            "on_error": [],
            "on_teardown": [],
        }

    def register(self, hook_type: str, hook: Hook):
        if hook_type not in self._hooks:
            raise ValueError(f"Unsupported hook type: {hook_type}")
        self._hooks[hook_type].append(hook)

    def clear(self, hook_type: Optional[str] = None):
        if hook_type:
            self._hooks[hook_type] = []
        else:
            for k in self._hooks:
                self._hooks[k] = []

    async def trigger(self, hook_type: str, context: HookContext):
        if hook_type not in self._hooks:
            raise ValueError(f"Unsupported hook type: {hook_type}")
        for hook in self._hooks[hook_type]:
            try:
                if inspect.iscoroutinefunction(hook):
                    await hook(context)
                else:
                    hook(context)
            except Exception as hook_error:
                name = context.get("name", "<unnamed>")
                logger.warning(f"⚠️ Hook '{hook.__name__}' raised an exception during '{hook_type}'"
                               f" for '{name}': {hook_error}")

                if hook_type == "on_error":
                    raise context.get("exception") from hook_error
