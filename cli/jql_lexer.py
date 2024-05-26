from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from typing import Callable

class JQLLexer(Lexer):
    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        text = document.text
        tokens = []

        keywords = {
            "AND", "OR", "NOT", "IN", "ORDER BY", "ASC", "DESC",
            "IS", "NULL", "TRUE", "FALSE", "EMPTY"
        }
        operators = {
            "=", "!", ">", "<", ">=", "<=", "~", "!~", "!="
        }
        punctuations = {"(", ")", ",", ":", " "}

        pos = 0
        word = ''

        while pos < len(text):
            char = text[pos]

            if char.isalpha():
                word += char
            else:
                if word:
                    if word.upper() in keywords:
                        tokens.append(('class:keyword', word))
                    else:
                        tokens.append(('class:name', word))
                    word = ''

                if char in operators:
                    tokens.append(('class:operator', char))
                elif char in punctuations:
                    tokens.append(('class:punctuation', char))
                elif char.isspace():
                    tokens.append(('class:text', char))
                else:
                    tokens.append(('class:error', char))
            pos += 1

        if word:
            if word.upper() in keywords:
                tokens.append(('class:keyword', word))
            else:
                tokens.append(('class:name', word))

        return lambda i: tokens

# Example usage
from prompt_toolkit import PromptSession

custom_style = Style.from_dict({
    'keyword': '#ff0066 bold',
    'operator': '#00ff00',
    'name': '#0000ff',
    'punctuation': '#00ffff',
    'text': '#ffffff',
    'error': '#ff0000 bold',
})

session = PromptSession(lexer=JQLLexer(), style=custom_style)

text = session.prompt('Enter JQL: ')
print(f'You entered: {text}')
