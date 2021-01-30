import micropython
import analyze as alz
import re
from machine import UART
import utime
import gc
import _thread
import dht
import machine


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
    WorkingMemory = [fact_ini.copy(), fact_pro.copy]

    global agent_name
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
    joken, jikko = ext.rule()

    print("joken: {0}, \njikko: {1}".format(
        joken, jikko))
    print('===============')
    gc.collect()
    print('Func run free: {} allocated: {}'.format(
        gc.mem_free(), gc.mem_alloc()))
    print('===============')

    mch = alz.Matching(joken, jikko, WorkingMemory)
    # マッチングの実行
    actions, vars = mch.mat()
    print('actionsは')
    print(actions)
    for s in actions:
        # オブジェクトを抽出
        content = extractOAVtoDict(s, vars)
        print('contentは')
        print(content)

        if content['obj'] == 'send':
            print(content[':content'])
            sendcontent = extractOAVtoDict(content[':content'], vars)
            print(sendcontent)
            '''
            坂本くん向けメモ
            print(sendcontent)
            ->
            いまは、{'obj': 'temp', 1: ':unit degree :value 27'}となっていて、
            これを、{'obj': 'temp', 1: ':unit':'degree', ':value' : '27'}としたい
 
            '''

            '''
            なかや用メモ
            pre_content = {}
            
            ◎TODO 順番をソートして、そして送信先とかに順番でkeyをリストで保存しておく, valueとかが1とか2みたいな数字ですむように
        

            sendcontent =extractOAVtoDict(content[':content'], vars)
            pre_sendcontent =extractOAVtoDict(pre_content[:content[':to']+content[':performative']], vars)

            ◎TODO content[':content']の要素数が異なっていれば、新規と判定してすべて送信する。
            ◎TODO pre_contentが空でも全部送信
            ◎TODO それ以外は、違っている部分だけ送る。
            
            i = 0
            for k in keyのリスト:
                if sendcontent[i] != pre_sendcontent[i] :
                    iとsendcontent[i]を送信
                i+=1

            #ここは毎回必ず実行。初回でも。
            pre_content[:content[':to']+content[':performative']] = content[':content']

            
            '''
            print('sendだよ')

            # exit()
            lpwa(uart, content, main_lock)
        if content['obj'] == 'control':
            # aaaa = "heel"
            # print(locals())
            ret = {}
            # exec('print(aaaa);d="unchi"', {'aaaa': aaaa}, ret)
            # exec('print(fact_ini)',{'fact_ini': fact_ini}, ret)
            # exec('print(aaaa)',locals(),locals())
            # print('controlだよ')
            # print(content['1'])
            # print(content[1][2:])
            # aaa = content[1][2:]
            # aaa ='print("Hello, world")'
            # print(fact_ini)
            # aaa = 'action_make( "(data {})".format(exec("d = dht.DHT11(machine.Pin(26));d.measure();d.temperature()",{"d":d})),fact_ini)'
            # aaa = 'action_make( "data"+ exec("d = dht.DHT11(machine.Pin(26));d.measure();d.temperature()"),fact_ini)'
            # tempval = {}

            '''
            aaaaa = "d = dht.DHT11(machine.Pin(26));d.measure();action_make('(data {})'.format(d.temperature()),fact_ini)"
            exec(aaaaa,{"dht":dht, "machine":machine,"action_make":action_make,"fact_ini": fact_ini})
            '''

            # action_make( "data"+ exec("d = dht.DHT11(machine.Pin(26));d.measure();d.temperature()",globals(),globals()),fact_ini)
            # print(type(content[1][2:]))
            # print(content[1][2:])
            # exec(aaaaa)
            '''
            Traceback (most recent call last):
            File "main.py", line 86, in main
            File "<string>", line 1, in <module>
            NameError: name 'fact_ini' isn't defined
            '''

            print(content[1][1:-1])
            '''
            content[1][2:]はaaaaaと同じはずなのに、通ってしまう
            '''
            # print(type(aaaaa))
            # print(content[1][2:])
            # print(aaaaa)
            # print(aaaaa == content[1][2:])
            '''
            falseになる
            '''

            exec(content[1][1:-1], {"dht": dht, "machine": machine,
                                    "action_make": action_make, "fact_ini": fact_ini}, ret)
            print(ret)

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

    # while True:
    #     utime.sleep(3)
    #     print('========mainだよ=======')


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
    uart.write(b'ECIO\r\n')
    print('ECIOは')
    status = read_status_block(main_lock)
    print(str(status, 'UTF-8'))
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
                    uart.write(b'TXDA {}{}{}'.format(k, v, '\r\n'))
                    # utime.sleep(3)
                    status = read_status_block(main_lock)
                    print(status)
                    if status == b'OK\r\n':
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
                        # utime.sleep(3)
                        status = read_status_block(main_lock)
                        print(str(status, 'UTF-8'))
                        if status == b'OK\r\n':
                            print('送信完了')
                            break
                        else:
                            print('送信失敗')


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
    # # obj == sendの場合
    # elif dict_ova['obj'] == 'send':
    #     regex2 = re.compile('^(:\w+)\s+([a-zA-Z0-9?_()"\'@ -]+)')
    #     while True:
    #         attr_val = regex2.search(s)
    #         if attr_val is not None:
    #             if attr_val.group(1) == ':content':
    #                 s = re.sub(':content\s+', '', s)
    #                 dict_ova[':content'] = s
    #                 break
    #             else:
    #                 s = regex2.sub('', s, 1)
    #                 dict_ova[attr_val.group(1)] = attr_val.group(2)
    #         else:
    #             break
    # それ以外の場合
    else:
        regex2 = re.compile('^(:\w+)\s+([a-zA-Z0-9?_()"\'.@ -]+)')
        while True:
            attr_val = regex2.search(s)
            if attr_val is not None:
                if attr_val.group(1) == ':content':
                    content_regex = re.compile(':content\s+(\(.*\))')
                    if content_regex.search(s) is None:
                        s = regex2.sub('', s, 1)
                        dict_ova[attr_val.group(1)] = attr_val.group(2)
                    else:
                        dict_ova[':content'] = content_regex.search(s).group(1)
                        s = content_regex.sub('', s, 1)
                else:
                    s = regex2.sub('', s, 1)
                    dict_ova[attr_val.group(1)] = attr_val.group(2)
            # bindの場合"?var"が後ろに来る
            elif regex.search(s) is not None:
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


