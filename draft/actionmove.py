import re

d = {}


def action_move(file):
    count = 0
    word_regex = re.compile('[a-zA-Z_?]+')
    with open(file, encoding='utf-8') as f:
        data = f.read()
        while True:
            word = word_regex.search(data)
            if word is not None:
                if word.group(0) in d.values():
                    for k, v in d.items():
                        if v == word.group(0):
                            data = word_regex.sub(k, data, 1)
                else:
                    d['"{}"'.format(count)] = word.group(0)
                    data = word_regex.sub('"{}"'.format(count), data, 1)
                    count += 1
            else:
                break

        print(d)

        with open('test.dash', 'wb') as fw:
            fw.write(data.encode())
