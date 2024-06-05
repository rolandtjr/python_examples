import time

from prompt_toolkit.formatted_text import HTML, merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent as E
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.shortcuts.progress_bar import formatters
from prompt_toolkit.styles import Style

style = Style.from_dict(
    {
        "title": "#FF8400 underline",
        "label": "#D8DEE9 bold",
        "percentage": "#FF8400",
        "bar-a": "bg:#FF8400 #FF8400",
        "bar-b": "bg:#FF8400 #2E3440",
        "bar-c": "#D8DEE9",
        "current": "#D8DEE9",
        "total": "#FF8400",
        "time-elapsed": "#D8DEE9",
        "time-left": "#FF8400",
    }
)


custom_formatters = [
    formatters.Label(suffix=": "),
    formatters.Bar(start="|", end="|", sym_a="\u2588", sym_b="\u2588", sym_c="\u2591"),
    formatters.Text(" "),
    formatters.Progress(),
    formatters.Text(" "),
    formatters.Percentage(),
    formatters.Text(" [elapsed: "),
    formatters.TimeElapsed(),
    formatters.Text(" left: "),
    formatters.TimeLeft(),
    formatters.Text("]"),
]


def get_toolbar():
    return f"time: {time.ctime():<30}"


def create_confirm_session(
    message: str, suffix: str = " (y/n) "
) -> PromptSession[bool]:
    """
    Create a `PromptSession` object for the 'confirm' function.
    """
    bindings = KeyBindings()

    @bindings.add("y")
    @bindings.add("Y")
    def yes(event: E) -> None:
        session.default_buffer.text = "y"
        event.app.exit(result=True)

    @bindings.add("n")
    @bindings.add("N")
    def no(event: E) -> None:
        session.default_buffer.text = "n"
        event.app.exit(result=False)

    @bindings.add("enter")
    def enter(event: E) -> None:
        "Accept the current value."
        session.default_buffer.text = "y"
        event.app.exit(result=True)

    @bindings.add(Keys.Any)
    def _(event: E) -> None:
        "Disallow inserting other text."
        pass

    complete_message = merge_formatted_text([message, suffix])
    session: PromptSession[bool] = PromptSession(
        complete_message, key_bindings=bindings
    )
    return session


def confirm(message: str = "Confirm?", suffix: str = " (y/n) ") -> bool:
    """
    Display a confirmation prompt that returns True/False.
    """
    session = create_confirm_session(message, suffix)
    return session.prompt()


def confirm_async(message: str = "Confirm?", suffix: str = " (y/n) ") -> bool:
    """
    Display a confirmation prompt that returns True/False.
    """
    session = create_confirm_session(message, suffix)
    return session.prompt_async()