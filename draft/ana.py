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
            # printではなくreturnさせてmainでprintさせるほうがいいっすね。byなかや
            '''
            print('property = ' + self.fact_pro)
            print('initial_facts = ' + self.fact_ini)
            '''
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

            # micropythonで使えなかった
            # regex = re.compile('(?<=\)\s=\s)\?.+')
            # regex2 = re.compile('^\(.*\)(?=\s*=.*)')

            regex = re.compile('(^\(.*\))\s*=\s*(\?.+$)')

            """
            micropythonで使えた
            regex = re.compile('\s+=\s+\?.+$')
            regex2 = re.compile('^\(.*\)\s*=\s*')
            regex3 = re.compile('^\(.*\)')
            """

            # '( ) = ?○○が存在するかどうか
            # '( ) = ?○○'が存在したら'= ?○○'を削除して条件のリストに加える
            for i in range(len(joken)):
                var1.append({})
                for s in range(len(joken[i])):
                    if regex.search(joken[i][s]) is not None:
                        var1[i][regex.search(joken[i][s]).group(
                            2)] = [regex.search(joken[i][s]).group(1)]
                        joken[i][s] = regex.search(joken[i][s]).group(1)

                # joken.append([regex.search(s).group(1) if regex.search(
                #     s) is not None else s for s in i])
            # print('joken = ', joken)
            # print('jikko = ', jikko)
            # print('dict1 = ', dict1)
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
        print(len(self.joken))
        # for i in range(1, len(self.joken)):
        for i in range(len(self.joken)):
            var2.clear()
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
                                var2['?{}'.format(multi_var.group(0))].clear()
                                var2['?{}'.format(
                                    multi_var.group(0))].append(var)
                                break
                        else:
                            print('false')
                            break
                    else:
                        # スペース, (), ?を正規表現に置き換え
                        s = re.sub('\s+', '.*', s)
                        s = s.replace(')', '\)')
                        s = s.replace('(', '\(')
                        s = s.replace('?', '\?')
                        regex = re.compile(s)

                        match_fact_list = []
                        # propertyとマッチング
                        for pro in self.fact_pro:
                            # print('----')
                            # print(pro)
                            m_pro = regex.search(pro)

                            # m_pro = re.search(s, pro)
                            if m_pro is not None:
                                match_fact_list.append(pro)
                        # initial_factsとマッチング
                        for ini in self.fact_ini:
                            # print('-- -= == == ==--')
                            # print(ini)
                            m_ini = regex.search(ini)
                            # m_ini = re.search(s, ini)
                            if m_ini is not None:
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

    def j_jikko(self, i):
        for s in self.jikko[i]:
            # オブジェクトを抽出
            regex = re.compile('\w+')
            mm = regex.search(s)
            with open(mm.group(0) + '.py') as f:
                script = f.read()
                exec(script)


def main():
    pass


if __name__ == '__main__':
    main()
