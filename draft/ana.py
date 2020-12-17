"""
researchのanalyze.py
"""
import re


class Extract:
    def __init__(self, file):
        self.file = file

    def fact(self):
        with open(self.file) as f:
            data = f.read().replace('\n', '')
            regex = re.compile('\(property\s*(\(.*?\))\s*\)')
            mm = regex.search(data)
            fact_pro = mm.group(1)

            regex = re.compile('\(initial_facts\s*(\(.*?\))\s*\)')
            mm = regex.search(data)
            fact_ini = mm.group(1)
            # printではなくreturnさせてmainでprintさせるほうがいいっすね。byなかや
            '''
            print('property = ' + self.fact_pro)
            print('initial_facts = ' + self.fact_ini)
            '''
            return fact_pro, fact_ini

    def rule(self):
        x = []
        dict1 = {}
        joken = []
        jikko = []

        # ファイルを1行ずつリストに格納
        with open(self.file) as f:
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
            for i in x:
                for s in i:
                    if regex.search(s) is not None:
                        dict1[regex.search(s).group(
                            2)] = regex.search(s).group(1)

            for i in x:
                # '( ) = ?○○'が存在したら'= ?○○'を削除して条件のリストに加える
                joken.append([regex.search(s).group(1) if regex.search(
                    s) is not None else s for s in i])
            # print('joken = ', joken)
            # print('jikko = ', jikko)
            # print('dict1 = ', dict1)
            return joken, jikko, dict1


class Matching:
    def __init__(self, joken, jikko, fact_pro, fact_ini):
        self.joken = joken
        self.jikko = jikko
        self.fact_pro = fact_pro
        self.fact_ini = fact_ini

    def mat(self):
        dict2 = {}
        for i in range(len(self.joken)):
            for s in self.joken[i]:
                # 比較演算子が存在しなかった場合
                if re.search('==|!=|>|>=|<|<=', s) is None:  # ここもESP32だとうまく動かないみたい
                    # ?部分の抽出
                    while True:
                        regex = re.compile('\?\w+')
                        mm = regex.search(s)

                        # ?が存在したら
                        if mm is not None:
                            # ?の手前の:○○を抽出
                            # vregex = re.compile(':\w+(?=\s\?)')
                            # val = vregex.search(s)
                            val = re.search(':\w+\s+\?\w+', s).group(0)
                            # 辞書に仮置き(dict = {'?○○':':○○'})
                            # dict2[mm.group(0)] = val.group(0)
                            dict2[mm.group(0)] = re.search(
                                ':\w+', val).group(0)
                            # ?○○が除去
                            s = regex.sub('', s, 1)
                        else:
                            break
                    # スペースを正規表現に置き換え
                    s = re.sub('\s+', '.*', s)
                    regex = re.compile(s)
                    # propertyとマッチング
                    m_pro = regex.search(self.fact_pro)
                    # initial_factsとマッチング
                    m_ini = regex.search(self.fact_ini)

                    # ファクトとマッチしたら
                    if (m_ini or m_pro) is not None:
                        for key, value in dict2.items():
                            mm = re.search(':\w+', value)

                            if mm is not None:
                                # regex = re.compile(
                                #     '(?<=' + mm.group(0) + '\s)' + '\w+')
                                # mmm = regex.search(self.fact_ini)
                                mmm = re.search(mm.group(0), self.fact_ini)
                                regex = re.compile(
                                    '{0}{1}'.format(mm.group(0), '\s+\w+'))
                                regex2 = re.compile(
                                    '{0}{1}'.format(mm.group(0), '\s+'))
                                if mmm is not None:
                                    # dict2[key] = mmm.group(0)
                                    h = regex.search(self.fact_ini).group(0)
                                    h = regex2.sub('', h)
                                    dict2[key] = h
                                else:
                                    # dict2[key] = regex.search(
                                    # self.fact_pro).group(0)
                                    h = regex.search(self.fact_pro).group(0)
                                    h = regex2.sub('', h)
                                    dict2[key] = h
                    # ファクトとマッチしなかったとき
                    else:
                        print('false')
                        dict2.clear()
                        break

                # 比較演算子が存在した場合
                else:
                    regex = re.compile('\?\w+')
                    mm = regex.search(s)
                    # ?が存在した場合
                    if mm is not None:
                        s = regex.sub(dict2[mm.group(0)], s)
                    # ()の中味を抜き出す
                    # regex = re.compile('(?<=^\().*?(?=\)$)')
                    # s = regex.search(s)
                    # t = s.group(0).split(' ')  # スペースで区切る
                    s = re.sub('\(|\)', '', s)
                    t = s.split(' ')
                    if not eval('t[1]' + t[0] + 't[2]'):
                        print('false')
                        dict2.clear()
                        break

            else:  # 全てマッチしたとき
                # self.j_jikko(i)
                # return dict2
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
