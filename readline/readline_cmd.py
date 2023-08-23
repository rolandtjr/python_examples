import cmd
import os
import readline

# Set up history file
histfile = os.path.join(os.path.expanduser('~'), '.history')
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    open(histfile, 'wb').close()

# Define add and subtract functions
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

# Define command processor
class MyCmd(cmd.Cmd):
    prompt = '> '
    intro = 'Type help for commands'

    def do_exit(self, arg):
        """Exit the program"""
        return True

    def do_add(self, arg):
        """Add two numbers: add <num1> <num2>"""
        try:
            num1, num2 = map(float, arg.split())
        except ValueError:
            print('Invalid input')
            return
        print(add(num1, num2))

    def do_subtract(self, arg):
        """Subtract two numbers: subtract <num1> <num2>"""
        try:
            num1, num2 = map(float, arg.split())
        except ValueError:
            print('Invalid input')
            return
        print(subtract(num1, num2))

    def default(self, line):
        print('Invalid command')

    def emptyline(self):
        pass

# Run command processor
console = MyCmd()
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')
while True:
    try:
        line = input(console.prompt)
    except EOFError:
        break
    console.onecmd(line)

# Save history file
with open(histfile, 'w') as f:
    readline.write_history_file(histfile)

