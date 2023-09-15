#!/usr/bin/env python3
"""bcrypt_test.py
This module provides utilities for user authentication, including functions to
store hashed passwords, create new users, and authenticate existing users using
bcrypt for password hashing and a CSV file to store user data.
"""
import bcrypt
import csv


def store_password(password):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def create_user(username, password):
    hashed_password = store_password(password).decode("utf-8")

    with open("passwords_db.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_password])


def authenticate_user(username, password):
    try:
        with open("passwords_db.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == username:
                    hashed_password = row[1].encode("utf-8")
                    return check_password(password, hashed_password)
        return False
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    create_user("user1", "mysecurepassword")

    if authenticate_user("user1", "mysecurepassword"):
        print("Authentication successful")
    else:
        print("Authentication failed")
