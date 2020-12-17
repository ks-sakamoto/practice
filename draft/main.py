def main():
    import ana

    t = ana.Extract('Sample.dash')
    fact_pro, fact_ini = t.fact()
    joken, jikko, vars1 = t.rule()
    # print(fact_ini)
    # print(fact_pro)
    # print(joken)
    # print(jikko)
    # print(dict1)

    m = ana.Matching(joken, jikko, fact_pro, fact_ini, vars1)
    actions, vars2 = m.mat()
    # for c in range(len(vars)):
    #     vars2[c].update(vars1[c])
    print('actions = {}'.format(actions))
    print('vars = {}'.format(vars2))

    # for i in range(len(actions)):
    #     for s in actions[i]:
    #         print(extractOVAtoDict(s, vars[i]))
    for s in actions:
        print(extractOVAtoDict(s, vars2))


def extractOVAtoDict(s, vars):
    import re
    dict_ova = {}
    count = 1

    # 先頭と末尾の()を削除（邪魔だったので…）
    s = re.sub('^\(|\)$', '', s)

    # 変数が存在したらvarsから対応する値を代入
    regex = re.compile('\?\w+')
    while True:
        var_find = regex.search(s)
        if var_find is None:
            break
        else:
            s = regex.sub(vars[var_find.group(0)], s, 1)

    # objを抽出
    regex = re.compile('\w+')
    obj = regex.search(s)
    dict_ova['obj'] = obj.group(0)
    s = re.sub('\w+\s+', '', s, 1)

    # attr,valを抽出
    regex2 = re.compile('^(:\w+)\s+([a-zA-Z0-9_\(\) -]+)')
    while True:
        attr_val = regex2.search(s)
        if attr_val is not None:
            s = regex2.sub('', s, 1)
            dict_ova[attr_val.group(1)] = attr_val.group(2)
        elif re.search('^\(', s) is not None:
            dict_ova[count] = s
            count += 1
            break
        else:
            break
    return dict_ova


if __name__ == '__main__':
    main()
