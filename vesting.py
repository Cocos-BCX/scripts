# -*- coding:utf-8 -*-

import os
import re
import json
import logging
import requests
import datetime as dt
from time import sleep
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

from PythonMiddleware.graphene import Graphene
from PythonMiddleware.instance import set_shared_graphene_instance
from pprint import pprint
from PythonMiddleware.account import Account
from PythonMiddleware.vesting import Vesting
from PythonMiddleware.asset import Asset
from PythonMiddleware.storage import configStorage as config

class SubFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

class Logging(object):
    def __init__(self, log_dir='./logs', log_name='server', console=True):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        formatter = SubFormatter(fmt='%(asctime)s [%(name)s] [%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')

        # file handler
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = log_dir + '/' + log_name
        fh = TimedRotatingFileHandler(filename=log_file, when="H", interval=1, backupCount=3*24)
        fh.suffix = "%Y-%m-%d_%H-%M.log"
        fh.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # console handler
        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def getLogger(self):
        return self.logger

logger = Logging().getLogger()

headers = {"content-type": "application/json"}
chain_url = "http://127.0.0.1:8049"
node_address = "ws://127.0.0.1:8049"

gph = Graphene(node=node_address, blocking=True)
set_shared_graphene_instance(gph)

def request_post(req_data, is_assert=True, response_log=True, url=chain_url):
    response = json.loads(requests.post(url, data = json.dumps(req_data), headers = headers).text)
    print('>> {} {}'.format(req_data['method'], req_data['params']))
    if response_log:
        print("{}\n".format(response))
    if is_assert:
        assert 'error' not in response
    return response

#########
wallet_password = "123456"
private_key = "5J2SChqa9QxrCkdMor9VC2k9NT4R4ctRrJA6odQCPkb3yL98vxo"
public_key = "COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx"
default_account = "nicotest"
############

def init_wallet():
    try:
        if not gph.wallet.created():
            gph.newWallet(wallet_password)
        logger.info("wallet create status: {}".format(gph.wallet.created()))

        if gph.wallet.locked():
            gph.wallet.unlock(wallet_password)
        logger.info("wallet lock status: {}".format(gph.wallet.locked()))

        if gph.wallet.getPrivateKeyForPublicKey(public_key) is None:
            logger.info("import private key into wallet. public key: {}".format(public_key))
            gph.wallet.addPrivateKey(private_key)

        logger.info("account id: {}, public key: {}".format(
            gph.wallet.getAccountFromPublicKey(public_key), public_key))

        config["default_prefix"] = gph.rpc.chain_params["prefix"]
        config["default_account"] = default_account
    except Exception as e:
        print(repr(e))

def get_vesting_balances(account_id):
    req_data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": [0, "get_vesting_balances", [account_id]],
        "id":1
    }
    return request_post(req_data, is_assert=False, url=chain_url)['result']

def allowed_withdraw(vesting_id):
    vesting_object = Vesting(vesting_id)
    return vesting_object.claimable

def account_vesting(account_id):
    vesting_objects = get_vesting_balances(account_id)
    for vesting_object in vesting_objects:
        vesting_object_id = vesting_object["id"]
        print(vesting_object_id)
        # def vesting_balance_withdraw(self, vesting_id, amount=None, asset=None, account=None):
        # 这里可以根据需要添加要提取的amount，asset，account
        gph.vesting_balance_withdraw(vesting_object_id, account=account_id)

def account_vesting_by_sdk(account_id):
    vesting_objects = gph.get_vesting_balances(account_id)
    for vesting_object in vesting_objects:
        vesting_object_id = vesting_object["id"]
        print(vesting_object_id)
        # def vesting_balance_withdraw(self, vesting_id, amount=None, asset=None, account=None):
        # 这里可以根据需要添加要提取的amount，asset，account
        # gph.vesting_balance_withdraw(vesting_object_id, account=account_id)

def allowed_withdraw_by_sdk(vesting_id):
    vesting_object = Vesting(vesting_id)
    return vesting_object.claimable

def allowed_withdraw_test(account_id):
    vesting_objects = get_vesting_balances(account_id)
    for vesting_object in vesting_objects:
        vesting_object_id = vesting_object["id"]
        amount = allowed_withdraw(vesting_object_id)
        print("vesting_id: {}, allowed_withdraw_amount: {}".format(vesting_object_id, amount))

