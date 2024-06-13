from itertools import chain
import json
from datetime import datetime
from typing import Dict, List, Optional, Iterable

from jira import JIRA
from jira.exceptions import JIRAError
from jira.resources import Issue
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import ValidationError, Validator
from prompt_toolkit.formatted_text import HTML, merge_formatted_text
from pygments.lexer import RegexLexer
from pygments.token import (Error, Keyword, Name,
                             Operator, Punctuation,
                            String, Text, Whitespace, _TokenType)
from rich.console import Console
from rich.text import Text as RichText


class JQLLexer(RegexLexer):
    """ JQL Lexer for Pygments. """
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
                r"THERE|THESE|THEY|THIS|TO|WILL|WITH|ORDER BY|ASC|DESC)\b",
                Keyword,
            ),
            (
                r"(?i)\b(?:assignee|affectedVersion|attachments|category|comment|component|created|createdDate|"
                r"creator|cescription|due|duedate|filter|fixVersion|issuekey|issuetype|issueLinkType|labels|"
                r"lastViewed|priority|project|reporter|resolved|Sprint|status|statusCategory|summary|text|"
                r"timespent|updated|updatedDate|voter|watcher|watchers)\b",
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


class JQLStyles:
    """ JQL Styles for Pygments.
    Based on the Nord color palette: https://www.nordtheme.com/docs/colors-and-palettes
    """
    nord: Style = Style.from_dict(
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

    token: Dict[_TokenType, str] = {
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

    completion: Dict[str, str] = {
        "Keywords": "#81A1C1 bold",
        "Functions": "#A3BE8C",
        "Attributes": "#B48EAD",
        "Operators": "#EBCB8B bold",
        "Projects": "#D08770",
        "Order": "#BF616A bold",
    }


completions: Dict[str, List[str]] = {
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
        "WITH",
        "ORDER BY"
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
        "endOfYear",
    ],
    "Attributes": [
        "assignee",
        "affectedVersion",
        "attachments",
        "category",
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
        "updated",
        "voter",
        "watcher",
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
        "WAS NOT",
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
        "PHOTON",
    ],
    "Order": [
        "ASC",
        "DESC",
    ],
}


class JQLPrinter:
    """ JQL Printer to print JQL queries with syntax highlighting. """
    def __init__(self, console: Console):
        self.console = console

    def print(self, text: str):
        """ Print JQL query with syntax highlighting. """
        self.console.print(self.pygments_to_rich(text), end="")

    def pygments_to_rich(self, text):
        """ Convert Pygments tokens to RichText. """
        tokens = list(JQLLexer().get_tokens(text))
        rich_text = RichText()
        for token_type, value in tokens:
            style = JQLStyles.token.get(token_type, "white")
            rich_text.append(value, style=style)
        return rich_text


class JQLValidator(Validator):
    """ JQL Validator to validate JQL queries. """
    def __init__(self, jira_instance):
        self.jira = jira_instance

    def validate(self, document):
        """ Validate JQL query. """
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

    def __init__(self, categorized_completions: Dict[str, List[str]]):
        self.categorized_completions = categorized_completions

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        text_before_cursor = document.text_before_cursor.lower().strip()
        words = text_before_cursor.split()

        if document.text_before_cursor and document.text_before_cursor[-1].isspace():
            return self._get_next_word_completions(words, text_before_cursor)
        else:
            return self._get_current_word_completions(words[-1] if words else '')

    def _get_next_word_completions(self, words: List[str], text_before_cursor: str) -> Iterable[Completion]:
        if not words:
            return chain(self._get_category_completions("Attributes"),
                         self._get_category_completions("Functions"))

        last_word = words[-1]

        if last_word in ["and", "or"]:
            return chain(self._get_category_completions("Functions"),
                         self._get_category_completions("Attributes"))

        if last_word in self.categorized_completions.get("Operators", []):
            return self._get_category_completions("Projects")

        if last_word in ["order", "by"]:
            return self._get_category_completions("Attributes")

        if "order by" in text_before_cursor:
            return self._get_category_completions("Order")

        if last_word in self.categorized_completions.get("Attributes", []):
            return self._get_category_completions("Operators")

        return []

    def _get_current_word_completions(self, word: str) -> Iterable[Completion]:
        for category, words in self.categorized_completions.items():
            for completion_word in words:
                if word in completion_word.lower():
                    yield Completion(completion_word,
                                     start_position=-len(word),
                                     display=completion_word,
                                     display_meta=category,
                                     style=f"fg: #D8DEE9 bg: {JQLStyles.completion.get(category, 'white')}",
                                     selected_style=f"fg: {JQLStyles.completion.get(category, 'white')} bg: #D8DEE9",
                                    )

    def _get_category_completions(self, category: str) -> Iterable[Completion]:
        for word in self.categorized_completions.get(category, []):
            yield Completion(word, display=word, display_meta=category)


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
    """ JQL Prompt to interact with JIRA using JQL queries. """
    def __init__(self, jira):
        self.jira: JIRA = jira
        self.console: Console = Console(color_system="truecolor", record=True)
        self.session: PromptSession = self.create_jql_prompt_session()
        self.jql: JQLPrinter = JQLPrinter(self.console)
        self.query_count: int = 0
        self.issue_count: int = 0
        self.total_issue_count: int = 0
        self.issues: List[Issue] = []

    def get_query_count(self):
        space = self.console.width // 3
        query_count_str = f"Query Count: {self.query_count}" if self.query_count else ""
        query_count_html = HTML(f"<b><style fg='#2E3440' bg='#88C0D0'>{query_count_str:^{space}}</style></b>")
        issue_count_str = f"Issues Added: {self.issue_count}" if self.issue_count else ""
        issue_count_html = HTML(f"<b><style fg='#2E3440' bg='#B48EAD'>{issue_count_str:^{space}}</style></b>")
        total_issue_count_str = f"Total Issues: {self.total_issue_count}" if self.total_issue_count else ""
        total_issue_count_html = HTML(f"<b><style fg='#2E3440' bg='#D8DEE9'>{total_issue_count_str:^{space}}</style></b>")
        return merge_formatted_text([query_count_html, issue_count_html, total_issue_count_html])

    def create_jql_prompt_session(self):
        completer: JQLCompleter = JQLCompleter(completions)
        return PromptSession(
            message=[("#B48EAD", "JQL \u276f ")],
            lexer=PygmentsLexer(JQLLexer),
            style=JQLStyles.nord,
            completer=completer,
            validator=JQLValidator(self.jira),
            rprompt=[
                ("#5E81AC bold", "[b] Back "),
                ("#BF616A bold", "[exit] Exit"),
            ],
            bottom_toolbar=self.get_query_count,
            validate_while_typing=False,
        )

    def prompt(self) -> Optional[List[Issue]]:
        """ Prompt the user for a JQL query.
        Returns:
            Optional[List[Issue]]: List of JIRA issues.
        """
        user_input: str = self.session.prompt()
        self.issue_count = 0
        if not user_input:
            do_empty_query = confirm(
                [("#EBCB8B bold", "[?] "), ("#D8DEE9 bold", "Do you want to perform an empty query?")],
                suffix=[("#81A1C1 bold", " (Y/n) ")],
            )
            if not do_empty_query:
                return
        if user_input.lower() == "b":
            return
        if user_input.lower() == "exit":
            exit(0)
        issues = self.jira.search_issues(user_input)
        if issues:
            self.query_count += 1
            self.console.print(
                RichText.assemble(
                    (f"[+] Found {len(issues)} issues from JQL query: ", "#A3BE8C bold"),
                    self.jql.pygments_to_rich(user_input),
                ),
                end="",
            )
            return issues
        self.console.print("[!] No issues found.", style="#BF616A bold")

    def multi_prompt(self) -> Optional[List[Issue]]:
        """ Prompt the user for multiple JQL queries.
        Returns:
            Optional[List[Issue]]: List of JIRA issues.
        """
        self.issues = []
        while True:
            try:
                issues = self.prompt()
                if issues:
                    issues = [issue for issue in issues if issue not in self.issues]
                    self.issues.extend(issues)
                    self.issue_count += len(issues)
                    self.total_issue_count += len(issues)
                self.console.print(f"[ℹ] Total issues: {len(self.issues)}", style="#D8DEE9")
                get_more = confirm([("#A3BE8C", "[?] Get more issues?")], suffix=[("#81A1C1 bold", " (Y/n) ")])
                if not get_more:
                    break
            except (EOFError, KeyboardInterrupt):
                break
        if self.issues:
            self.console.print(f"[+] Issues added: {self.total_issue_count}", style="#A3BE8C bold")
            return self.issues
        self.console.print("[!] No issues added.", style="#BF616A bold")

    def save_log(self):
        """ Save the console log to a file. """
        log_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"jql_{log_time}.txt", "w") as log_file:
            log_file.write(self.console.export_text())


"""
[+] for additions
[-] for deletions
[~] for changes
[<] for incoming
[>] for outgoing
[✔] for success
[✖] for failure
[⚠] for warnings
[?] for questions
[!] for errors
[ℹ] for information
"""


def main():
    config = load_config()
    jira = JIRA(server=config["server"], basic_auth=(config["username"], config["token"]))
    prompt = JQLPrompt(jira)
    prompt.multi_prompt()


if __name__ == "__main__":
    main()
