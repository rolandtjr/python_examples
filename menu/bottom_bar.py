from prompt_toolkit.formatted_text import HTML, merge_formatted_text
from typing import Callable, Literal, Optional
from rich.console import Console


class BottomBar:
    def __init__(self, columns: int = 3):
        self.columns = columns
        self.console = Console()
        self._items: list[Callable[[], HTML]] = []
        self._named_items: dict[str, Callable[[], HTML]] = {}
        self._states: dict[str, any] = {}

    def get_space(self) -> str:
        return self.console.width // self.columns

    def add_static(self, name: str, text: str) -> None:
        def render():
            return HTML(f"<style fg='#D8DEE9'>{text:^{self.get_space()}}</style>")
        self._add_named(name, render)

    def add_counter(self, name: str, label: str, current: int, total: int) -> None:
        self._states[name] = (label, current, total)

        def render():
            l, c, t = self._states[name]
            text = f"{l}: {c}/{t}"
            return HTML(f"<style fg='#A3BE8C'>{text:^{self.get_space()}}</style>")

        self._add_named(name, render)

    def add_toggle(self, name: str, label: str, state: bool) -> None:
        self._states[name] = (label, state)

        def render():
            l, s = self._states[name]
            color = '#A3BE8C' if s else '#BF616A'
            status = "ON" if s else "OFF"
            text = f"{l}: {status}"
            return HTML(f"<style fg='{color}'>{text:^{self.get_space()}}</style>")

        self._add_named(name, render)

    def update_toggle(self, name: str, state: bool) -> None:
        if name in self._states:
            label, _ = self._states[name]
            self._states[name] = (label, state)

    def update_counter(self, name: str, current: Optional[int] = None, total: Optional[int] = None) -> None:
        if name in self._states:
            label, c, t = self._states[name]
            self._states[name] = (label, current if current is not None else c, total if total is not None else t)

    def _add_named(self, name: str, render_fn: Callable[[], HTML]) -> None:
        self._named_items[name] = render_fn
        self._items = list(self._named_items.values())

    def render(self):
        return merge_formatted_text([fn() for fn in self._items])
