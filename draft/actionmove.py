import re

d = {}


def action_move(file):
    count = 0
    end_index = 0
    word_regex = re.compile('[a-zA-Z?":][a-zA-Z_?@:"]+')
    num_regex = re.compile('[0-9.]+')
    with open(file, encoding='utf-8') as f:
        ori_data = f.read()
        # 元から数字のものと置き換えたものの区別をつける
        # まず元から数字のものに目印をつける
        while True:
            num = num_regex.search(ori_data[end_index:])
            if num is not None:
                temp_data = num_regex.sub('[{}]'.format(
                    num.group(0)), ori_data[end_index:], 1)
                ori_data = ori_data.replace(ori_data[end_index:], temp_data)
                end_index = end_index + num.end() + 1
            else:
                break

        # 単語をインデックスに置き換える
        while True:
            word = word_regex.search(ori_data)
            if word is not None:
                if word.group(0) in d.values():
                    for k, v in d.items():
                        if v == word.group(0):
                            ori_data = word_regex.sub(k, ori_data, 1)
                else:
                    d[str(count)] = word.group(0)
                    ori_data = word_regex.sub(str(count), ori_data, 1)
                    count += 1
            else:
                break

        print(d)

        with open('test.dash', 'wb') as fw:
            fw.write(ori_data.encode())
