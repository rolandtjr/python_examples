#!/usr/bin/env python3
"""rand_char.py
----------------
Generate and Print Random Unicode Characters

This module generates a string of random Unicode characters, specifically
avoiding the surrogate pair range (0xD800 to 0xDFFF). The generated string has
a default length of 5000 characters.

Usage:
    Run the script with an argument to specify the length of the string to be
    generated: `python script_name.py 5000`
"""
import random
from argparse import ArgumentParser


def generate_string(length):
    characters = ""
    try:
        characters = "".join(
            [
                chr(
                    random.choice(
                        [
                            i
                            for i in range(0x0, 0xD7FF + 1)
                            if i < 0xD800 or i > 0xDFFF
                        ]
                    )
                )
                for _ in range(length)
            ]
        )
    except UnicodeEncodeError as e:
        print(f"Error encoding character: {e}")

    return characters


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generate a string of random Unicode characters."
    )
    parser.add_argument(
        "length",
        type=int,
        default=5000,
        help="Length of the string to be generated.",
    )
    args = parser.parse_args()

    print(generate_string(args.length))
