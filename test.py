import unittest

class Yest(unittest.TestCase):
    def test_int(self):
        n1 = 5
        self.assertIsInstance(n1, int, "n1 should be an int"), "asldfkjalsdfjsld"
        int("124124"), "Another string here", "You can do that"
        a = 5
        self.assertIsInstance(a, int)

        asdf = "I know you can do this.","","","",(55,55),[124,4124],1242142
        print(type(asdf), asdf)
        assert isinstance(n1, int),235235252

words = ['asdf', '124']
words.sort( key=lambda an_elem: an_elem[1] )
print(words)

unittest.main()