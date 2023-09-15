#!/usr/bin/env python3
"""bcrypt_test.py
This module provides utilities for user authentication, including functions to
store hashed passwords, create new users, and authenticate existing users using
bcrypt for password hashing and a sqlite database to store user data.
"""
import bcrypt
import sqlite3


def initialize_database():
    conn = sqlite3.connect("passwords_db.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, hashed_password TEXT)"""
    )
    conn.commit()
    conn.close()


def store_password(password):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def create_user(username, password):
    hashed_password = store_password(password).decode("utf-8")

    conn = sqlite3.connect("passwords_db.db")
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print("Username already exists")
    finally:
        conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect("passwords_db.db")
    c = conn.cursor()

    c.execute(
        "SELECT hashed_password FROM users WHERE username = ?", (username,)
    )
    row = c.fetchone()
    conn.close()

    if row:
        hashed_password = row[0].encode("utf-8")
        return check_password(password, hashed_password)
    else:
        return False


if __name__ == "__main__":
    initialize_database()
    create_user("user1", "mysecurepassword")

    if authenticate_user("user1", "mysecurepassword"):
        print("Authentication successful")
    else:
        print("Authentication failed")
