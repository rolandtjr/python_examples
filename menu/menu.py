"""menu.py

This class creates a Menu object that creates a selectable menu
with customizable options and functionality.

It allows for adding options, and their accompanying actions,
and provides a method to display the menu and handle user input.

This class uses the `rich` library to display the menu in a
formatted and visually appealing way.

This class also uses the `prompt_toolkit` library to handle
user input and create an interactive experience.
"""

import logging
from functools import cached_property
from itertools import islice
from typing import Any, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator
from pydantic import BaseModel, Field, field_validator, PrivateAttr
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from colors import get_nord_theme
from one_colors import OneColors

logger = logging.getLogger("menu")


def chunks(iterator, size):
    """Yield successive n-sized chunks from an iterator."""
    iterator = iter(iterator)
    while True:
        chunk = list(islice(iterator, size))
        if not chunk:
            break
        yield chunk


class MenuError(Exception):
    """Custom exception for the Menu class."""


class OptionAlreadyExistsError(MenuError):
    """Exception raised when an option with the same key already exists in the menu."""


class InvalidHookError(MenuError):
    """Exception raised when a hook is not callable."""


class InvalidActionError(MenuError):
    """Exception raised when an action is not callable."""


class NotAMenuError(MenuError):
    """Exception raised when the provided submenu is not an instance of Menu."""


