from typing import Dict

from rich.style import Style
from rich.theme import Theme
from rich.console import Console

class NordColors:
    """
    Defines the Nord color palette as class attributes.

    Each color is labeled by its canonical Nord name (NORD0-NORD15)
    and also has useful aliases grouped by theme:
    - Polar Night
    - Snow Storm
    - Frost
    - Aurora
    """

    # Polar Night
    NORD0 = "#2E3440"
    NORD1 = "#3B4252"
    NORD2 = "#434C5E"
    NORD3 = "#4C566A"

    # Snow Storm
    NORD4 = "#D8DEE9"
    NORD5 = "#E5E9F0"
    NORD6 = "#ECEFF4"

    # Frost
    NORD7 = "#8FBCBB"
    NORD8 = "#88C0D0"
    NORD9 = "#81A1C1"
    NORD10 = "#5E81AC"

    # Aurora
    NORD11 = "#BF616A"
    NORD12 = "#D08770"
    NORD13 = "#EBCB8B"
    NORD14 = "#A3BE8C"
    NORD15 = "#B48EAD"

    POLAR_NIGHT_ORIGIN = NORD0
    POLAR_NIGHT_BRIGHT = NORD1
    POLAR_NIGHT_BRIGHTER = NORD2
    POLAR_NIGHT_BRIGHTEST = NORD3

    SNOW_STORM_BRIGHT = NORD4
    SNOW_STORM_BRIGHTER = NORD5
    SNOW_STORM_BRIGHTEST = NORD6

    FROST_TEAL = NORD7
    FROST_ICE = NORD8
    FROST_SKY = NORD9
    FROST_DEEP = NORD10

    RED = NORD11
    ORANGE = NORD12
    YELLOW = NORD13
    GREEN = NORD14
    PURPLE = NORD15

    @classmethod
    def as_dict(cls):
        """
        Returns a dictionary mapping every NORD* attribute
        (e.g. 'NORD0') to its hex code.
        """
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if attr.startswith("NORD") and not callable(getattr(cls, attr))
        }

    @classmethod
    def aliases(cls):
        """
        Returns a dictionary of *all* other aliases 
        (Polar Night, Snow Storm, Frost, Aurora).
        """
        skip_prefixes = ("NORD", "__")
        alias_names = [
            attr for attr in dir(cls)
            if not any(attr.startswith(sp) for sp in skip_prefixes) 
            and not callable(getattr(cls, attr))
        ]
        return {name: getattr(cls, name) for name in alias_names}

