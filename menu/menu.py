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
import asyncio
import logging
from functools import cached_property
from typing import Any, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.validation import Validator
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from action import BaseAction
from bottom_bar import BottomBar
from colors import get_nord_theme
from hook_manager import HookManager
from menu_utils import (CaseInsensitiveDict, InvalidActionError, MenuError,
                        NotAMenuError, OptionAlreadyExistsError, chunks, run_async)
from one_colors import OneColors
from option import Option

logger = logging.getLogger("menu")


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
        self.bottom_bar: str | Callable[[], None] | None = bottom_bar or BottomBar(columns=columns)
        self.options: dict[str, Option] = CaseInsensitiveDict()
        self.back_option: Option = self._get_back_option()
        self.console: Console = Console(color_system="truecolor", theme=get_nord_theme())
        #self.session: PromptSession = self._get_prompt_session()
        self.welcome_message: str | Markdown = welcome_message
        self.exit_message: str | Markdown = exit_message
        self.hooks: HookManager = HookManager()
        self.run_hooks_on_back_option: bool = run_hooks_on_back_option
        self.continue_on_error_prompt: bool = continue_on_error_prompt
        self._never_confirm: bool = never_confirm
        self._verbose: bool = _verbose
        self.last_run_option: Option | None = None
        self.key_bindings: KeyBindings = KeyBindings()
        self.toggles: dict[str, str] = {}

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

    @cached_property
    def session(self) -> PromptSession:
        """Returns the prompt session for the menu."""
        return PromptSession(
            message=self.prompt,
            multiline=False,
            completer=self._get_completer(),
            reserve_space_for_menu=1,
            validator=self._get_validator(),
            bottom_toolbar=self.bottom_bar.render,
        )

    def add_toggle(self, key: str, label: str, state: bool = False):
        if key in self.options or key in self.toggles:
            raise ValueError(f"Key '{key}' is already in use.")

        self.toggles[key] = label
        self.bottom_bar.add_toggle(label, label, state)

        @self.key_bindings.add(key)
        def _(event):
            current = self.bottom_bar._states[label][1]
            self.bottom_bar.update_toggle(label, not current)
            self.console.print(f"Toggled [{label}] to {'ON' if not current else 'OFF'}")

    def add_counter(self, name: str, label: str, current: int, total: int):
        self.bottom_bar.add_counter(name, label, current, total)

    def update_counter(self, name: str, current: int | None = None, total: int | None = None):
        self.bottom_bar.update_counter(name, current=current, total=total)

    def update_toggle(self, name: str, state: bool):
        self.bottom_bar.update_toggle(name, state)

    def debug_hooks(self) -> None:
        if not self._verbose:
            return

        def hook_names(hook_list):
            return [hook.__name__ for hook in hook_list]

        logger.debug(f"Menu-level before hooks: {hook_names(self.hooks._hooks['before'])}")
        logger.debug(f"Menu-level after hooks: {hook_names(self.hooks._hooks['after'])}")
        logger.debug(f"Menu-level error hooks: {hook_names(self.hooks._hooks['on_error'])}")

        for key, option in self.options.items():
            logger.debug(f"[Option '{key}'] before: {hook_names(option.hooks._hooks['before'])}")
            logger.debug(f"[Option '{key}'] after: {hook_names(option.hooks._hooks['after'])}")
            logger.debug(f"[Option '{key}'] error: {hook_names(option.hooks._hooks['on_error'])}")

    def _validate_option_key(self, key: str) -> None:
        """Validates the option key to ensure it is unique."""
        if key.upper() in self.options or key.upper() == self.back_option.key.upper():
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
        action: BaseAction | Callable[[], Any],
        color: str = OneColors.WHITE,
        confirm: bool = False,
        confirm_message: str = "Are you sure?",
        spinner: bool = False,
        spinner_message: str = "Processing...",
        spinner_type: str = "dots",
        spinner_style: str = OneColors.CYAN,
        spinner_kwargs: dict[str, Any] | None = None,
        before_hooks: list[Callable] | None = None,
        after_hooks: list[Callable] | None = None,
        error_hooks: list[Callable] | None = None,
    ) -> Option:
        """Adds an option to the menu, preventing duplicates."""
        spinner_kwargs: dict[str, Any] = spinner_kwargs or {}
        self._validate_option_key(key)
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
        )

        for hook in before_hooks or []:
            option.hooks.register("before", hook)
        for hook in after_hooks or []:
            option.hooks.register("after", hook)
        for hook in error_hooks or []:
            option.hooks.register("on_error", hook)

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

    def _should_run_action(self, selected_option: Option) -> bool:
        if selected_option.confirm and not self._never_confirm:
            return confirm(selected_option.confirm_message)
        return True

    def _create_context(self, selected_option: Option) -> dict[str, Any]:
        """Creates a context dictionary for the selected option."""
        return {
            "name": selected_option.description,
            "option": selected_option,
            "args": (),
            "kwargs": {},
        }

    def _run_action_with_spinner(self, option: Option) -> Any:
        """Runs the action of the selected option with a spinner."""
        with self.console.status(
            option.spinner_message,
            spinner=option.spinner_type,
            spinner_style=option.spinner_style,
            **option.spinner_kwargs,
        ):
            return option()

    def _handle_action_error(self, selected_option: Option, error: Exception) -> bool:
        """Handles errors that occur during the action of the selected option."""
        logger.exception(f"Error executing '{selected_option.description}': {error}")
        self.console.print(f"[{OneColors.DARK_RED}]An error occurred while executing "
                           f"{selected_option.description}:[/] {error}")
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

        if selected_option == self.back_option:
            logger.info(f"🔙 Back selected: exiting {self.get_title()}")
            return False

        if not self._should_run_action(selected_option):
            logger.info(f"[{OneColors.DARK_RED}] {selected_option.description} cancelled.")
            return True

        context = self._create_context(selected_option)

        try:
            run_async(self.hooks.trigger("before", context))

            if selected_option.spinner:
                result = self._run_action_with_spinner(selected_option)
            else:
                result = selected_option()

            selected_option.set_result(result)
            context["result"] = result
            context["duration"] = selected_option.get_duration()
            run_async(self.hooks.trigger("after", context))
        except Exception as error:
            context["exception"] = error
            context["duration"] = selected_option.get_duration()
            run_async(self.hooks.trigger("on_error", context))
            if "exception" not in context:
                logger.info(f"✅ Recovery hook handled error for '{selected_option.description}'")
                return True
            return self._handle_action_error(selected_option, error)
        return True

    def run_headless(self, option_key: str, never_confirm: bool | None = None) -> Any:
        """Runs the action of the selected option without displaying the menu."""
        self.debug_hooks()
        if never_confirm is not None:
            self._never_confirm = never_confirm

        selected_option = self.get_option(option_key)
        self.last_run_option = selected_option

        if not selected_option:
            logger.info("[Headless] Back option selected. Exiting menu.")
            return

        logger.info(f"[Headless] 🚀 Running: '{selected_option.description}'")

        if not self._should_run_action(selected_option):
            raise MenuError(f"[Headless] '{selected_option.description}' cancelled by confirmation.")

        context = self._create_context(selected_option)

        try:
            run_async(self.hooks.trigger("before", context))

            if selected_option.spinner:
                result = self._run_action_with_spinner(selected_option)
            else:
                result = selected_option()

            selected_option.set_result(result)
            context["result"] = result
            context["duration"] = selected_option.get_duration()

            run_async(self.hooks.trigger("after", context))
            logger.info(f"[Headless] ✅ '{selected_option.description}' complete.")
        except (KeyboardInterrupt, EOFError):
            raise MenuError(f"[Headless] ⚠️ '{selected_option.description}' interrupted by user.")
        except Exception as error:
            context["exception"] = error
            context["duration"] = selected_option.get_duration()
            run_async(self.hooks.trigger("on_error", context))
            if "exception" not in context:
                logger.info(f"[Headless] ✅ Recovery hook handled error for '{selected_option.description}'")
                return True
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
