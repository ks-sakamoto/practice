"""
researchのanalyze.py
"""
import re


class Extract:
    def __init__(self, file):
        self.file = file

    def fact(self):
        fact_pro = []
        fact_ini = []
        with open(self.file, encoding='utf-8') as f:
            data = f.read().replace('\n', '')
            regex = re.compile('\(property\s*(\(.*?\))\s*\)')
            text = regex.search(data).group(1)
            regex2 = re.compile('\(.*?\)')
            while True:
                pro_exist = regex2.search(text)
                if pro_exist is not None:
                    fact_pro.append(pro_exist.group(0))
                    text = regex2.sub('', text, 1)
                else:
                    break

            regex = re.compile('\(initial_facts\s*(\(.*?\))\s*\)')
            text = regex.search(data).group(1)
            while True:
                ini_exist = regex2.search(text)
                if ini_exist is not None:
                    fact_ini.append(ini_exist.group(0))
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
        x = []
        vars1 = []
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
                x.append(data[1:data.index('-->')])
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
            for i in range(len(x)):
                vars1.append({})
                for s in x[i]:
                    if regex.search(s) is not None:
                        vars1[i][regex.search(s).group(
                            2)] = [regex.search(s).group(1)]

            for i in x:
                # '( ) = ?○○'が存在したら'= ?○○'を削除して条件のリストに加える
                joken.append([regex.search(s).group(1) if regex.search(
                    s) is not None else s for s in i])
            # print('joken = ', joken)
            # print('jikko = ', jikko)
            # print('dict1 = ', dict1)
            return joken, jikko, vars1


class Matching:
    def __init__(self, joken, jikko, fact_pro, fact_ini, vars1):
        self.joken = joken
        self.jikko = jikko
        self.fact_pro = fact_pro
        self.fact_ini = fact_ini
        self.vars1 = vars1

    def mat(self):
        dict2 = {}
        for i in range(len(self.joken)):
            dict2.clear()
            for s in self.joken[i]:
                # 比較演算子が存在しなかった場合
                if re.search('==|!=|>|>=|<|<=', s) is None:
                    # ?部分の抽出
                    while True:
                        regex = re.compile('\?(\w+)')
                        var_exist = regex.search(s)

                        # ?が存在したら
                        if var_exist is not None:
                            if not var_exist.group(0) in dict2.keys():
                                # ?の手前の:○○を抽出
                                val = re.search(':\w+\s+\?\w+', s).group(0)
                                # 辞書に仮置き(dict = {'?○○':':○○'})
                                dict2[var_exist.group(0)] = re.search(
                                    ':\w+', val).group(0)
                                # ?○○が除去
                                s = regex.sub('', s, 1)
                            elif len(dict2[var_exist.group(0)]) == 1:
                                s = regex.sub(
                                    dict2[var_exist.group(0)][0], s, 1)
                            else:
                                s = regex.sub(':{}:'.format(
                                    var_exist.group(1)), s, 1)

                        else:
                            break

                    regex2 = re.compile(':(\w+):')
                    mm = regex2.search(s)
                    if mm is not None:
                        for var in dict2['?{}'.format(mm.group(1))]:
                            s_copy = regex2.sub(var, s, 1)

                            # スペースを正規表現に置き換え
                            s_copy = re.sub('\s+', '.*', s_copy)
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
                                dict2['?{}'.format(mm.group(1))].clear()
                                dict2['?{}'.format(mm.group(1))].append(var)
                                break
                        else:
                            print('false')
                            break
                    else:
                        # スペースを正規表現に置き換え
                        s = re.sub('\s+', '.*', s)
                        regex = re.compile(s)

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
                        # マッチしなければbreak
                        if not match_fact_list:
                            print('false')
                            break

                    # ファクトとマッチしたら
                    for key, value in dict2.items():
                        if type(value) is not list:
                            dict2[key] = []
                            regex = re.compile(
                                '{0}{1}'.format(value, '\s+[a-zA-Z0-9_"\'@-]+'))
                            regex2 = re.compile(
                                '{0}{1}'.format(value, '\s+'))

                            for match_fact in match_fact_list:
                                h = regex.search(match_fact)
                                if (h is not None) and \
                                        (regex2.sub('', h.group(0)) not in dict2[key]):
                                    dict2[key].append(
                                        regex2.sub('', h.group(0)))

                # 比較演算子が存在した場合
                else:
                    regex = re.compile('\?\w+')
                    var_exist = regex.search(s)
                    # ?が存在した場合
                    if var_exist is not None:
                        for var in dict2[var_exist.group(0)]:
                            s_copy = regex.sub(var, s)
                            # ()の中味を抜き出してスペースで区切る
                            s_copy = re.sub('\(|\)', '', s_copy)
                            t = s_copy.split(' ')
                            if not eval('t[1]' + t[0] + 't[2]'):
                                continue
                            else:
                                dict2[var_exist.group(0)].clear()
                                dict2[var_exist.group(0)].append(var)
                                break
                        else:
                            print('false')
                            break

            else:  # 全てマッチしたとき
                # self.j_jikko(i)
                # return dict2
                dict2.update(self.vars1[i])
                return self.jikko[i], dict2

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
