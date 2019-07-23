#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import requests
import threading

url = 'http://127.0.0.1:8049'

class DeriveThread(threading.Thread):
    def __init__(self, name, count):
        threading.Thread.__init__(self)
        self.name = name
        self.count = count

    def run(self):
        memo = str(self.name) + ' '
        #print('[run] {m} run start '.format(m = memo))
        transfer_N(self.count, memo)
        #print('[run] {m} run end '.format(m = memo))

def transfer(from_account, to_account, amount, symbol, memo):
    session = requests.Session()

    method = "transfer"
    params = [from_account, to_account, amount, symbol, memo, True]
    payload= {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

    headers = {'Content-type': 'application/json'}
    response = session.post(url, json=payload, headers=headers)
    #print('raw json response: {}'.format(response.json()))

def transfer_N(n, memo):
    from_account = "1.2.15"     # official-account
    to_account = "init1"
    amount = "1"
    symbol = "COCOS"
    memo_base = memo + ", transfer test by python "
    for i in range(n):
        memo = memo_base + "number " + str(i)
        transfer(from_account , to_account, amount, symbol, memo)

'''
thread_num: 开启的线程数
count: 每个线程的转账次数
'''
def multi_threads_transfer(thread_num, count):
    threads = []
    start_time = time.time()

    # 创建新线程
    for num in range(thread_num):
        name = 'thread-' + str(num)
        thread = DeriveThread(name, count)
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for t in threads:
        t.join()

    end_time = time.time()
    duration = end_time - start_time
    total =  thread_num * count
    print("transfer total number: {c}, total time: {d}, Unit time: {p}, Times per second: {m}" \
        .format(c = total, d = duration, p = duration/total, m = total/duration))

if __name__ == '__main__':
    multi_threads_transfer(10, 200)



