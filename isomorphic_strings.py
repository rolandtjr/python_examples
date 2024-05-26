#!/usr/bin/env python3
from collections import Counter

def isIsometric(s, t):
    if len(s) != len(t):
        return False

    s_dict = {}
    t_dict = {}

    for index in range(len(s)):
        if s[index] not in s_dict:
            s_dict[s[index]] = t[index]
        if t[index] not in t_dict:
            t_dict[t[index]] = s[index]

        if s_dict[s[index]] != t[index] or t_dict[t[index]] != s[index]:
            return False
    return True


if __name__ == '__main__':
    s = 'egg'
    t = 'add'
    print(isIsometric(s, t)) # True

    s = 'foo'
    t = 'bar'
    print(isIsometric(s, t)) # False

    s = 'paper'
    t = 'title'
    print(isIsometric(s, t)) # True

    s = 'ab'
    t = 'aa'
    print(isIsometric(s, t)) # False

    s = 'bbbaaaba'
    t = 'aaabbbba'
    print(isIsometric(s, t)) # False
