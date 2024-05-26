from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json


def ask_questions():
    questions = [
        {
            'type': 'input',
            'name': 'name',
            'message': 'What\'s your name',
        },
        {
            'type': 'input',
            'name': 'age',
            'message': 'How old are you',
        },
        {
            'type': 'input',
            'name': 'city',
            'message': 'Where do you live',
        },
    ]

    answers = prompt(questions)
    print_json(answers)
    print('Hello {name}, you are {age} years old and live in {city}'.format(**answers))
    print(f"Hello {answers['name']}, you are {answers['age']} years old and live in {answers['city']}")

def choose_option():
    questions = [
        {
            'type': 'list',
            'name': 'theme',
            'message': 'What do you want to do',
            'choices': [
                'Order a pizza',
                'Make a reservation',
                'Ask for opening hours',
                'Contact support',
                'Talk to the receptionist',
            ]
        }
    ]

    answers = prompt(questions)
    print_json(answers)

def editor_args():
    questions = [
        {
            'type': 'editor',
            'name': 'bio',
            'message': 'Please write a short bio of at least 3 lines',
            'validate': lambda text: len(text.split('\n')) >= 3 or 'Must be at least 3 lines.'
        }
    ]

    answers = prompt(questions)
    print_json(answers)


if __name__ == '__main__':
    #ask_questions()
    #choose_option()
    editor_args()