def action_make(fact, WorkingMemory):
    print(fact)
    print(WorkingMemory)
    print('=====')
    WorkingMemory[0].append(fact)
    print(WorkingMemory)
    print('added')


def action_remove(fact, WorkingMemory):
    if fact in WorkingMemory[0]:
        WorkingMemory[0].remove(fact)
    else:
        print("can't remove {}".format(fact))


def aciton_modify(modi_varattr, new_value, WorkingMemory, vars):
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

    WorkingMemory[0].remove('({})'.format(ori_fact))
    WorkingMemory[0].append('({})'.format(new_fact))


def check(main_lock):
    global status_que
    global receive_que
    global agent_name
    uart = UART(2, 19200)  # 与えたボーレートで初期化
    uart.init(baudrate=19200, bits=8, parity=None,
              stop=1, rx=16, tx=17)  # 与えたパラメータで初期化

    # while True:
    #     utime.sleep(5)
    #     msg_bytes = uart.readline()
    #     print('checkでのreadは')
    #     print(msg_bytes)
    #     if msg_bytes is not None:
    #         if msg_bytes == b'OK\r\n' or msg_bytes == b'NG\r\n':
    #             with main_lock:
    #                 print('status queにappendしたよ')
    #                 status_que.append(msg_bytes)
    #         else:
    #             with main_lock:
    #                 receive_que.append(msg_bytes)
    #                 print('メッセージを受信しました')
    #                 message = receive_que.pop(0)
    #                 print(message)

    #                 print(agent_name)
    #                 if agent_name == 'Sample2':
    #                     print('agent nameはSample2')


if __name__ == '__main__':
    path = 'Sample2.dash'
    # agent_name = path[:-5]
    with open('Sample2.dash', encoding='utf-8') as f:
        data = f.readline()
        # regex = re.split('\(agent ', data)[1]
    agent_name = ''
    print('agent_name')
    print(agent_name)
    utime.sleep(1)

    receive_que = []
    status_que = []

    try:
        main_lock = _thread.allocate_lock()
        _thread.start_new_thread(check, (main_lock, ))
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
