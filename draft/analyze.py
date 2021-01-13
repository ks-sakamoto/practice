import re

import gc


class Extract:
    def __init__(self, file):
        self.file = file

    def fact(self):
        fact_pro = []
        fact_ini = []
        with open(self.file, encoding='utf-8') as f:
            data = f.read()
            regex = re.compile('\(property.*?\r\n\s*((\(.*?\)\r\n\s*)*)')
            text = regex.search(data).group(1)
            regex2 = re.compile('(\(.*?\))\r\n')
            while True:
                pro_exist = regex2.search(text)
                if pro_exist is not None:
                    fact_pro.append(pro_exist.group(1))
                    text = regex2.sub('', text, 1)
                else:
                    break

            regex = re.compile('\(initial_facts.*?\r\n\s*((\(.*?\)\r\n\s*)*)')
            text = regex.search(data).group(1)
            while True:
                ini_exist = regex2.search(text)
                if ini_exist is not None:
                    fact_ini.append(ini_exist.group(1))
                    text = regex2.sub('', text, 1)
                else:
                    break

            return fact_pro, fact_ini

    def rule(self):
        var1 = []
        joken = []
        jikko = []

        # ファイルを1行ずつリストに格納
        with open(self.file, encoding='utf-8') as f:
            data = [s.strip() for s in f.readlines()]

            # 空白行の要素を削除
            data = [i for i in data if i != '']
            del data[:(data.index('(knowledge') + 1)]

            while '-->' in data:
                # '-->'まで抽出
                joken.append(data[1:data.index('-->')])
                # '-->'以降')'まで抽出
                jikko.append(
                    data[(data.index('-->') + 1):data.index(')')])
                del data[:(data.index(')') + 1)]

            # regex = re.compile('(^\(.*\))\s*=\s*(\?.+$)')
            regex = re.compile('\s*=\s*(\?\w+$)')

            # '( ) = ?○○が存在するかどうか
            # '( ) = ?○○'が存在したら'= ?○○'を削除して条件のリストに加える
            for i in range(len(joken)):
                var1.append({})
                for s in range(len(joken[i])):
                    if regex.search(joken[i][s]) is not None:
                        var1[i][regex.search(joken[i][s]).group(
                            1)] = [regex.sub('', joken[i][s])]
                        joken[i][s] = regex.sub('', joken[i][s])

            return joken, jikko, var1


