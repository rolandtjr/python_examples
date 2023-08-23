import readline

# Set up history file
histfile = '.history'
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    open(histfile, 'wb').close()

# Define add and subtract functions
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

# Loop for user input
while True:
    # Read user input
    try:
        line = input('> ')
    except EOFError:
        break

    # Check for exit command
    if line == 'exit':
        break

    # Parse user input
    try:
        args = line.split()
        if len(args) != 3:
            raise ValueError
        num1 = float(args[0])
        num2 = float(args[2])
        op = args[1]
        if op not in ['+', '-']:
            raise ValueError
    except ValueError:
        print('Invalid input')
        continue

    # Perform operation
    if op == '+':
        result = add(num1, num2)
    else:
        result = subtract(num1, num2)

    # Print result and add command to history
    print(result)
    readline.add_history(line)

# Save history file
readline.write_history_file(histfile)
