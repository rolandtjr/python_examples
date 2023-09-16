# /usr/bin/env python3
"""set_get_attr_example.py
-----------------------

This module contains a class named `Number` which implements special attribute
access methods to demonstrate custom attribute setting and getting behaviors
in a Python class.

Here is a summary of its functionality and methods:

- `__init__(self, number)`: Initializes a new instance with a `number` parameter. 
- `power(self)`: Squares the current value of the `_number` attribute. It utilizes
  `self.number` to access the `_number` attribute, which works correctly due to
  the overridden `__getattribute__` method.
- `another_func(self)`: Prints a message when invoked.
- `__str__(self)`: Returns a string representation of the `_number` attribute.
  
The class also overrides special methods (`__setattr__`, `__getattribute__`,
`__getattr__`) to define custom behaviors for setting, getting, and accessing
non-existent attributes, respectively.

Usage:
  If run as the main program, an instance of `Number` is created with an initial
  value of 5. The script then performs various operations to demonstrate the
  custom attribute access behaviors.

Note:
  The `__getattribute__` method in the `Number` class is implemented such that if
  an attribute other than the ones listed in the `options` list is accessed, the
  `_number` attribute value is returned. This is demonstrated in the script where
  `number.num` and `number.number` (which are non-existing attributes) are accessed,
  but the `_number` value is printed instead of raising an AttributeError.
"""


class Number:
    def __init__(self, number):
        self._number = number

    def power(self):
        self._number = self.number * self.number

    def another_func(self):
        print("In another function")

    def __setattr__(self, name, value):
        # print(name, type(name), value, type(value))
        super().__setattr__("_number", 0)
        try:
            if isinstance(value, int):
                super().__setattr__("_number", value)
            elif isinstance(value, str):
                super().__setattr__("_number", int(value))
        except ValueError:
            return

    def __getattribute__(self, name):
        options = ["power", "another_func", "__class__"]
        if name in options:
            return super().__getattribute__(name)
        else:
            return super().__getattribute__("_number")

    def __str__(self):
        return str(self._number)

    def __getattr__(self, name):
        return self._number


if __name__ == "__main__":
    number = Number(5)
    print(number.num)
    print(number.number)
    number.power()
    print(number.num)
    number.another_func()
