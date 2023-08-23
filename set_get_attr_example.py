
class Number:
    def __init__(self, number):
        self._number = number

    def power(self):
        self._number = self.number * self.number

    def another_func(self):
        print("In another function")

    def __setattr__(self, name, value):
        # print(name, type(name), value, type(value))
        super().__setattr__('_number', 0)
        try:
            if isinstance(value, int):
                super().__setattr__('_number', value)
            elif isinstance(value, str):
                super().__setattr__('_number', int(value))
        except ValueError:
            return

    def __getattribute__(self, name):
        options = ['power', 'another_func', '__class__']
        if name in options:
            return super().__getattribute__(name)
        else:
            return super().__getattribute__('_number')

    def __str__(self):
        return str(self._number)

    def __getattr__(self, name):
        return self._number
