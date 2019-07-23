#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import requests

url = 'http://127.0.0.1:8099'

def transfer(from_account, to_account, amount, symbol, memo):
    session = requests.Session()

    method = "transfer"
    params = [from_account, to_account, amount, symbol, memo, True]
    payload= {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

    headers = {'Content-type': 'application/json'}
    response = session.post(url, json=payload, headers=headers)
    #print('raw json response: {}'.format(response.json()))

def transfer_N(n):
    from_account = "1.2.15"     # official-account
    to_account = "init1"
    amount = "1"
    symbol = "COCOS"
    memo_base = "transfer test by python "
    for i in range(n):
        memo = memo_base + "number " + str(i)
        transfer(from_account , to_account, amount, symbol, memo)


def main():
    start_time = time.time()
    n = 1000
    transfer_N(n)
    end_time = time.time()
    duration = end_time - start_time
    per = duration / n
    print("duration: {d}, per: {p}".format(d = duration, p = per))

if __name__ == '__main__':
    main()
