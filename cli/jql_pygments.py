import json

from pygments.lexer import RegexLexer
from pygments.token import (
    Text,
    Keyword,
    Operator,
    Punctuation,
    Name,
    String,
    Whitespace,
    Error,
)
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from rich.console import Console
from rich.text import Text as RichText
from jira import JIRA
from jira.exceptions import JIRAError


class JQLLexer(RegexLexer):
    name = "JQL"
    aliases = ["jql"]
    filenames = ["*.jql"]

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r'"', String, "string"),
            (r"'", String, "string"),
            (
                r"(?i)\b(?:issueHistory|openSprints|watchedIssues|myApproval|myPending|currentLogin|currentUser|"
                r"membersOf|lastLogin|now|startOfDay|endOfDay|startOfWeek|endOfWeek|startOfMonth|endOfMonth|"
                r"startOfYear|endOfYear)\b",
                Name.Function,
            ),
            (
                r"(?i)\b(?:A|AND|ARE|AS|AT|BE|BUT|BY|FOR|IF|INTO|IT|NO|OF|ON|OR|S|SUCH|T|THAT|THE|THEIR|THEN|"
                r"THERE|THESE|THEY|THIS|TO|WILL|WITH)\b",
                Keyword,
            ),
            (
                r"(?i)\b(?:Assignee|affectedVersion|Attachments|Category|Comment|Component|Created|createdDate|"
                r"Creator|Description|Due|duedate|Filter|fixVersion|issuekey|issuetype|issueLinkType|Labels|"
                r"lastViewed|Priority|Project|Reporter|Resolved|Sprint|Status|statusCategory|Summary|Text|"
                r"timespent|Voter|Watcher)\b",
                Name.Attribute,
            ),
            (r"(?i)(=|!=|<|>|<=|>=|~|!~|IN|NOT IN|IS|IS NOT|WAS|WAS IN|WAS NOT IN|WAS NOT)", Operator),
            (r"[\*\(/\^\.@;:+%#\[\|\?\),\$]", Punctuation),
            (
                r"(?i)\b(?:QUANTUM|NEBULA|GALACTIC|STELLAR|AETHER|NOVA|COSMIC|LUNAR|ASTRAL|PHOTON)\b",
                Name.Other,
            ),
            (r"[\w\.\-]+", Text),
        ],
        "string": [
            (r'"', String, "#pop"),
            (r"'", String, "#pop"),
            (r'[^"\']+', String),
        ],
    }


nord_style = Style.from_dict(
    {
        "pygments.whitespace": "#FFFFFF",
        "pygments.keyword": "#81A1C1 bold",
        "pygments.operator": "#EBCB8B bold",
        "pygments.punctuation": "#BF616A",
        "pygments.name.attribute": "#B48EAD",
        "pygments.name.function": "#A3BE8C",
        "pygments.literal.string": "#D08770",
        "pygments.text": "#D8DEE9",
        "pygments.name.other": "#D08770",
        "pygments.error": "#BF616A bold",
    }
)


token_styles = {
    Whitespace: "#FFFFFF",
    Keyword: "#81A1C1 bold",
    Operator: "#EBCB8B bold",
    Punctuation: "#BF616A",
    Name.Attribute: "#B48EAD",
    Name.Function: "#A3BE8C",
    String: "#D08770",
    Text: "#D8DEE9",
    Error: "#BF616A bold",
    Name.Other: "#D08770",
}


completion_styles = {
    "Keywords": "#81A1C1 bold",
    "Functions": "#A3BE8C",
    "Attributes": "#B48EAD",
    "Operators": "#EBCB8B bold",
    "Projects": "#D08770",
}


completions ={
            "Keywords": [
                "A",
                "AND",
                "ARE",
                "AS",
                "AT",
                "BE",
                "BUT",
                "BY",
                "FOR",
                "IF",
                "INTO",
                "IT",
                "NO",
                "NOT",
                "OF",
                "ON",
                "OR",
                "S",
                "SUCH",
                "T",
                "THAT",
                "THE",
                "THEIR",
                "THEN",
                "THERE",
                "THESE",
                "THEY",
                "THIS",
                "TO",
                "WILL",
                "WITH"
            ],
            "Functions": [
                "issueHistory",
                "openSprints",
                "watchedIssues",
                "myApproval",
                "myPending",
                "currentLogin",
                "currentUser",
                "membersOf",
                "lastLogin",
                "now",
                "startOfDay",
                "endOfDay",
                "startOfWeek",
                "endOfWeek",
                "startOfMonth",
                "endOfMonth",
                "startOfYear",
                "endOfYear"
            ],
            "Attributes": [
                "assignee",
                "affectedVersion",
                "attachments",
                "comment",
                "component",
                "created",
                "creator",
                "description",
                "due",
                "duedate",
                "filter",
                "fixVersion",
                "issuekey",
                "labels",
                "lastViewed",
                "priority",
                "project",
                "reporter",
                "resolved",
                "sprint",
                "status",
                "statusCategory",
                "summary",
                "text",
                "timespent",
                "voter",
                "watcher"
            ],
            "Operators": [
                "=",
                "!=",
                "<",
                ">",
                "<=",
                ">=",
                "~",
                "!~",
                "IN",
                "NOT IN",
                "IS",
                "IS NOT",
                "WAS",
                "WAS IN",
                "WAS NOT IN",
                "WAS NOT"
            ],
            "Projects": [
                "QUANTUM",
                "NEBULA",
                "GALACTIC",
                "STELLAR",
                "AETHER",
                "NOVA",
                "COSMIC",
                "LUNAR",
                "ASTRAL",
                "PHOTON"
            ]
        }


