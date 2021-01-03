import re


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
    print('actions = {}'.format(actions))
    print('vars = {}'.format(vars2))

    # for i in range(len(actions)):
    #     for s in actions[i]:
    #         print(extractOVAtoDict(s, vars[i]))
    for s in actions:
        print(extractOVAtoDict(s, vars2))


def extractOVAtoDict(s, vars):
    dict_ova = {}
    count = 1

    # 先頭と末尾の()を削除（邪魔だったので…）
    s = re.sub('^\(|\)$', '', s)

    # objを抽出
    regex = re.compile('\w+')
    obj = regex.search(s)
    dict_ova['obj'] = obj.group(0)
    s = re.sub('\w+\s+', '', s, 1)

    # 変数が存在したらvarsから対応する値を代入
    regex = re.compile('\?\w+')
    while True:
        if dict_ova['obj'] == 'bind' or dict_ova['obj'] == 'modify':
            break
        var_find = regex.search(s)
        if var_find is None:
            break
        else:
            s = regex.sub(vars[var_find.group(0)][0], s, 1)

    # attr,valを抽出
    regex2 = re.compile('^(:\w+)\s+([a-zA-Z0-9?_()"\'@ -]+)')
    while True:
        attr_val = regex2.search(s)
        if attr_val is not None:
            s = regex2.sub('', s, 1)
            dict_ova[attr_val.group(1)] = attr_val.group(2)
        elif re.search('^\(', s) is not None:
            dict_ova[count] = re.search('^\(.+\)', s).group(0)
            s = re.sub('^\(.+\)', '', s, 1)
            count += 1
        # modifyの場合 ?var:attr を抽出
        elif re.search('\?\w+:\w+', s) is not None:
            dict_ova[count] = re.search('\?\w+:\w+', s).group(0)
            s = re.sub('\?\w+:\w+', '', s, 1)
            count += 1
        # modifyの場合 value を抽出
        elif re.search('\(.+\)', s) is not None:
            dict_ova[count] = re.search('\(.+\)', s).group(0)
            s = re.sub('\(.+\)', '', s, 1)
            count += 1
        else:
            break
    return dict_ova


def action_make(fact, fact_ini):
    fact_ini.append(fact)


def action_remove(fact, fact_ini):
    if fact in fact_ini:
        fact_ini.remove(fact)
    else:
        print("can't remove {}".format(fact))


def aciton_modify(modi_varattr, fact_ini, value, vars):
    var = re.search('\?\w+', modi_varattr).group(0)
    attr = re.search(':\w+', modi_varattr).group(0)

    # 両端の括弧を削除
    fact = re.sub('^\(|\)$', '', vars[var][0])

    mm = re.search('{}\s+([a-zA-Z0-9_()"\'?@ -]+)'.format(attr), fact)

    if mm is not None:
        # 元の値のスペース, (), ?を正規表現に置き換え
        ori_value = re.sub('\s+', '.*', mm.group(1))
        ori_value = re.sub('\)', '\)', ori_value)
        ori_value = re.sub('\(', '\(', ori_value)
        ori_value = re.sub('\?', '\?', ori_value)
        # 元の値を新しい値に置き換える
        new_fact = re.sub(ori_value, value, vars[var][0])
    else:
        print("Can't modify")

    fact_ini.remove(vars[var][0])
    fact_ini.append(new_fact)


if __name__ == '__main__':
    main()