class Matching:
    def __init__(self, joken, jikko, fact_pro, fact_ini, var1):
        self.joken = joken
        self.jikko = jikko
        self.fact_pro = fact_pro
        self.fact_ini = fact_ini
        self.var1 = var1

    def mat(self):
        var2 = {}
        # for i in range(1, len(self.joken)):
        for i in range(len(self.joken)):
            var2.clear()
            print('iは')
            print(i)
            print('self.joken[i]は')
            print(self.joken[i])
            for s in self.joken[i]:
                # 比較演算子が存在しなかった場合
                if re.search('==|!=|>|>=|<|<=', s) is None:
                    # ?部分の抽出
                    while True:
                        regex = re.compile('\?(\w+)')
                        var_exist = regex.search(s)

                        # ?が存在したら
                        if var_exist is not None:
                            if not var_exist.group(0) in var2.keys():
                                # ?の手前の:○○を抽出
                                val = re.search('(:\w+)\s+\?\w+', s)
                                # 辞書に仮置き(dict = {'?○○':':○○'})
                                var2[var_exist.group(0)] = val.group(1)
                                # ?○○が除去
                                s = regex.sub('', s, 1)
                            elif len(var2[var_exist.group(0)]) == 1:
                                s = regex.sub(
                                    var2[var_exist.group(0)][0], s, 1)
                            else:
                                # マッチする変数が2つ以上あったとき
                                s = regex.sub(':{}:'.format(
                                    var_exist.group(1)), s, 1)

                        else:
                            print()
                            break

                    regex2 = re.compile(':(\w+):')
                    multi_var = regex2.search(s)
                    if multi_var is not None:
                        for var in var2['?{}'.format(multi_var.group(1))]:
                            s_copy = regex2.sub(var, s, 1)

                            # スペース, (), ?を正規表現に置き換え
                            s_copy = re.sub('\s+', '.*', s_copy)
                            s_copy = s_copy.replace(')', '\)')
                            s_copy = s_copy.replace('(', '\(')
                            s_copy = s_copy.replace('?', '\?')
                            regex = re.compile(s_copy)

                            match_fact_list = []
                            # propertyとマッチング
                            for pro in self.fact_pro:
                                m_pro = regex.search(pro)
                                if m_pro is not None:
                                    match_fact_list.append(pro)
                            # initial_factsとマッチング
                            for ini in self.fact_ini:
                                m_ini = regex.search(ini)
                                if m_ini is not None:
                                    match_fact_list.append(ini)
                            # マッチしたらマッチした変数を残して抜ける
                            if match_fact_list:
                                var2['?{}'.format(multi_var.group(1))] = [var]
                                break
                        else:
                            print('false')
                            break
                    else:
                        # スペース, (), ?を正規表現に置き換え
                        print(s)
                        # s = re.sub('\s+', '.*', s)
                        # s = s.replace(')', '\)')
                        # s = s.replace('(', '\(')
                        # s = s.replace('?', '\?')
                        # regex = re.compile(s)
                        s = re.sub('^\(|\)$', '', s)
                        s = s.split(':')
                        for p in range(len(s)):
                            s[p] = s[p].rstrip(' ')

                        match_fact_list = []
                        # propertyとマッチング
                        for pro in self.fact_pro:
                            # m_pro = regex.search(pro)
                            # if m_pro is not None:
                            #     match_fact_list.append(pro)
                            for p in s:
                                if p not in pro:
                                    break
                            else:
                                match_fact_list.append(pro)
                        # initial_factsとマッチング
                        for ini in self.fact_ini:
                            # m_ini = regex.search(ini)
                            # if m_ini is not None:
                            #     match_fact_list.append(ini)
                            for p in s:
                                if p not in ini:
                                    break
                            else:
                                match_fact_list.append(ini)
                        # マッチしなければbreak
                        if match_fact_list == []:
                            print('false')
                            break

                    # ファクトとマッチしたら
                    for key, value in var2.items():
                        print('いまここやで')
                        if type(value) is not list:
                            var2[key] = []
                            regex = re.compile(
                                '{0}{1}'.format(value, '\s+[a-zA-Z0-9?_"\'()@-]+'))
                            regex2 = re.compile(
                                '{0}{1}'.format(value, '\s+'))

                            for match_fact in match_fact_list:
                                # 先頭と末尾の()を削除
                                match_fact = re.sub('^\(|\)$', '', match_fact)
                                h = regex.search(match_fact)
                                if (h is not None) and \
                                        (regex2.sub('', h.group(0)) not in var2[key]):
                                    var2[key].append(
                                        regex2.sub('', h.group(0)))

                # 比較演算子が存在した場合
                else:
                    regex = re.compile('\?\w+')
                    var_exist = regex.search(s)
                    # ?が存在した場合
                    if var_exist is not None:
                        for var in var2[var_exist.group(0)]:
                            s_copy = regex.sub(var, s)
                            # ()の中味を抜き出してスペースで区切る
                            s_copy = re.sub('\(|\)', '', s_copy)
                            t = s_copy.split(' ')
                            print('"{}"{}"{}"'.format(t[1], t[0], t[2]))
                            # t[1]にはいっている文字列をいったんformatで取り出してからstring型に変換してやれば通った。そのままだとString型として認識できてなかった。
                            if not eval('"{}"{}"{}"'.format(t[1], t[0], t[2])):
                                # if not eval(t[1] + t[0] + 't[2]'):
                                continue
                            else:
                                var2[var_exist.group(0)].clear()
                                var2[var_exist.group(0)].append(var)
                                break
                        else:
                            print('false')
                            break

            else:  # 全てマッチしたとき
                # self.j_jikko(i)
                # return dict2
                var2.update(self.var1[i])
                return self.jikko[i], var2


def main():
    pass


if __name__ == '__main__':
    main()
