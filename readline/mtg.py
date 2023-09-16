#!/usr/bin/env python3
"""mtg.py
----------------
This module defines a command-line interface (CLI) application which allows
users to interact with a predefined list of completion options, specifically,
card names from the "Alara Reborn" set.

It leverages the `cmd` module to build the CLI and has tab-completion 
functionality for adding items from the predefined list of card names.
"""
import cmd

completions = [
    "Mage Slayer (Alara Reborn)",
    "Magefire Wings (Alara Reborn)",
    "Sages of the Anima (Alara Reborn)",
    "Sanctum Plowbeast (Alara Reborn)",
    "Sangrite Backlash (Alara Reborn)",
    "Sanity Gnawers (Alara Reborn)",
    "Sen Triplets (Alara Reborn)",
]


class mycmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)

    def do_quit(self, s):
        return True

    def do_add(self, s):
        pass

    def complete_add(self, text, line, begidx, endidx):
        mline = line.partition(" ")[2]
        offs = len(mline) - len(text)
        return [s[offs:] for s in completions if s.startswith(mline)]


if __name__ == "__main__":
    mycmd().cmdloop()
