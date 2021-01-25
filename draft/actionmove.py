import re
import os

d = {0: '-->', 1: '==', 2: ' '}


def convert(file):
    count = 4
    end_index = 0
    word_regex = re.compile('[a-zA-Z_?@:"0-9/]+')
    # num_regex = re.compile('[0-9.]+')
    with open(file, encoding='utf-8') as f:
        ori_data = f.read()
        # 元から数字のものと置き換えたものの区別をつける
        # まず元から数字のものに目印をつける
        # while True:
        #     num = num_regex.search(ori_data[end_index:])
        #     if num is not None:
        #         temp_data = num_regex.sub('[{}]'.format(
        #             num.group(0)), ori_data[end_index:], 1)
        #         ori_data = ori_data.replace(ori_data[end_index:], temp_data)
        #         end_index = end_index + num.end() + 1
        #     else:
        #         break

        # 単語をインデックスに置き換える
        while True:
            word = word_regex.search(ori_data[end_index:])
            if word is not None:
                if word.group(0) in d.values():
                    for k, v in d.items():
                        if v == word.group(0):
                            temp_data = word_regex.sub(
                                str(k), ori_data[end_index:], 1)
                            ori_data = ori_data.replace(
                                ori_data[end_index:], temp_data)
                            end_index = end_index + word.start() + len(str(k))
                else:
                    d[count] = word.group(0)
                    temp_data = word_regex.sub(
                        str(count), ori_data[end_index:], 1)
                    ori_data = ori_data.replace(
                        ori_data[end_index:], temp_data)
                    end_index = end_index + word.start() + len(str(count))
                    count += 1
            else:
                break

        ori_data = ori_data.replace('-->', '0')
        ori_data = ori_data.replace('==', '1')

        # スペースが4つ以上連続してあった場合
        space_regex = re.compile('    +')
        while True:
            space = space_regex.search(ori_data)
            if space is not None:
                ori_data = space_regex.sub(
                    '2*{}'.format(len(space.group(0))), ori_data, 1)
            else:
                break

        print(d)

        with open('test.dash', 'wb') as fw:
            fw.write(ori_data.encode())


def restore(file, word_dict):
    end_index = 0

    with open(file, 'r') as f:
        ori_data = f.read()
        # まずスペースを変換
        space_regex = re.compile('2\*(\d)')
        while True:
            space = space_regex.search(ori_data)
            if space is not None:
                ori_data = space_regex.sub(
                    ' ' * int(space.group(1)), ori_data, 1)
            else:
                break
        # 次に辞書を参照しながら単語を復元
        num_regex = re.compile('\d+')
        while True:
            num = num_regex.search(ori_data[end_index:])
            if num is not None:
                temp_data = num_regex.sub(
                    word_dict[int(num.group(0))], ori_data[end_index:], 1)
                ori_data = ori_data.replace(ori_data[end_index:], temp_data)
                end_index = end_index + \
                    num.start() + len(word_dict[int(num.group(0))])
            else:
                break

        with open(file, 'w') as fw:
            fw.write(ori_data)


convert('Sample.dash')
print(os.path.getsize('test.dash'))
