import re


def main():
    import analyze as ana

    t = ana.Extract('Sample2.dash')
    agent_name = t.agentname()
    fact_pro, fact_ini = t.fact()
    joken, jikko, var1 = t.rule()
    print('agent_name = {}'.format(agent_name))
    print('initialfacts = {}'.format(fact_ini))
    print('property = {}'.format(fact_pro))
    print('joken = {}'.format(joken))
    print('jikko = {}'.format(jikko))

    m = ana.Matching(joken, jikko, fact_pro, fact_ini, var1)
    actions, vars = m.mat()
    print('actions = {}'.format(actions))
    print('vars = {}'.format(vars))

    # for i in range(len(actions)):
    #     for s in actions[i]:
    #         print(extractOVAtoDict(s, vars[i]))
    for s in actions:
        d = extractOAVtoDict(s, vars)
        print(d)
        #############################################
        if d['obj'] == 'make':
            action_make(d[1], fact_ini)
            print(fact_ini)
        elif d['obj'] == 'remove':
            action_remove(d[1], fact_ini)
            print(fact_ini)
        elif d['obj'] == 'modify':
            aciton_modify(d[1], d[2], fact_ini, vars)
            print(fact_ini)
        #############################################


def extractOAVtoDict(s, vars):
    dict_ova = {}
    count = 1

    # 先頭と末尾の()を削除（邪魔だったので…）
    s = re.sub('^\(|\)$', '', s)

    # objを抽出
    obj_regex = re.compile('\w+')
    obj = obj_regex.search(s)
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
    # obj == modifyの場合 ("?fact:var1 var1")
    if dict_ova['obj'] == 'modify':
        dict_ova[count] = re.search('\?\w+:\w+', s).group(0)
        s = re.sub('\?\w+:\w+', '', s, 1)
        count += 1
        dict_ova[count] = s
        count += 1
    # obj == sendの場合
    elif dict_ova['obj'] == 'send':
        regex2 = re.compile('^(:\w+)\s+([a-zA-Z0-9?_()"\'@ -]+)')
        while True:
            attr_val = regex2.search(s)
            if attr_val is not None:
                if attr_val.group(1) == ':content':
                    s = re.sub(':content\s+', '', s)
                    dict_ova[':content'] = s
                    break
                else:
                    s = regex2.sub('', s, 1)
                    dict_ova[attr_val.group(1)] = attr_val.group(2)
            else:
                break
    # それ以外の場合
    else:
        while True:
            # bindの場合"?var"が後ろに来る
            if regex.search(s) is not None:
                dict_ova[count] = regex.search(s).group(0)
                s = regex.sub('', s, 1)
                count += 1
            # "?var"が来ない場合->make, remove->後ろの要素が1つなので全て抜き出す
            elif s != '':
                dict_ova[count] = s
                break
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


def aciton_modify(modi_varattr, new_value, fact_ini, vars):
    # ?var:attr 変数名と対称の属性に分解
    var = re.search('\?\w+', modi_varattr).group(0)
    attr = re.search(':\w+', modi_varattr).group(0)

    # 変数名から対称のファクトを取ってきて両端の括弧を削除
    ori_fact = re.sub('^\(|\)$', '', vars[var][0])

    # ファクトの中に変数が存在したらvarsから対応する値を代入
    regex = re.compile('\?\w+')
    while True:
        var_find = regex.search(ori_fact)
        if var_find is None:
            break
        else:
            ori_fact = regex.sub(vars[var_find.group(0)][0], ori_fact, 1)

    # 属性をmodify対称のファクトから検索
    mm = re.search('{}\s+([a-zA-Z0-9_()"\'?@ -]+)'.format(attr), ori_fact)

    if mm is not None:
        # modify前の値のスペース, (), ?を正規表現に置き換え
        ori_value = re.sub('\s+', '.*', mm.group(1))
        ori_value = ori_value.replace(')', '\)')
        ori_value = ori_value.replace('(', '\(')
        ori_value = ori_value.replace('?', '\?')
        # 新しい値に置き換える
        new_fact = re.sub(ori_value, new_value, ori_fact)
    else:
        print("Can't modify")

    fact_ini.remove('({})'.format(ori_fact))
    fact_ini.append('({})'.format(new_fact))


if __name__ == '__main__':
    main()
