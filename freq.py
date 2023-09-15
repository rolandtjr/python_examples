# Most frequently used words in a text

from collections import Counter
from string import ascii_letters


def top_3_words(text):
    letters = set([x for x in ascii_letters])
    letters.add("'")
    letters.add(" ")
    cleaned_text = "".join([x.lower() for x in text if x in letters])
    text_counter = Counter([word for word in cleaned_text.split()])
    del text_counter["'"]
    keys_to_delete = []
    for key in text_counter:
        new = Counter(key)
        if new["'"] > 1:
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del text_counter[key]
    return sorted(text_counter, key=text_counter.get, reverse=True)[:3]


print(top_3_words("a a a  b  c c  d d d d  e e e e e"))
print(top_3_words("  //wont won't won't "))
print(top_3_words("e e e e DDD ddd DdD: ddd ddd aa aA Aa, bb cc cC e e e"))
print(top_3_words("  '  "))
print(top_3_words("  '''  "))
