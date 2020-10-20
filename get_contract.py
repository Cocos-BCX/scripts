
#-*- coding: utf-8  -*-

import sys
import json
import requests

url_config = {
    "cli_wallet": "http://127.0.0.1:8048",
    "testnet": "https://test.cocosbcx.net",
    "mainnet": "https://api.cocosbcx.net"
}

#default url: mainnet
api_env = "mainnet"  # testnet, mainnet, cli_wallet
api_url = url_config[api_env]

headers = {"content-type": "application/json"}

# curl https://api.cocosbcx.net -d
# '{"id":1, "method":"call", "params":[0,"get_accounts",[["1.2.5", "1.2.100"]]]}'

def request_post(req_data, is_assert=True):
    response = json.loads(requests.post(api_url, data = json.dumps(req_data), headers = headers).text)
    # print('>> {} {}\n{}\n'.format(req_data['method'], req_data['params'], response))
    print('>> {} {}\n'.format(req_data['method'], req_data['params']))
    if is_assert:
        assert 'error' not in response
    return response

def get_contract(name_or_id):
    req_data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": [0, "get_contract", [name_or_id]],
        "id":1
    }
    if api_env == "cli_wallet":
        req_data["method"] = "get_contract"
        req_data["params"] = [name_or_id]
    return request_post(req_data)

def get_transaction_by_id(id):
    req_data = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": [0, "get_transaction_by_id", [id]],
        "id":1
    }
    if api_env == "cli_wallet":
        req_data["method"] = "get_transaction_by_id"
        req_data["params"] = [id]

    return request_post(req_data)

def main(name_or_id):
    contract = get_contract(name_or_id)['result']
    contract_version = contract['current_version']
    transaction = get_transaction_by_id(contract_version)['result']
    for operation_list in transaction['operations']:
        operation = operation_list[1]
        file_name = ""
        if operation_list[0] == 34:
            file_name = '{}_{}.lua'.format(api_env, operation['name'])
        elif operation_list[0] == 50:
            file_name = '{}_{}.lua'.format(api_env, operation['contract_id'])
        else:
            continue
        contract_code = operation['data']
        tokens = contract_code.split('\n')
        file = open(file_name, 'w')
        for token in tokens:
            file.writelines(token+'\n')
        file.close()


if __name__ == '__main__':
    print('>> {}\n'.format(sys.argv))
    if len(sys.argv) >= 2:
        contract_name_or_id = sys.argv[1]
        if len(sys.argv) >= 3:
            api_env = sys.argv[2]
            api_url = url_config[api_env]
        main(contract_name_or_id)
    else:
        print("Usage:\n./{} contract_name_or_id env \n  -- env: cli_wallet|testnet|mainnet, default mainnet".format(sys.argv[0]))

'''
示例：

dev@ubuntu:~/Desktop$ python3 get_contract_from_chain.py 1.16.2 cli_wallet
>> ['get_contract_from_chain.py', '1.16.2', 'cli_wallet']

>> get_contract ['1.16.2']

>> get_transaction_by_id ['efb7c050983d5572237d7e7bb4d99804bd285a799e672541ede81535e761dbc2']

dev@ubuntu:~/Desktop$ python3 get_contract_from_chain.py 1.16.2 testnet
>> ['get_contract_from_chain.py', '1.16.2', 'testnet']

>> call [0, 'get_contract', ['1.16.2']]

>> call [0, 'get_transaction_by_id', ['97784afe6f6304ed3fc9fb3919a20c2eff4b7d2188e12cde4be893154102053c']]

dev@ubuntu:~/Desktop$ python3 get_contract_from_chain.py 1.16.2 
>> ['get_contract_from_chain.py', '1.16.2']

>> call [0, 'get_contract', ['1.16.2']]

>> call [0, 'get_transaction_by_id', ['efb7c050983d5572237d7e7bb4d99804bd285a799e672541ede81535e761dbc2']]

dev@ubuntu:~/Desktop$ python3 get_contract_from_chain.py 1.16.3 mainnet
>> ['get_contract_from_chain.py', '1.16.3', 'mainnet']

>> call [0, 'get_contract', ['1.16.3']]

>> call [0, 'get_transaction_by_id', ['f23f955595bc64168d5ac8d194b67775ede9e51b037545925b47e1ad825f9cff']]

dev@ubuntu:~/Desktop$ ls *.lua
cli_wallet_contract.debug.hello12213132111111111111112.lua  mainnet_contract.debug.hello12213132111111111111112.lua
mainnet_1.16.3.lua                                          testnet_contract.privatetest.lua
dev@ubuntu:~/Desktop$ 
'''