class CaseInsensitiveDict(dict):
    """A case-insensitive dictionary that treats all keys as uppercase."""

    def __setitem__(self, key, value):
        super().__setitem__(key.upper(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.upper())

    def __contains__(self, key):
        return super().__contains__(key.upper())

    def get(self, key, default=None):
        return super().get(key.upper(), default)

    def pop(self, key, default=None):
        return super().pop(key.upper(), default)

    def update(self, other=None, **kwargs):
        if other:
            other = {k.upper(): v for k, v in other.items()}
        kwargs = {k.upper(): v for k, v in kwargs.items()}
        super().update(other, **kwargs)


class Hooks(BaseModel):
    """Class to manage hooks for the menu and options."""

    hooks: list[Callable[["Option"], None]] | list[Callable[["Option", Exception], None]] = Field(
        default_factory=list
    )

    @field_validator("hooks", mode="before")
    @classmethod
    def validate_hooks(cls, hooks):
        if hooks is None:
            return []
        if not all(callable(hook) for hook in hooks):
            raise InvalidHookError("All hooks must be callable.")
        return hooks

    def add_hook(self, hook: Callable[["Option"], None] | Callable[["Option", Exception], None]) -> None:
        """Add a hook to the list."""
        if not callable(hook):
            raise InvalidHookError("Hook must be a callable.")
        if hook not in self.hooks:
            self.hooks.append(hook)

    def run_hooks(self, *args, **kwargs) -> None:
        """Run all hooks with the given arguments."""
        for hook in self.hooks:
            try:
                hook(*args, **kwargs)
            except Exception as hook_error:
                logger.exception(f"Hook '{hook.__name__}': {hook_error}")


class Option(BaseModel):
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
    action: Callable[[], Any] = lambda: None
    color: str = OneColors.WHITE
    confirm: bool = False
    confirm_message: str = "Are you sure?"
    spinner: bool = False
    spinner_message: str = "Processing..."
    spinner_type: str = "dots"
    spinner_style: str = OneColors.CYAN
    spinner_kwargs: dict[str, Any] = Field(default_factory=dict)

    before_action: Hooks = Field(default_factory=Hooks)
    after_action: Hooks = Field(default_factory=Hooks)
    on_error: Hooks = Field(default_factory=Hooks)

    _start_time: float | None = PrivateAttr(default=None)
    _end_time: float | None = PrivateAttr(default=None)
    _duration: float | None = PrivateAttr(default=None)

    _result: Any | None = PrivateAttr(default=None)

    def __str__(self):
        return f"Option(key='{self.key}', description='{self.description}')"

    def set_result(self, result: Any) -> None:
        """Set the result of the action."""
        self._result = result

    def get_result(self) -> Any:
        """Get the result of the action."""
        return self._result

    @field_validator("action")
    def validate_action(cls, action):
        if not callable(action):
            raise InvalidActionError("Action must be a callable.")
        return action


class Menu:
    """Class to create a menu with options.

    Hook functions must have the signature:
        def hook(option: Option) -> None:
    where `option` is the selected option.

    Error hook functions must have the signature:
        def error_hook(option: Option, error: Exception) -> None:
    where `option` is the selected option and `error` is the exception raised.

    Hook execution order:
    1. Before action hooks of the menu.
    2. Before action hooks of the selected option.
    3. Action of the selected option.
    4. After action hooks of the selected option.
    5. After action hooks of the menu.
    6. On error hooks of the selected option (if an error occurs).
    7. On error hooks of the menu (if an error occurs).

    Parameters:
        title (str|Markdown): The title of the menu.
        columns (int): The number of columns to display the options in.
        prompt (AnyFormattedText): The prompt to display when asking for input.
        bottom_bar (str|callable|None): The text to display in the bottom bar.
    """

    def __init__(
        self,
        title: str | Markdown = "Menu",
        prompt: str | AnyFormattedText = "> ",
        columns: int = 3,
        bottom_bar: str | Callable[[], None] | None = None,
        welcome_message: str | Markdown = "",
        exit_message: str | Markdown = "",
        run_hooks_on_back_option: bool = False,
        continue_on_error_prompt: bool = True,
        never_confirm: bool = False,
        _verbose: bool = False,
    ) -> None:
        """Initializes the Menu object."""
        self.title: str | Markdown = title
        self.prompt: str | AnyFormattedText = prompt
        self.columns: int = columns
        self.bottom_bar: str | Callable[[], None] | None = bottom_bar
        self.options: dict[str, Option] = CaseInsensitiveDict()
        self.back_option: Option = self._get_back_option()
        self.console: Console = Console(color_system="truecolor", theme=get_nord_theme())
        self.session: PromptSession = self._get_prompt_session()
        self.welcome_message: str | Markdown = welcome_message
        self.exit_message: str | Markdown = exit_message
        self.before_action: Hooks = Hooks()
        self.after_action: Hooks = Hooks()
        self.on_error: Hooks = Hooks()
        self.run_hooks_on_back_option: bool = run_hooks_on_back_option
        self.continue_on_error_prompt: bool = continue_on_error_prompt
        self._never_confirm: bool = never_confirm
        self._verbose: bool = _verbose
        self.last_run_option: Option | None = None

    def get_title(self) -> str:
        """Returns the string title of the menu."""
        if isinstance(self.title, str):
            return self.title
        elif isinstance(self.title, Markdown):
            return self.title.markup
        return self.title

    def _get_back_option(self) -> Option:
        """Returns the back option for the menu."""
        return Option(key="0", description="Back", color=OneColors.DARK_RED)

    def _get_completer(self) -> WordCompleter:
        """Completer to provide auto-completion for the menu options."""
        return WordCompleter([*self.options.keys(), self.back_option.key], ignore_case=True)

    def _get_validator(self) -> Validator:
        """Validator to check if the input is a valid option."""
        valid_keys = {key.upper() for key in self.options.keys()} | {self.back_option.key.upper()}
        valid_keys_str = ", ".join(sorted(valid_keys))
        return Validator.from_callable(
            lambda text: text.upper() in valid_keys,
            error_message=f"Invalid option. Valid options are: {valid_keys_str}",
            move_cursor_to_end=True,
        )

    def _invalidate_table_cache(self):
        """Forces the table to be recreated on the next access."""
        if hasattr(self, "table"):
            del self.table

    def _refresh_session(self):
        """Refreshes the prompt session to apply any changes."""
        self.session.completer = self._get_completer()
        self.session.validator = self._get_validator()
        self._invalidate_table_cache()

    def _get_prompt_session(self) -> PromptSession:
        """Returns the prompt session for the menu."""
        return PromptSession(
            message=self.prompt,
            multiline=False,
            completer=self._get_completer(),
            reserve_space_for_menu=1,
            validator=self._get_validator(),
            bottom_toolbar=self.bottom_bar,
        )

    def add_before(self, hook: Callable[["Option"], None]) -> None:
        """Adds a hook to be executed before the action of the menu."""
        self.before_action.add_hook(hook)

    def add_after(self, hook: Callable[["Option"], None]) -> None:
        """Adds a hook to be executed after the action of the menu."""
        self.after_action.add_hook(hook)

    def add_on_error(self, hook: Callable[["Option", Exception], None]) -> None:
        """Adds a hook to be executed on error of the menu."""
        self.on_error.add_hook(hook)

    def debug_hooks(self) -> None:
        if not self._verbose:
            return
        logger.debug(f"Menu-level before hooks: {[hook.__name__ for hook in self.before_action.hooks]}")
        logger.debug(f"Menu-level after hooks: {[hook.__name__ for hook in self.after_action.hooks]}")
        logger.debug(f"Menu-level error hooks: {[hook.__name__ for hook in self.on_error.hooks]}")
        for key, option in self.options.items():
            logger.debug(f"[Option '{key}'] before: {[hook.__name__ for hook in option.before_action.hooks]}")
            logger.debug(f"[Option '{key}'] after: {[hook.__name__ for hook in option.after_action.hooks]}")
            logger.debug(f"[Option '{key}'] error: {[hook.__name__ for hook in option.on_error.hooks]}")

    def _validate_option_key(self, key: str) -> None:
        """Validates the option key to ensure it is unique."""
        if key in self.options or key.upper() == self.back_option.key.upper():
            raise OptionAlreadyExistsError(f"Option with key '{key}' already exists.")

    def update_back_option(
        self,
        key: str = "0",
        description: str = "Back",
        action: Callable[[], Any] = lambda: None,
        color: str = OneColors.DARK_RED,
        confirm: bool = False,
        confirm_message: str = "Are you sure?",
    ) -> None:
        """Updates the back option of the menu."""
        if not callable(action):
            raise InvalidActionError("Action must be a callable.")
        self._validate_option_key(key)
        self.back_option = Option(
            key=key,
            description=description,
            action=action,
            color=color,
            confirm=confirm,
            confirm_message=confirm_message,
        )
        self._refresh_session()

    def add_submenu(self, key: str, description: str, submenu: "Menu", color: str = OneColors.CYAN) -> None:
        """Adds a submenu to the menu."""
        if not isinstance(submenu, Menu):
            raise NotAMenuError("submenu must be an instance of Menu.")
        self._validate_option_key(key)
        self.add_option(key, description, submenu.run, color)
        self._refresh_session()

    def add_options(self, options: list[dict]) -> None:
        """Adds multiple options to the menu."""
        for option in options:
            self.add_option(**option)

    def add_option(
        self,
        key: str,
        description: str,
        action: Callable[[], Any],
        color: str = OneColors.WHITE,
        confirm: bool = False,
        confirm_message: str = "Are you sure?",
        spinner: bool = False,
        spinner_message: str = "Processing...",
        spinner_type: str = "dots",
        spinner_style: str = OneColors.CYAN,
        spinner_kwargs: dict[str, Any] = None,
        before_hooks: list[Callable[[Option], None]] = None,
        after_hooks: list[Callable[[Option], None]] = None,
        error_hooks: list[Callable[[Option, Exception], None]] = None,
    ) -> Option:
        """Adds an option to the menu, preventing duplicates."""
        self._validate_option_key(key)
        if not spinner_kwargs:
            spinner_kwargs = {}
        option = Option(
            key=key,
            description=description,
            action=action,
            color=color,
            confirm=confirm,
            confirm_message=confirm_message,
            spinner=spinner,
            spinner_message=spinner_message,
            spinner_type=spinner_type,
            spinner_style=spinner_style,
            spinner_kwargs=spinner_kwargs,
            before_action=Hooks(hooks=before_hooks),
            after_action=Hooks(hooks=after_hooks),
            on_error=Hooks(hooks=error_hooks),
        )
        self.options[key] = option
        self._refresh_session()
        return option

    @cached_property
    def table(self) -> Table:
        """Creates a rich table to display the menu options."""
        table = Table(title=self.title, show_header=False, box=box.SIMPLE, expand=True)
        for chunk in chunks(self.options.items(), self.columns):
            row = []
            for key, option in chunk:
                row.append(f"[{key}] [{option.color}]{option.description}")
            table.add_row(*row)
        table.add_row(f"[{self.back_option.key}] [{self.back_option.color}]{self.back_option.description}")
        return table

    def get_option(self, choice: str) -> Option | None:
        """Returns the selected option based on user input."""
        if choice.upper() == self.back_option.key.upper():
            return self.back_option
        return self.options.get(choice)

    def _should_hooks_run(self, selected_option: Option) -> bool:
        """Determines if hooks should be run based on the selected option."""
        return selected_option != self.back_option or self.run_hooks_on_back_option

    def _should_run_action(self, selected_option: Option) -> bool:
        if selected_option.confirm and not self._never_confirm:
            return confirm(selected_option.confirm_message)
        return True

    def _run_action_with_spinner(self, option: Option) -> Any:
        """Runs the action of the selected option with a spinner."""
        with self.console.status(
            option.spinner_message,
            spinner=option.spinner_type,
            spinner_style=option.spinner_style,
            **option.spinner_kwargs,
        ):
            return option.action()

    def _handle_action_error(self, selected_option: Option, error: Exception) -> bool:
        """Handles errors that occur during the action of the selected option."""
        logger.exception(f"Error executing '{selected_option.description}': {error}")
        self.console.print(f"[{OneColors.DARK_RED}]An error occurred while executing "
                           f"{selected_option.description}:[/] {error}")
        selected_option.on_error.run_hooks(selected_option, error)
        self.on_error.run_hooks(selected_option, error)
        if self.continue_on_error_prompt and not self._never_confirm:
            return confirm("An error occurred. Do you wish to continue?")
        if self._never_confirm:
            return True
        return False

    def process_action(self) -> bool:
        """Processes the action of the selected option."""
        choice = self.session.prompt()
        selected_option = self.get_option(choice)
        self.last_run_option = selected_option
        should_hooks_run = self._should_hooks_run(selected_option)
        if not self._should_run_action(selected_option):
            logger.info(f"[{OneColors.DARK_RED}] {selected_option.description} cancelled.")
            return True
        try:
            if should_hooks_run:
                self.before_action.run_hooks(selected_option)
            selected_option.before_action.run_hooks(selected_option)
            if selected_option.spinner:
                result = self._run_action_with_spinner(selected_option)
            else:
                result = selected_option.action()
            selected_option.set_result(result)
            selected_option.after_action.run_hooks(selected_option)
            if should_hooks_run:
                self.after_action.run_hooks(selected_option)
        except Exception as error:
            return self._handle_action_error(selected_option, error)
        return selected_option != self.back_option

    def run_headless(self, option_key: str, never_confirm: bool | None = None) -> Any:
        """Runs the action of the selected option without displaying the menu."""
        self.debug_hooks()
        if never_confirm is not None:
            self._never_confirm = never_confirm

        selected_option = self.get_option(option_key)
        self.last_run_option = selected_option
        if not selected_option:
            raise MenuError(f"[Headless] Option '{option_key}' not found.")

        logger.info(f"[Headless] 🚀 Running: '{selected_option.description}'")
        should_hooks_run = self._should_hooks_run(selected_option)
        if not self._should_run_action(selected_option):
            logger.info(f"[Headless] ⛔ '{selected_option.description}' cancelled.")
            raise MenuError(f"[Headless] '{selected_option.description}' cancelled by confirmation.")

        try:
            if should_hooks_run:
                self.before_action.run_hooks(selected_option)
            selected_option.before_action.run_hooks(selected_option)
            if selected_option.spinner:
                result = self._run_action_with_spinner(selected_option)
            else:
                result = selected_option.action()
            selected_option.set_result(result)
            selected_option.after_action.run_hooks(selected_option)
            if should_hooks_run:
                self.after_action.run_hooks(selected_option)
            logger.info(f"[Headless] ✅ '{selected_option.description}' complete.")
        except (KeyboardInterrupt, EOFError):
            raise MenuError(f"[Headless] ⚠️ '{selected_option.description}' interrupted by user.")
        except Exception as error:
            continue_running = self._handle_action_error(selected_option, error)
            if not continue_running:
                raise MenuError(f"[Headless] ❌ '{selected_option.description}' failed.") from error
        return selected_option.get_result()

    def run(self) -> None:
        """Runs the menu and handles user input."""
        logger.info(f"Running menu: {self.get_title()}")
        self.debug_hooks()
        if self.welcome_message:
            self.console.print(self.welcome_message)
        while True:
            self.console.print(self.table)
            try:
                if not self.process_action():
                    break
            except (EOFError, KeyboardInterrupt):
                logger.info(f"[{OneColors.DARK_RED}]EOF or KeyboardInterrupt. Exiting menu.")
                break
        logger.info(f"Exiting menu: {self.get_title()}")
        if self.exit_message:
            self.console.print(self.exit_message)


if __name__ == "__main__":
    from rich.traceback import install
    from logging_utils import setup_logging

    install(show_locals=True)
    setup_logging()

    def say_hello():
        print("Hello!")

    def say_goodbye():
        print("Goodbye!")

    def say_nested():
        print("This is a nested menu!")

    def my_action():
        print("This is my action!")

    def long_running_task():
        import time

        time.sleep(5)

    nested_menu = Menu(
        Markdown("## Nested Menu", style=OneColors.DARK_YELLOW),
        columns=2,
        bottom_bar="Menu within a menu",
    )
    nested_menu.add_option("1", "Say Nested", say_nested, color=OneColors.MAGENTA)
    nested_menu.add_before(lambda opt: logger.info(f"Global BEFORE '{opt.description}'"))
    nested_menu.add_after(lambda opt: logger.info(f"Global AFTER '{opt.description}'"))

    nested_menu.add_option(
        "2",
        "Test Action",
        action=my_action,
        before_hooks=[lambda opt: logger.info(f"Option-specific BEFORE '{opt.description}'")],
        after_hooks=[lambda opt: logger.info(f"Option-specific AFTER '{opt.description}'")],
    )

    def bottom_bar():
        return (
            f"Press Q to quit | Options available: {', '.join([f'[{key}]' for key in menu.options.keys()])}"
        )

    welcome_message = Markdown("# Welcome to the Menu!")
    exit_message = Markdown("# Thank you for using the menu!")
    menu = Menu(
        Markdown("## Main Menu", style=OneColors.CYAN),
        columns=3,
        bottom_bar=bottom_bar,
        welcome_message=welcome_message,
        exit_message=exit_message,
    )
    menu.add_option("1", "Say Hello", say_hello, color=OneColors.GREEN)
    menu.add_option("2", "Say Goodbye", say_goodbye, color=OneColors.LIGHT_RED)
    menu.add_option("3", "Do Nothing", lambda: None, color=OneColors.BLUE)
    menu.add_submenu("4", "Nested Menu", nested_menu, color=OneColors.MAGENTA)
    menu.add_option("5", "Do Nothing", lambda: None, color=OneColors.BLUE)
    menu.add_option(
        "6",
        "Long Running Task",
        action=long_running_task,
        spinner=True,
        spinner_message="Working, please wait...",
        spinner_type="moon",
        spinner_style=OneColors.GREEN,
        spinner_kwargs={"speed": 0.7},
    )

    menu.update_back_option("Q", "Quit", color=OneColors.DARK_RED)

    try:
        menu.run()
    except EOFError as error:
        logger.exception("EOFError: Exiting program.", exc_info=error)
        print("Exiting program.")
