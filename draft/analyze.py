import re

import gc


class Extract:
    def __init__(self, file):
        self.file = file

    def agentname(self):
        with open(self.file, encoding='utf=8') as f:
            agent_name = re.search('\(agent\s*(\w+)', f.read()).group(1)
        return agent_name

    def fact(self):
        fact_pro = []
        fact_ini = []
        with open(self.file, encoding='utf-8') as f:
            data = f.read()
            regex = re.compile('\(property.*?\n\s*((\(.*?\)\n\s*)*)')
            text = regex.search(data).group(1)
            regex2 = re.compile('(\(.*?\))\n')
            while True:
                pro_exist = regex2.search(text)
                if pro_exist is not None:
                    fact_pro.append(pro_exist.group(1))
                    text = regex2.sub('', text, 1)
                else:
                    break

            regex = re.compile('\(initial_facts.*?\n\s*((\(.*?\)\n\s*)*)')
            text = regex.search(data).group(1)
            while True:
                ini_exist = regex2.search(text)
                if ini_exist is not None:
                    fact_ini.append(ini_exist.group(1))
                    text = regex2.sub('', text, 1)
                else:
                    break
            # printではなくreturnさせてmainでprintさせるほうがいいっすね。byなかや
            return fact_pro, fact_ini

    def rule(self):
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

            # regex = re.compile('(^\(.*\))\s*=\s*(\?.+$)')

            """
            micropythonで使えた
            regex = re.compile('\s+=\s+\?.+$')
            regex2 = re.compile('^\(.*\)\s*=\s*')
            regex3 = re.compile('^\(.*\)')
            """

            return joken, jikko


class Matching:
    def __init__(self, joken, jikko, workingmemory):
        self.joken = joken
        self.jikko = jikko
        self.workingmemory = workingmemory

    def mat(self):
        vars = {}
        # regex = re.compile('\s*=\s*(\?\w+$)')
        # # '( ) = ?○○が存在するかどうか
        # # '( ) = ?○○'が存在したら'= ?○○'を削除して条件のリストに加える
        # for i in range(len(self.joken)):
        #     vars.append({})
        #     for s in range(len(self.joken[i])):
        #         if regex.search(self.joken[i][s]) is not None:
        #             vars[i][regex.search(self.joken[i][s]).group(1)] = [
        #                 regex.sub('', self.joken[i][s])]
        #             self.joken[i][s] = regex.sub('', self.joken[i][s])
        for i in range(len(self.joken)):
            vars.clear()
            for s in self.joken[i]:
                regex = re.compile('\s*=\s*(\?\w+$)')
                if regex.search(s) is not None:
                    vars[regex.search(s).group(1)] = [regex.sub('', s)]
                    s = regex.sub('', s)
                    print(s)
                # 比較演算子が存在しなかった場合
                if re.search('==|!=|>|>=|<|<=', s) is None:
                    # ?部分の抽出
                    while True:
                        regex = re.compile('\?(\w+)')
                        var_exist = regex.search(s)

                        # ?が存在したら
                        if var_exist is not None:
                            if not var_exist.group(0) in vars.keys():
                                # ?の手前の:○○を抽出
                                val = re.search('(:\w+)\s+\?\w+', s)
                                # 辞書に仮置き(dict = {'?○○':':○○'})
                                vars[var_exist.group(0)] = val.group(1)
                                # ?○○が除去
                                s = regex.sub('', s, 1)
                            elif len(vars[var_exist.group(0)]) == 1:
                                s = regex.sub(
                                    vars[var_exist.group(0)][0], s, 1)
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
                        for var in vars['?{}'.format(multi_var.group(1))]:
                            s_copy = regex2.sub(var, s, 1)

                            # 両端の（）を削除
                            s_copy = re.sub('^\(|\)$', '', s_copy)
                            # 条件部を属性，属性値のペアに分解
                            attr_val_pairs = s_copy.split(':')
                            for p in range(len(attr_val_pairs)):
                                attr_val_pairs[p] = attr_val_pairs[p].rstrip(
                                    ' ')

                            match_fact_list = []
                            # propertyとマッチング
                            for pro in self.workingmemory[1]:
                                # m_pro = regex.search(pro)
                                # if m_pro is not None:
                                #     match_fact_list.append(pro)
                                for pair in attr_val_pairs:
                                    if pair not in pro:
                                        break
                                else:
                                    match_fact_list.append(pro)
                            # initial_factsとマッチング
                            for ini in self.workingmemory[0]:
                                # m_ini = regex.search(ini)
                                # if m_ini is not None:
                                #     match_fact_list.append(ini)
                                for pair in attr_val_pairs:
                                    if pair not in ini:
                                        break
                                else:
                                    match_fact_list.append(ini)
                            # マッチしたらマッチした変数を残して抜ける
                            if match_fact_list:
                                vars['?{}'.format(multi_var.group(1))] = [var]
                                break
                        else:
                            print('false')
                            break
                    else:
                        # 両端の（）を削除
                        s = re.sub('^\(|\)$', '', s)
                        # 条件部を属性，属性値のペアに分解
                        attr_val_pairs = s.split(':')
                        for p in range(len(attr_val_pairs)):
                            attr_val_pairs[p] = attr_val_pairs[p].rstrip(' ')

                        match_fact_list = []
                        # propertyとマッチング
                        # proの中に属性，属性値のペアが存在しているか確認
                        # 条件部の全ての属性，属性値のペアが存在していればマッチ
                        for pro in self.workingmemory[1]:
                            # m_pro = regex.search(pro)
                            # if m_pro is not None:
                            #     match_fact_list.append(pro)
                            for pair in attr_val_pairs:
                                if pair not in pro:
                                    break
                            else:
                                match_fact_list.append(pro)
                        # initial_factsとマッチング(propertyと同様)
                        for ini in self.workingmemory[0]:
                            # m_ini = regex.search(ini)
                            # if m_ini is not None:
                            #     match_fact_list.append(ini)
                            for pair in attr_val_pairs:
                                if pair not in ini:
                                    break
                            else:
                                match_fact_list.append(ini)
                        # マッチしなければbreak
                        if match_fact_list == []:
                            print('false')
                            break

                    # ファクトとマッチしたら
                    for key, value in vars.items():
                        if type(value) is not list:
                            vars[key] = []
                            regex = re.compile(
                                '{0}{1}'.format(value, '\s+[a-zA-Z0-9?_"\'()@-]+'))
                            regex2 = re.compile(
                                '{0}{1}'.format(value, '\s+'))

                            for match_fact in match_fact_list:
                                # 先頭と末尾の()を削除
                                match_fact = re.sub('^\(|\)$', '', match_fact)
                                h = regex.search(match_fact)
                                if (h is not None) and \
                                        (regex2.sub('', h.group(0)) not in vars[key]):
                                    vars[key].append(
                                        regex2.sub('', h.group(0)))

                # 比較演算子が存在した場合
                else:
                    regex = re.compile('\?\w+')
                    var_exist = regex.search(s)
                    # ?が存在した場合
                    if var_exist is not None:
                        for var in vars[var_exist.group(0)]:
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
                                vars[var_exist.group(0)].clear()
                                vars[var_exist.group(0)].append(var)
                                break
                        else:
                            print('false')
                            break

            else:  # 全てマッチしたとき
                yield self.jikko[i], vars


def main():
    pass


if __name__ == '__main__':
    main()
