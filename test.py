import unittest


class Yest(unittest.TestCase):
    def test_int(self):
        n1 = 5
        self.assertIsInstance(n1, int, "n1 should be an int")
        int("124124")
        a = 5
        self.assertIsInstance(a, int)

        assert isinstance(n1, int)


unittest.main()
