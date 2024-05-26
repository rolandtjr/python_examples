from collections import defaultdict
def meeting(s):
    result = [tuple(word.split(":")) for word in s.split(";")]
    reorder = sorted([(tup[1].upper(),tup[0].upper()) for tup in result])
    names = defaultdict(lambda:[])
    for tup in reorder:
        names[tup[0]].append(tup)
    names_list = []
    for _, value in names.items():
        names_list.extend(sorted(value, key=lambda tup: tup[0]))
    get_string = [f"({tup[0]}, {tup[1]})" for tup in names_list]
    return "".join(get_string)

print(meeting("Alexis:Wahl;John:Bell;Victoria:Schwarz;Abba:Dorny;Grace:Meta;Ann:Arno;Madison:STAN;Alex:Cornwell;Lewis:Kern;Megan:Stan;Alex:Korn"))
