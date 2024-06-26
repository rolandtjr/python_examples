from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.bindings.basic import load_basic_bindings
from prompt_toolkit.shortcuts import prompt, PromptSession
from prompt_toolkit.validation import Validator
from rich.table import Table
from rich.console import Console

keybindings = load_basic_bindings()

@keybindings.add('c-q')
def exit_(event):
    """ Pressing 'c-q' will exit the application. """
    exit(0)

@keybindings.add('c-m')
def open_menu(event):
    """ Pressing 'c-m' will open the menu. """
    show_keybindings_menu()
    event.app.exit()

@keybindings.add('enter')
def process_input(event):
    """ Pressing 'enter' will process the input. """
    print(dir(event))
    event.app.exit(result=event.current_buffer.text)

bindings_info = [
    {"Key": "Ctrl-Q", "Action": "Exit the application"},
    {"Key": "Ctrl-M", "Action": "Open the menu"},
]

def is_y_n(text):
    return text in ["y", "n", "Y", "N", ""]

yes_no_validator = Validator.from_callable(
    is_y_n,
    error_message="Please enter 'y' or 'n'",
    move_cursor_to_end=True,
)

def confirm(message: str = "Confirm?", suffix: str = " (y/n) \u276f ") -> bool:
    result = prompt(f"{message}{suffix}", validator=yes_no_validator)
    return result.lower() == "y" or result == ""


console = Console()


def show_keybindings_menu():
    table = Table(title="Keybindings")

    table.add_column("Key", justify="right", style="cyan", no_wrap=True)
    table.add_column("Action", style="magenta")

    for binding in bindings_info:
        table.add_row(binding["Key"], binding["Action"])

    console.print(table)


def main_menu():
    session = PromptSession("\u276f ", key_bindings=keybindings)
    while True:
        show_keybindings_menu()

        user_input = session.prompt()
        console.print(f"You entered: {user_input}")

        result = confirm("Do you want to continue?")

        if not result:
            break



if __name__ == "__main__":
    main_menu()
