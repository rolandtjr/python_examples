import readline

creatures = []

def add_creature():
    creature = input("Enter a creature name: ")
    creatures.append(creature)
    print(f"{creature} added to the list of creatures.")

def lookup_creature():
    def completer(text, state):
        options = [c for c in creatures if c.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None
    
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
    print("List of creatures:")
    for creature in creatures:
        print(f"- {creature}")
    
    while True:
        creature = input("Enter the name of a creature or press enter to return to the main menu: ")
        if not creature:
            break
        elif creature in creatures:
            print(f"{creature} found!")
        else:
            print(f"{creature} not found.")
    
    readline.set_completer(None)
    readline.parse_and_bind("tab: ")

def quit():
    print("Goodbye!")
    exit()

menu = {
    "1": add_creature,
    "2": lookup_creature,
    "3": quit
}

while True:
    print("Menu:")
    print("[1] Add Creature")
    print("[2] Lookup Creature")
    print("[3] Quit")
    
    choice = input("Enter your choice: ")
    action = menu.get(choice)
    if action:
        action()
    else:
        print(f"{choice} is not a valid option.")

