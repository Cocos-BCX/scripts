# -*- coding:utf-8 -*-

import json
import requests

#cli_wallet_url = "http://0.0.0.0:8048"
cli_wallet_url = "http://0.0.0.0:8047"
headers = {"content-type": "application/json"}

def get_account(name):
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "method": "get_account",
            "params": [name],
            "id":1
        }
        account_info = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
        account_object = account_info['result']
        return account_object
    except Exception as e:
        print(repr(e))

def suggest_brain_key():
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "method": "suggest_brain_key",
            "params": [],
            "id":1
        }
        response = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
        brain_key = response['result']
        print('>> suggest_brain_key\n {}\n'.format(brain_key))
        return brain_key
    except Exception as e:
        print(repr(e))

#register = "nicotest"
def register_account(register, new_account_name):
    owner_brain_key = suggest_brain_key()
    active_brain_key = suggest_brain_key()
    owner_pub_key = owner_brain_key['pub_key']   
    active_pub_key = active_brain_key['pub_key']
    print('>> register_account {} {} {} {} {}\n'.format(new_account_name, owner_pub_key, active_pub_key, register, 'true'))
    try:    
        body_relay = {
            "jsonrpc": "2.0",
            "method": "register_account",
            "params": [new_account_name, owner_pub_key, active_pub_key, register, "true"],
            "id":1
        }
        response = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
        #response = requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers)
        #print("status_code = {}, text: ".format(response.status_code, response.text))
        #print("response: ", json.loads(response))
        #if "error" in info:
        #    error = info["error"]["message"]
        #    print('errror: ', error)
        account_object = get_account(new_account_name)
        print('>> get_account {} \n{}\n'.format(new_account_name, account_object))
    except Exception as e:
        print(repr(e))

def get_account_asset_balance(account, asset_id='1.3.0'):
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "method": "list_account_balances",
            "params": [account],
            "id":1
        }
        response = json.loads(requests.post(cli_wallet_url, data = json.dumps(body_relay), headers = headers).text)
        balances = response['result']
        print('>> suggest_brain_key\n {}\n'.format(balances))
        for asset_balance in balances:
            print('asset_balance: {}'.format(asset_balance))
            if asset_balance['asset_id'] == asset_id:
                return asset_balance['amount']
        return 0
    except Exception as e:
        print(repr(e))

#test
#register_account('nicotest', 'test82')
amount = get_account_asset_balance('nicotest')
print('amount: {}\n'.format(amount))

amount = get_account_asset_balance('test22')
print('amount: {}\n'.format(amount))

''' 
example: 
python3 create_account.py

>> suggest_brain_key
 {'wif_priv_key': '5K2t8Y9P9KzMxJ9D6CK5h7HFzspb2zJyMvAVAcwPzaLahjEbcYd', 'brain_priv_key': 'QUARTAN AAM CUPRITE ROPY BUCKY FITTY TERMA PLOTE CATTAIL BERRET JINNY LADYISH TOW GOMUTI WITTING GARVOCK', 'address_info': 'COCOS4JmiPSsTxSjo6QfVZfSrPNf2AKvLdyiVo', 'pub_key': 'COCOS8WwAQmcjXBqNt2gwpQERzT6GVjqQHq8RCzMhNNPjK1BWQ99dE4'}

>> suggest_brain_key
 {'wif_priv_key': '5JGmmgByTJNzxAfAVDECT7Q2SQ7omro8eGxZSMyRcxwMhWqpTvr', 'brain_priv_key': 'AMINE BASALLY SAFENER CASSINO CANTRED TURBITH CHOIR SCHOLIA SEA CYMBA WOULDNT SERRANO BESCOUR INSHELL BEGLUC GAGROOT', 'address_info': 'COCOS2Tg23NPNsgHYhjQd9niCUZEEFa645Bea4', 'pub_key': 'COCOS64vuKNKijR8utnz6MH83A58YXCsy4gA9XtBTe1uabKadBZFGCz'}

>> register_account test81 COCOS8WwAQmcjXBqNt2gwpQERzT6GVjqQHq8RCzMhNNPjK1BWQ99dE4 COCOS64vuKNKijR8utnz6MH83A58YXCsy4gA9XtBTe1uabKadBZFGCz nicotest true

>> get_account test81 
{'options': {'memo_key': 'COCOS64vuKNKijR8utnz6MH83A58YXCsy4gA9XtBTe1uabKadBZFGCz', 'votes': [], 'extensions': []}, 'membership_expiration_date': '1970-01-01T00:00:00', 'asset_locked': {'contract_lock_details': [], 'locked_total': []}, 'owner': {'weight_threshold': 1, 'account_auths': [], 'key_auths': [['COCOS8WwAQmcjXBqNt2gwpQERzT6GVjqQHq8RCzMhNNPjK1BWQ99dE4', 1]], 'address_auths': []}, 'active': {'weight_threshold': 1, 'account_auths': [], 'key_auths': [['COCOS64vuKNKijR8utnz6MH83A58YXCsy4gA9XtBTe1uabKadBZFGCz', 1]], 'address_auths': []}, 'id': '1.2.269', 'registrar': '1.2.16', 'statistics': '2.6.269', 'name': 'test81'}

'''
