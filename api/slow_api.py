""" Module that mocks a slow API. """
from flask import Flask, request
from time import sleep
from random import randint

app = Flask(__name__)

@app.route('/slow')
def slow():
    sleep(randint(1, 5))
    return 'Slow response'

@app.route('/fast', methods=['GET', 'POST'])
def fast():
    """ If GET request is made to /fast, the server will return a fast response.
    If POST request is made to /fast, it will save the data to a file and return a fast response."""
    if request.method == 'POST':
        data = request.data.decode('utf-8')
        with open('data.txt', 'a') as file:
            file.write(f"{data}\n")
        return 'Data saved!'
    return 'Fast response'

if __name__ == '__main__':
    app.run(port=5597)

