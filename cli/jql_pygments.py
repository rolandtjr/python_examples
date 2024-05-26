from pygments.lexer import RegexLexer, include
from pygments.token import Text, Keyword, Operator, Punctuation, Name, String, Whitespace
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter

class JQLLexer(RegexLexer):
    name = 'JQL'
    aliases = ['jql']
    filenames = ['*.jql']

    tokens = {
        'root': [
            (r'\s+', Whitespace),
            (r'"', String, 'string'),
            (r"'", String, 'string'),
            (r'(?i)\b(?:issueHistory|openSprints|watchedIssues|myApproval|myPending|currentLogin|currentUser|'
             r'membersOf|lastLogin|now|startOfDay|endOfDay|startOfWeek|endOfWeek|startOfMonth|endOfMonth|'
             r'startOfYear|endOfYear)\b', Name.Function),
            (r'(?i)\b(?:A|AND|ARE|AS|AT|BE|BUT|BY|FOR|IF|INTO|IT|NO|OF|ON|OR|S|SUCH|T|THAT|THE|THEIR|THEN|'
             r'THERE|THESE|THEY|THIS|TO|WILL|WITH)\b', Keyword),
            (r'(?i)\b(?:Assignee|affectedVersion|Attachments|Category|Comment|Component|Created|createdDate|'
             r'Creator|Description|Due|duedate|Filter|fixVersion|issuekey|issuetype|issueLinkType|Labels|'
             r'lastViewed|Priority|Project|Reporter|Resolved|Sprint|Status|statusCategory|Summary|Text|'
             r'timespent|Voter|Watcher|affectedVersion)\b', Name.Attribute),
            (r'(?i)(=|>|>=|~|IN|IS|WAS|CHANGED|!=|<|<=|!~|NOT)', Operator),
            (r'[\*\(/\^\.@;:+%#\[\|\?\),\$]]', Punctuation),
            (r'[\w\.\-]+', Text),
        ],
        'string': [
            (r'"', String, '#pop'),
            (r"'", String, '#pop'),
            (r'[^"\']+', String),
        ],
    }

nord_style = Style.from_dict({
    'whitespace': '#FFFFFF',
    'operator': '#B48EAD',
    'keyword': '#81A1C1 bold',
    'punctuation': '#BF616A',
    # 'name.attribute': '#A3BE8C',
    # 'name.function': '#B48EAD',
    'string': '#EBCB8B',
    'text': '#D8DEE9',
})

completions = [
    'assignee', 'affectedVersion', 'attachments', 'comment', 'component', 'created', 'creator', 'description',
    'due', 'duedate', 'filter', 'fixVersion', 'issuekey', 'labels', 'lastViewed', 'priority', 'project',
    'reporter', 'resolved', 'sprint', 'status', 'statusCategory', 'summary', 'text', 'timespent', 'voter', 'watcher',
    'A', 'AND', 'ARE', 'AS', 'AT', 'BE', 'BUT', 'BY', 'FOR', 'IF', 'INTO', 'IT', 'NO', 'NOT', 'OF', 'ON', 'OR', 'S',
    'SUCH', 'T', 'THAT', 'THE', 'THEIR', 'THEN', 'THERE', 'THESE', 'THEY', 'THIS', 'TO', 'WILL', 'WITH',
    'issueHistory', 'watchedIssues', 'myApproval', 'myPending', 'currentLogin', 'currentUser',
    'membersOf', 'lastLogin', 'now', 'startOfDay', 'endOfDay', 'startOfWeek', 'endOfWeek', 'startOfMonth', 'endOfMonth',
    'startOfYear', 'endOfYear'
]

completer = WordCompleter(completions, ignore_case=True)

def main():
    session = PromptSession(lexer=PygmentsLexer(JQLLexer), style=nord_style, completer=completer)
    while True:
        try:
            user_input = session.prompt('Enter JQL: ')
            print(f'You entered: {user_input}')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
    print('Goodbye!')

if __name__ == '__main__':
    main()
