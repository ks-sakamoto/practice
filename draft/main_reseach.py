import micropython
import analyze as alz
import re
from machine import UART
import utime
import gc
import _thread


def main(path):
    print('===============')
    gc.collect()
    print('Func run free: {} allocated: {}'.format(
        gc.mem_free(), gc.mem_alloc()))
    print('===============')

    uart = UART(2, 19200)  # 与えたボーレートで初期化
    uart.init(baudrate=19200, bits=8, parity=None,
              stop=1, rx=16, tx=17)  # 与えたパラメータで初期化

    ext = alz.Extract(path)
    # ファクトの抽出
    fact_pro, fact_ini = ext.fact()

    # micropython.mem_info()

    print("fact_pro: {0}, \nfact_ini: {1}".format(fact_pro, fact_ini))
    print('===============')
    gc.collect()
    print('Func run free: {} allocated: {}'.format(
        gc.mem_free(), gc.mem_alloc()))
    print('===============')

    # ルールの抽出
    joken, jikko, var1 = ext.rule()
    print("joken: {0}, \njikko: {1}, \nvar1: {2}".format(
        joken, jikko, var1))
    print('===============')
    gc.collect()
    print('Func run free: {} allocated: {}'.format(
        gc.mem_free(), gc.mem_alloc()))
    print('===============')

    mch = alz.Matching(joken, jikko, fact_pro, fact_ini, var1)
    # マッチングの実行
    actions, vars = mch.mat()
    print('actions: {0} \nvars: {1}'.format(actions, vars))
    for s in actions:
        # オブジェクトを抽出
        content = extractOVAtoDict(s, vars)
        if content['obj'] == 'send':
            # exit()
            lpwa(uart, content)

            '''
            アクション実行, ここでfact_iniが書き換わる可能性あり。
            sendをやって、できたら受信部分
            var2は変数のリスト

            content[“:obj:”] -> “send”
            content[“:performative”] -> “tell”
            content[“:content”] -> “(abc 変数v1の中身)”
            '''

    # print("hensyu: {}".format(hensyu))
    # print('===============')
    # gc.collect()
    # print('Func run free: {} allocated: {}'.format(
    #     gc.mem_free(), gc.mem_alloc()))
    # print('===============')
    # 送信部分 重いので一旦コメントアウト
    # lpwa(uart, joken, hensyu)

    print('=======終了========')
    gc.collect()
    print('Func run free: {} allocated: {}'.format(
        gc.mem_free(), gc.mem_alloc()))
    while True:
        utime.sleep(3)
        print('========mainだよ=======')


def lpwa(uart, content):

    print('----lpwa-----')
#     uart.write(b'RDID\r\n')
#     utime.sleep(3)
#     msg_bytes = uart.readline()
#     print(str(msg_bytes, 'UTF-8'))

#     uart.write(b'ECIO\r\n')
#     utime.sleep(2)
#     msg_bytes = uart.readline()
#     print(str(msg_bytes, 'UTF-8'))
# #     string = 'Hello World!\r\n'

#     for k, v in content.items():
#         if k == 'obj':
#             pass
#         else:
#             if len('{},{}'.format(k, v)) < 32:
#                 while(1):
#                     print('送信文字列 key:{}, value:{}'.format(k, v))
#                     uart.write(b'TXDA {}'.format(k, v, '\r\n'))
#                     utime.sleep(3)
#                     print(str(msg_bytes, 'UTF-8'))
#                     if msg_bytes == b'OK\r\n':
#                         print('送信完了')
#                         break
#                     else:
#                         print('送信失敗')
#             else:
#                 num = (len('{},{}'.format(k, v))//32) + 1
#                 for i in range(num):
#                     while(1):
#                         print('送信文字列: {}{}'.format(
#                             '{},{}'.format(k, v)[32*i:32*(i+1)], '\r\n'))
#                         uart.write(b'TXDA {}{}'.format(
#                             '{},{}'.format(k, v)[32*i:32*(i+1)], '\r\n'))
#                         utime.sleep(3)
#                         print(str(msg_bytes, 'UTF-8'))
#                         if msg_bytes == b'OK\r\n':
#                             print('送信完了')
#                             break
#                         else:
#                             print('送信失敗')


'''
    for strs in joken:
        for string in strs:
            if(len(string) > 32):
                num = (len(string)//32) + 1
                for i in range(num):
                    while(1):
                        print('送信文字列: {}{}'.format(
                            string[32*i:32*(i+1)], '\r\n'))
                        uart.write(b'TXDA {}{}'.format(
                            string[32*i:32*(i+1)], '\r\n'))
                        utime.sleep(3)
                        msg_bytes = uart.readline()
                        print(str(msg_bytes, 'UTF-8'))
                        if msg_bytes == b'OK\r\n':
                            print('送信完了')
                            break
                        else:
                            print('送信失敗')
            else:
                while(1):
                    print('送信文字列: {}{}'.format(string, '\r\n'))
                    uart.write(b'TXDA {}{}'.format(string, '\r\n'))
                    utime.sleep(3)
                    print(str(msg_bytes, 'UTF-8'))
                    if msg_bytes == b'OK\r\n':
                        print('送信完了')
                        break
                    else:
                        print('送信失敗')
    # hensyu = {'?from': 'Japannnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn',
    #           '?content': 'question'}
    for k, v in hensyu.items():
        if len('{},{}'.format(k, v)) < 32:
            while(1):
                print('送信文字列 key:{}, value:{}'.format(k, v))
                uart.write(b'TXDA {}'.format(k, v, '\r\n'))
                utime.sleep(3)
                print(str(msg_bytes, 'UTF-8'))
                if msg_bytes == b'OK\r\n':
                    print('送信完了')
                    break
                else:
                    print('送信失敗')
        else:
            num = (len('{},{}'.format(k, v))//32) + 1
            for i in range(num):
                while(1):
                    print('送信文字列: {}{}'.format(
                        '{},{}'.format(k, v)[32*i:32*(i+1)], '\r\n'))
                    uart.write(b'TXDA {}{}'.format(
                        '{},{}'.format(k, v)[32*i:32*(i+1)], '\r\n'))
                    utime.sleep(3)
                    print(str(msg_bytes, 'UTF-8'))
                    if msg_bytes == b'OK\r\n':
                        print('送信完了')
                        break
                    else:
                        print('送信失敗')
'''


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


def check(agent_name):
    # print('hello')
    # uart = UART(2, 19200)  # 与えたボーレートで初期化
    # uart.init(baudrate=19200, bits=8, parity=None,
    #           stop=1, rx=16, tx=17)  # 与えたパラメータで初期化
    # while True:
    #     utime.sleep(3)
    #     msg_bytes = uart.readline()
    #     print(msg_bytes)
    #     if msg_bytes is not None:
    #         print('受信しました')
    #        # if agent_name ==  :toで抜き出した名前と一致すれば。それでいいのか？

    #     # print(str(msg_bytes, 'UTF-8'))
    while True:
        utime.sleep(3)
        print(agent_name)


if __name__ == '__main__':
    path = 'Sample2.dash'
    agent_name = path[:-5]
    try:
        _thread.start_new_thread(check, (agent_name,))
        _thread.start_new_thread(main, (path,))

    except:
        print("Error: unable to start thread")


'''
joken = [ [ルール1の条件], [ルール2の条件], ..]
jikko = [ [      1の実行], [　　　2の実行], ..]

hensuは条件部の?○○とファクトの値の組を辞書に格納
send!やremove!はアクションsend, removeとして仮で出力
正規表現の先読み、後読みの部分はとりあえずそのまま
'''
