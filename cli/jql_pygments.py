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
from prompt_toolkit.completion import WordCompleter
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
                r"timespent|Voter|Watcher|affectedVersion)\b",
                Name.Attribute,
            ),
            (r"(?i)(=|!=|<|>|<=|>=|~|!~|IN|NOT IN|IS|IS NOT|WAS|WAS IN|WAS NOT IN|WAS NOT)", Operator),
            (r"[\*\(/\^\.@;:+%#\[\|\?\),\$]", Punctuation),
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
}


completions = [
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
    "watcher",
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
    "WITH",
    "issueHistory",
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
    "endOfYear",
]


class JQLPrinter:
    def __init__(self, console: Console):
        self.console = console

    def print(self, text: str):
        self.console.print(self.pygments_to_rich(text))

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


def create_jira_prompt_session(jira):
    completer = WordCompleter(completions, ignore_case=True)
    return PromptSession(
        lexer=PygmentsLexer(JQLLexer),
        style=nord_style,
        completer=completer,
        validator=JQLValidator(jira),
        rprompt="[b] Back [exit] Exit",
    )

with open("config.json") as json_file:
    config = json.load(json_file)

def main():
    console = Console(color_system="truecolor")
    jira = JIRA(server=config["server"], basic_auth=(config["username"], config["token"]))
    jql = JQLPrinter(console)
    session = create_jira_prompt_session(jira)
    while True:
        try:
            user_input = session.prompt("Enter JQL: ", validate_while_typing=False)
            if user_input.lower() == "b":
                continue
            if user_input.lower() == "exit":
                break
            jql.print(user_input)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
    console.print("Goodbye!", style="#BF616A bold")


if __name__ == "__main__":
    main()
