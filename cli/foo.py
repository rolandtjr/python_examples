from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion


class Completer(Completer):
    def get_completions(self, document, complete_event):
        yield Completion('foo', start_position=0, style='bg:ansiyellow fg:ansiblack')
        yield Completion('bar', start_position=0, style='underline')

class Foo:
    def __init__(self):
        self.session = PromptSession()

    def run(self):
        print(self.multi_line_prompt())


    def multi_line_prompt(self):
        """ Prompt the user for input, allowing multiple lines with default text. """
        return self.session.prompt('Give me some input: ', multiline=True, default='Hello\nWorld\n', completer=Completer())

def main():
    foo = Foo()
    foo.run()

if __name__ == '__main__':
    main()
