import micropython
import analyze as alz
import re
from machine import UART
import utime
import gc
import _thread


def main(path, main_lock):
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
    agent_name = ext.agentname()

    # micropython.mem_info()

    print("fact_pro: {0}, \nfact_ini: {1}\nagent_name: {2}".format(
        fact_pro, fact_ini, agent_name))
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
    for s in actions:
        # オブジェクトを抽出
        content = extractOVAtoDict(s, vars)
        if content['obj'] == 'send':
            # exit()
            lpwa(uart, content, main_lock)

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


def read_status_block(main_lock):
    while(1):
        global status_que
        with main_lock:
            if len(status_que) > 0:
                return status_que.pop(0)
            else:
                pass

        utime.sleep(3)


def lpwa(uart, content, main_lock):
    global status_que
    global receive_que

    print('---------')
    # utime.sleep(3)
    # uart.write(b'RDID\r\n')
    # print('RDIDは')
    # status = read_status_block()
    # print(status)

    print('---------')
    # uart.write(b'ECIO\r\n')
    # print('ECIOは')
    # status = read_status_block(main_lock)
    # print(str(status, 'UTF-8'))
    print(content)
    for k, v in content.items():
        utime.sleep(3)
        print('いまは key:{}, value:{}'.format(k, v))
        if k == 'obj':
            pass
        else:
            if len('{},{}'.format(k, v)) < 32:
                while(1):
                    print('送信文字列 key:{}, value:{}'.format(k, v))
                    break
                    # uart.write(b'TXDA {}{}{}'.format(k, v, '\r\n'))
                    # # utime.sleep(3)
                    # status = read_status_block(main_lock)
                    # print(status)
                    # if status == b'OK\r\n':
                    #     print('送信完了')
                    #     break
                    # else:
                    #     print('送信失敗')
            else:
                num = (len('{},{}'.format(k, v))//32) + 1
                for i in range(num):
                    while(1):
                        print('送信文字列: {}{}'.format(
                            '{},{}'.format(k, v)[32*i:32*(i+1)], '\r\n'))
                        break
                        # uart.write(b'TXDA {}{}'.format(
                        #     '{},{}'.format(k, v)[32*i:32*(i+1)], '\r\n'))
                        # # utime.sleep(3)
                        # status = read_status_block(main_lock)
                        # print(str(status, 'UTF-8'))
                        # if status == b'OK\r\n':
                        #     print('送信完了')
                        #     break
                        # else:
                        #     print('送信失敗')


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
    # obj == modifyの場合 ("?fact:var1 var1")
    if dict_ova['obj'] == 'modify':
        dict_ova[count] = re.search('\?\w+:\w+', s).group(0)
        s = re.sub('\?\w+:\w+', '', s, 1)
        count += 1
        dict_ova[count] = s
    # modify以外の場合
    else:
        regex2 = re.compile('^(:\w+)\s+([a-zA-Z0-9?_()"\'@ -]+)')
        while True:
            attr_val = regex2.search(s)
            if attr_val is not None:
                s = regex2.sub('', s, 1)
                dict_ova[attr_val.group(1)] = attr_val.group(2)
            # bindの場合"?var"が後ろに来る
            elif re.search('\?\w+', s) is not None:
                dict_ova[count] = re.search('\?\w+', s).group(0)
                s = re.sub('\?\w+', '', s, 1)
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
        new_fact = ''
        print("Can't modify")

    fact_ini.remove('({})'.format(ori_fact))
    fact_ini.append('({})'.format(new_fact))


def check(agent_name, main_lock):
    global status_que
    global receive_que

    # uart = UART(2, 19200)  # 与えたボーレートで初期化
    # uart.init(baudrate=19200, bits=8, parity=None,
    #           stop=1, rx=16, tx=17)  # 与えたパラメータで初期化

    while True:
        utime.sleep(5)
        print('===check===')
        # msg_bytes = uart.readline()
        # print('checkでのreadは')
        # print(msg_bytes)
        # if msg_bytes is not None:
        #     if msg_bytes == b'OK\r\n' or msg_bytes == b'NG\r\n':
        #         with main_lock:
        #             print('status queにappendしたよ')
        #             status_que.append(msg_bytes)
        #     else:
        #         with main_lock:
        #             receive_que.append(msg_bytes)
        #             print('メッセージを受信しました')
        #             message = receive_que.pop(0)
        #             print(message)

        #             print(agent_name)
        #             if agent_name == 'Sample2':
        #                 print('agent nameはSample2')


if __name__ == '__main__':
    path = 'Sample2.dash'
    # agent_name = path[:-5]
    with open('Sample2.dash', encoding='utf-8') as f:
        data = f.readline()
        # regex = re.split('\(agent ', data)[1]
    agent_name = data[7:-1]
    print('agent_name')
    print(agent_name)
    utime.sleep(1)

    receive_que = []
    status_que = []

    try:
        main_lock = _thread.allocate_lock()
        _thread.start_new_thread(check, (agent_name, main_lock, ))
        # _thread.stack_size(10000)
        _thread.start_new_thread(main, (path, main_lock,))
    except Exception as e:
        print(e)


'''
joken = [ [ルール1の条件], [ルール2の条件], ..]
jikko = [ [      1の実行], [　　　2の実行], ..]

hensuは条件部の?○○とファクトの値の組を辞書に格納
send!やremove!はアクションsend, removeとして仮で出力
正規表現の先読み、後読みの部分はとりあえずそのまま
'''