class JQLPrinter:
    def __init__(self, console: Console):
        self.console = console

    def print(self, text: str):
        self.console.print(self.pygments_to_rich(text), end="")

    def pygments_to_rich(self, text):
        tokens = list(JQLLexer().get_tokens(text))
        rich_text = RichText()
        for token_type, value in tokens:
            style = token_styles.get(token_type, "white")
            rich_text.append(value, style=style)
        return rich_text


class JQLValidator(Validator):
    def __init__(self, jira_instance):
        self.jira = jira_instance

    def validate(self, document):
        text = document.text
        if text.lower() == "b" or text.lower() == "exit":
            return
        try:
            self.jira.search_issues(text, maxResults=1)
        except JIRAError as error:
            error_text = error.response.json().get("errorMessages", ["Unknown error"])[0]
            raise ValidationError(message=f"[!] {error_text}", cursor_position=len(text))


class JQLCompleter(Completer):
    """Custom JQL completer to categorize and color completions."""

    def __init__(self, categorized_completions):
        self.categorized_completions = categorized_completions

    def get_completions(self, document, complete_event):
        text = document.get_word_before_cursor().lower()
        for category, words in self.categorized_completions.items():
            for word in words:
                if text in word.lower():
                    display_text = f"{word}"
                    yield Completion(
                        word,
                        start_position=-len(text),
                        display=display_text,
                        display_meta=category,
                        style=f"fg: #D8DEE9 bg: {completion_styles.get(category, 'white')}",
                        selected_style=f"fg: {completion_styles.get(category, 'white')} bg: #D8DEE9",
                    )


def load_config():
    with open("config.json") as json_file:
        try:
            with open("config.json") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print("Configuration file not found.")
            exit(1)
        except json.JSONDecodeError:
            print("Error decoding configuration file.")
            exit(1)


class JQLPrompt:
    def __init__(self, jira, console):
        self.jira = jira
        self.console = console
        self.session = self.create_jql_prompt_session()
        self.jql = JQLPrinter(console)
        self.query_count = 0

    def get_query_count(self):
        space = self.console.width // 4
        query_count_str = f"Query count: {self.query_count}"
        plain_text = f"{query_count_str:^{space}}{query_count_str:^{space}}{query_count_str:^{space}}{query_count_str:^{space}}"
        return [("bg:#2E3440 #D8DEE9", plain_text)]

    def create_jql_prompt_session(self):
        completer = JQLCompleter(completions)
        return PromptSession(
            lexer=PygmentsLexer(JQLLexer),
            style=nord_style,
            completer=completer,
            validator=JQLValidator(self.jira),
            rprompt="[b] Back [exit] Exit",
            bottom_toolbar=self.get_query_count,
        )

    def get_input(self):
        user_input = self.session.prompt("Enter JQL: ", validate_while_typing=False)
        if user_input.lower() == "b":
            return
        if user_input.lower() == "exit":
            exit(0)
        issues = self.jira.search_issues(user_input)
        if issues:
            self.query_count += 1
            self.console.print(
                RichText.assemble(
                    (f"[+] Found {len(issues)} issues from JQL query: ", "green bold"),
                    self.jql.pygments_to_rich(user_input),
                ),
                end="",
            )
            for issue in issues:
                self.console.print(f"{issue.key}: {issue.fields.summary}")

    def run(self):
        while True:
            try:
                self.get_input()
            except (EOFError, KeyboardInterrupt):
                break
        self.console.print("Goodbye!", style="#BF616A bold")


def main():
    config = load_config()
    console = Console(color_system="truecolor")
    jira = JIRA(server=config["server"], basic_auth=(config["username"], config["token"]))
    prompt = JQLPrompt(jira, console)
    prompt.run()


if __name__ == "__main__":
    main()
