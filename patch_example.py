#!/usr/bin/env python3

import unittest
from io import StringIO
from unittest.mock import patch
import print_things 


class TestPrintFunction(unittest.TestCase):
    def test_print_example(self):
        # The expected output of the print statement
        expected_output = "the world\n"

        # Using a context manager to temporarily replace sys.stdout with a StringIO object
        with patch("sys.stdout", new=StringIO()) as captured_output:
            print_things.print_the_world()  # Call the function that has the print statement

            # Assert the captured output is equal to the expected output
            self.assertEqual(captured_output.getvalue(), expected_output)


if __name__ == "__main__":
    unittest.main()