NORD_THEME_STYLES: Dict[str, Style] = {
    # ---------------------------------------------------------------
    # Base / Structural styles
    # ---------------------------------------------------------------
    "none": Style.null(),
    "reset": Style(
        color="default",
        bgcolor="default",
        dim=False,
        bold=False,
        italic=False,
        underline=False,
        blink=False,
        blink2=False,
        reverse=False,
        conceal=False,
        strike=False,
    ),
    "dim": Style(dim=True),
    "bright": Style(dim=False),
    "bold": Style(bold=True),
    "strong": Style(bold=True),
    "code": Style(reverse=True, bold=True),
    "italic": Style(italic=True),
    "emphasize": Style(italic=True),
    "underline": Style(underline=True),
    "blink": Style(blink=True),
    "blink2": Style(blink2=True),
    "reverse": Style(reverse=True),
    "strike": Style(strike=True),

    # ---------------------------------------------------------------
    # Basic color names mapped to Nord
    # ---------------------------------------------------------------
    "black": Style(color=NordColors.NORD0),
    "red": Style(color=NordColors.RED),
    "green": Style(color=NordColors.GREEN),
    "yellow": Style(color=NordColors.YELLOW),
    "magenta": Style(color=NordColors.PURPLE),
    "cyan": Style(color=NordColors.FROST_ICE),
    "white": Style(color=NordColors.SNOW_STORM_BRIGHTEST),

    # ---------------------------------------------------------------
    # Inspect
    # ---------------------------------------------------------------
    "inspect.attr": Style(color=NordColors.YELLOW, italic=True),
    "inspect.attr.dunder": Style(color=NordColors.YELLOW, italic=True, dim=True),
    "inspect.callable": Style(bold=True, color=NordColors.RED),
    "inspect.async_def": Style(italic=True, color=NordColors.FROST_ICE),
    "inspect.def": Style(italic=True, color=NordColors.FROST_ICE),
    "inspect.class": Style(italic=True, color=NordColors.FROST_ICE),
    "inspect.error": Style(bold=True, color=NordColors.RED),
    "inspect.equals": Style(),
    "inspect.help": Style(color=NordColors.FROST_ICE),
    "inspect.doc": Style(dim=True),
    "inspect.value.border": Style(color=NordColors.GREEN),

    # ---------------------------------------------------------------
    # Live / Layout
    # ---------------------------------------------------------------
    "live.ellipsis": Style(bold=True, color=NordColors.RED),
    "layout.tree.row": Style(dim=False, color=NordColors.RED),
    "layout.tree.column": Style(dim=False, color=NordColors.FROST_DEEP),

    # ---------------------------------------------------------------
    # Logging
    # ---------------------------------------------------------------
    "logging.keyword": Style(bold=True, color=NordColors.YELLOW),
    "logging.level.notset": Style(dim=True),
    "logging.level.debug": Style(color=NordColors.GREEN),
    "logging.level.info": Style(color=NordColors.FROST_ICE),
    "logging.level.warning": Style(color=NordColors.RED),
    "logging.level.error": Style(color=NordColors.RED, bold=True),
    "logging.level.critical": Style(color=NordColors.RED, bold=True, reverse=True),
    "log.level": Style.null(),
    "log.time": Style(color=NordColors.FROST_ICE, dim=True),
    "log.message": Style.null(),
    "log.path": Style(dim=True),

    # ---------------------------------------------------------------
    # Python repr
    # ---------------------------------------------------------------
    "repr.ellipsis": Style(color=NordColors.YELLOW),
    "repr.indent": Style(color=NordColors.GREEN, dim=True),
    "repr.error": Style(color=NordColors.RED, bold=True),
    "repr.str": Style(color=NordColors.GREEN, italic=False, bold=False),
    "repr.brace": Style(bold=True),
    "repr.comma": Style(bold=True),
    "repr.ipv4": Style(bold=True, color=NordColors.GREEN),
    "repr.ipv6": Style(bold=True, color=NordColors.GREEN),
    "repr.eui48": Style(bold=True, color=NordColors.GREEN),
    "repr.eui64": Style(bold=True, color=NordColors.GREEN),
    "repr.tag_start": Style(bold=True),
    "repr.tag_name": Style(color=NordColors.PURPLE, bold=True),
    "repr.tag_contents": Style(color="default"),
    "repr.tag_end": Style(bold=True),
    "repr.attrib_name": Style(color=NordColors.YELLOW, italic=False),
    "repr.attrib_equal": Style(bold=True),
    "repr.attrib_value": Style(color=NordColors.PURPLE, italic=False),
    "repr.number": Style(color=NordColors.FROST_ICE, bold=True, italic=False),
    "repr.number_complex": Style(color=NordColors.FROST_ICE, bold=True, italic=False),
    "repr.bool_true": Style(color=NordColors.GREEN, italic=True),
    "repr.bool_false": Style(color=NordColors.RED, italic=True),
    "repr.none": Style(color=NordColors.PURPLE, italic=True),
    "repr.url": Style(underline=True, color=NordColors.FROST_ICE, italic=False, bold=False),
    "repr.uuid": Style(color=NordColors.YELLOW, bold=False),
    "repr.call": Style(color=NordColors.PURPLE, bold=True),
    "repr.path": Style(color=NordColors.PURPLE),
    "repr.filename": Style(color=NordColors.PURPLE),

    # ---------------------------------------------------------------
    # Rule
    # ---------------------------------------------------------------
    "rule.line": Style(color=NordColors.GREEN),
    "rule.text": Style.null(),

    # ---------------------------------------------------------------
    # JSON
    # ---------------------------------------------------------------
    "json.brace": Style(bold=True),
    "json.bool_true": Style(color=NordColors.GREEN, italic=True),
    "json.bool_false": Style(color=NordColors.RED, italic=True),
    "json.null": Style(color=NordColors.PURPLE, italic=True),
    "json.number": Style(color=NordColors.FROST_ICE, bold=True, italic=False),
    "json.str": Style(color=NordColors.GREEN, italic=False, bold=False),
    "json.key": Style(color=NordColors.FROST_ICE, bold=True),

    # ---------------------------------------------------------------
    # Prompt
    # ---------------------------------------------------------------
    "prompt": Style.null(),
    "prompt.choices": Style(color=NordColors.PURPLE, bold=True),
    "prompt.default": Style(color=NordColors.FROST_ICE, bold=True),
    "prompt.invalid": Style(color=NordColors.RED),
    "prompt.invalid.choice": Style(color=NordColors.RED),

    # ---------------------------------------------------------------
    # Pretty
    # ---------------------------------------------------------------
    "pretty": Style.null(),

    # ---------------------------------------------------------------
    # Scope
    # ---------------------------------------------------------------
    "scope.border": Style(color=NordColors.FROST_ICE),
    "scope.key": Style(color=NordColors.YELLOW, italic=True),
    "scope.key.special": Style(color=NordColors.YELLOW, italic=True, dim=True),
    "scope.equals": Style(color=NordColors.RED),

    # ---------------------------------------------------------------
    # Table
    # ---------------------------------------------------------------
    "table.header": Style(bold=True),
    "table.footer": Style(bold=True),
    "table.cell": Style.null(),
    "table.title": Style(italic=True),
    "table.caption": Style(italic=True, dim=True),

    # ---------------------------------------------------------------
    # Traceback
    # ---------------------------------------------------------------
    "traceback.error": Style(color=NordColors.RED, italic=True),
    "traceback.border.syntax_error": Style(color=NordColors.RED),
    "traceback.border": Style(color=NordColors.RED),
    "traceback.text": Style.null(),
    "traceback.title": Style(color=NordColors.RED, bold=True),
    "traceback.exc_type": Style(color=NordColors.RED, bold=True),
    "traceback.exc_value": Style.null(),
    "traceback.offset": Style(color=NordColors.RED, bold=True),

    # ---------------------------------------------------------------
    # Progress bars
    # ---------------------------------------------------------------
    "bar.back": Style(color=NordColors.NORD3),
    "bar.complete": Style(color=NordColors.RED),
    "bar.finished": Style(color=NordColors.GREEN),
    "bar.pulse": Style(color=NordColors.RED),
    "progress.description": Style.null(),
    "progress.filesize": Style(color=NordColors.GREEN),
    "progress.filesize.total": Style(color=NordColors.GREEN),
    "progress.download": Style(color=NordColors.GREEN),
    "progress.elapsed": Style(color=NordColors.YELLOW),
    "progress.percentage": Style(color=NordColors.PURPLE),
    "progress.remaining": Style(color=NordColors.FROST_ICE),
    "progress.data.speed": Style(color=NordColors.RED),
    "progress.spinner": Style(color=NordColors.GREEN),
    "status.spinner": Style(color=NordColors.GREEN),

    # ---------------------------------------------------------------
    # Tree
    # ---------------------------------------------------------------
    "tree": Style(),
    "tree.line": Style(),

    # ---------------------------------------------------------------
    # Markdown
    # ---------------------------------------------------------------
    "markdown.paragraph": Style(),
    "markdown.text": Style(),
    "markdown.em": Style(italic=True),
    "markdown.emph": Style(italic=True),  # For commonmark compatibility
    "markdown.strong": Style(bold=True),
    "markdown.code": Style(bold=True, color=NordColors.FROST_ICE, bgcolor=NordColors.NORD0),
    "markdown.code_block": Style(color=NordColors.FROST_ICE, bgcolor=NordColors.NORD0),
    "markdown.block_quote": Style(color=NordColors.PURPLE),
    "markdown.list": Style(color=NordColors.FROST_ICE),
    "markdown.item": Style(),
    "markdown.item.bullet": Style(color=NordColors.YELLOW, bold=True),
    "markdown.item.number": Style(color=NordColors.YELLOW, bold=True),
    "markdown.hr": Style(color=NordColors.YELLOW),
    "markdown.h1.border": Style(),
    "markdown.h1": Style(bold=True),
    "markdown.h2": Style(bold=True, underline=True),
    "markdown.h3": Style(bold=True),
    "markdown.h4": Style(bold=True, dim=True),
    "markdown.h5": Style(underline=True),
    "markdown.h6": Style(italic=True),
    "markdown.h7": Style(italic=True, dim=True),
    "markdown.link": Style(color=NordColors.FROST_ICE),
    "markdown.link_url": Style(color=NordColors.FROST_SKY, underline=True),
    "markdown.s": Style(strike=True),

    # ---------------------------------------------------------------
    # ISO8601
    # ---------------------------------------------------------------
    "iso8601.date": Style(color=NordColors.FROST_ICE),
    "iso8601.time": Style(color=NordColors.PURPLE),
    "iso8601.timezone": Style(color=NordColors.YELLOW),
}

def get_nord_theme() -> Theme:
    """
    Returns a Rich Theme for the Nord color palette.
    """
    return Theme(NORD_THEME_STYLES)


if __name__ == "__main__":
    console = Console(theme=get_nord_theme(), color_system="truecolor")

    console.print("This is default text (no style).")
    console.print("This is [red]red[/].")
    console.print("This is [green]green[/].")
    console.print("This is [blue]blue[/] (maps to Frost).")
    console.print("[bold]Bold text[/] and [italic]italic text[/]")

    console.log("Log sample in info mode.")
    console.log("Another log", style="logging.level.warning")

    # Demonstrate a traceback style:
    try:
        raise ValueError("Nord test exception!")
    except ValueError:
        console.print_exception(show_locals=True)