def allowed_withdraw_by_sdk_test(account_id):
    vesting_objects = gph.get_vesting_balances(account_id)
    for vesting_object in vesting_objects:
        vesting_object_id = vesting_object["id"]
        amount = allowed_withdraw(vesting_object_id)
        print("vesting_id: {}, allowed_withdraw_amount: {}".format(vesting_object_id, amount))

if __name__ == '__main__':
    init_wallet()
    # account_vesting("1.2.16")
    # allowed_withdraw_test("1.2.16")

    print("by sdk test")
    account_vesting_by_sdk("nicotest")
    allowed_withdraw_by_sdk_test("1.2.16")

'''
>>> 1. account_vesting 测试
dev@ubuntu:~$ python3 vesting.py 
chain_params {'chain_id': '9f487f4cca8ababac23d3806a901e9044ab4d82be33cf2abb5cc3185e04fbafd', 'prefix': 'COCOS', 'core_symbol': 'COCOS'}
2020-03-30 16:27:11.666890 [server] [init_wallet:98] [INFO]: wallet create status: True
2020-03-30 16:27:11.667664 [server] [init_wallet:102] [INFO]: wallet lock status: False
2020-03-30 16:27:12.113250 [server] [init_wallet:109] [INFO]: account id: 1.2.16, public key: COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx
2020-03-30 16:27:12.146529 [server] [account_vesting:131] [INFO]: vesting start
>> call [0, 'get_vesting_balances', ['1.2.16']]

{'jsonrpc': '2.0', 'result': [{'policy': [1, {'coin_seconds_earned_last_update': '2020-03-30T08:26:56', 'coin_seconds_earned': '811000000', 'vesting_seconds': 86400, 'start_claim': '1970-01-01T00:00:00'}], 'balance': {'amount': 200000, 'asset_id': '1.3.1'}, 'describe': 'cashback_gas', 'owner': '1.2.16', 'id': '1.13.10'}], 'id': 1}


1.13.10
{'expiration': '2020-03-30T09:27:13',
 'extensions': [],
 'operations': [[27,
                 {'amount': {'amount': 9386, 'asset_id': '1.3.1'},
                  'owner': '1.2.16',
                  'vesting_balance': '1.13.10'}]],
 'ref_block_num': 6609,
 'ref_block_prefix': 2414662508,
 'signatures': ['1f29bb31540d1b57d2f3cd45998eece3412ecaee4c7cf218ed4b1391130286547e54c1798b50f1e73032dd77685bc6b8d0a787eef3553556ec6a7b17ca596f08df']}

>>> 2. allowed_withdraw_test 测试
dev@ubuntu:~$ python3 vesting.py 
chain_params {'prefix': 'COCOS', 'chain_id': '9f487f4cca8ababac23d3806a901e9044ab4d82be33cf2abb5cc3185e04fbafd', 'core_symbol': 'COCOS'}
2020-03-30 16:34:53.922863 [server] [init_wallet:98] [INFO]: wallet create status: True
2020-03-30 16:34:53.924487 [server] [init_wallet:102] [INFO]: wallet lock status: False
2020-03-30 16:34:54.375142 [server] [init_wallet:109] [INFO]: account id: 1.2.16, public key: COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx
>> call [0, 'get_vesting_balances', ['1.2.16']]

{'id': 1, 'jsonrpc': '2.0', 'result': [{'balance': {'amount': 290614, 'asset_id': '1.3.1'}, 'id': '1.13.10', 'describe': 'cashback_gas', 'policy': [1, {'start_claim': '1970-01-01T00:00:00', 'vesting_seconds': 86400, 'coin_seconds_earned': '3249600', 'coin_seconds_earned_last_update': '2020-03-30T08:27:12'}], 'owner': '1.2.16'}]}


vesting_id: 1.13.10, allowed_withdraw_amount: 0.00038 GAS


>>> 3. vesting by sdk test
dev@ubuntu:~/data/mrepo/BlockContinuity$ python3 vesting.py 
chain_params {'core_symbol': 'COCOS', 'prefix': 'COCOS', 'chain_id': '9f487f4cca8ababac23d3806a901e9044ab4d82be33cf2abb5cc3185e04fbafd'}
2020-03-30 17:09:10.086646 [server] [init_wallet:88] [INFO]: wallet create status: True
2020-03-30 17:09:10.087725 [server] [init_wallet:92] [INFO]: wallet lock status: False
2020-03-30 17:09:10.533187 [server] [init_wallet:99] [INFO]: account id: 1.2.16, public key: COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx
by sdk test
1.13.10
vesting_id: 1.13.10, allowed_withdraw_amount: 0.07542 GAS

'''
