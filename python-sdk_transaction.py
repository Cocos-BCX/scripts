# -*- coding: utf-8 -*-

from PythonMiddleware.graphene import Graphene
from PythonMiddleware.instance import set_shared_graphene_instance
from PythonMiddlewarebase import transactions, operations
from PythonMiddleware.transactionbuilder import TransactionBuilder
from PythonMiddleware.account import Account
from PythonMiddleware.asset import Asset
from PythonMiddleware.storage import configStorage
from PythonMiddleware.memo import Memo
from PythonMiddleware.amount import Amount
from pprint import pprint

import time 

################################ config ################################
## register config
register = {
    "name": "nicotest",
    "id": "1.2.16",
    "private_key": "5J2SChqa9QxrCkdMor9VC2k9NT4R4ctRrJA6odQCPkb3yL89vxo",
    "public_key": "COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx",
}

## wallet_password
wallet_password = "123456"

## chain-node ws config
# nodeAddress = "wss://api.cocosbcx.net" 
nodeAddress = "wss://test.cocosbcx.net" 
# nodeAddress = "ws://127.0.0.1:8049"
################################ config END ################################

gph = Graphene(node=nodeAddress, blocking=True)
set_shared_graphene_instance(gph)

def get_account(name):
    try:
        account = Account(name)
        return account
    except Exception as e:
        error_msg = repr(e)
        print('[WARN]name {}, error: {}'.format(name, repr(e)))
        return None

def create_account(name, owner_key, active_key, memo_key, registrar):
    try:
        response = gph.create_account(account_name=name, registrar=registrar,
                           owner_key=owner_key, active_key=active_key, memo_key=memo_key)
        print(response)
    except Exception as e:
        print('[ERROR]name {}, error: {}'.format(name, repr(e)))
        return False
    return True

def transfer(from_account, to, amount, asset="1.3.0", memo=""):
    try:
        response = gph.transfer(to=to, amount=amount, asset=asset, memo=[memo,0], account=from_account)
        print(response)
    except Exception as e:
        print('[ERROR]to {}, amount: {}, error: {}'.format(to, amount, repr(e)))
        return False
    return True

def init_wallet():
    try:
        if not gph.wallet.created():
            gph.newWallet(wallet_password)
        print("wallet create status: {}".format(gph.wallet.created()))

        if gph.wallet.locked():
            gph.wallet.unlock(wallet_password)
        print("wallet lock status: {}".format(gph.wallet.locked()))

        if gph.wallet.getPrivateKeyForPublicKey(register["public_key"]) is None:
            print("import private key into wallet. public key: {}".format(
                register["public_key"]))
            gph.wallet.addPrivateKey(register["private_key"])

        print("account id: {}, public key: {}".format(
            gph.wallet.getAccountFromPublicKey(register["public_key"]),
            register["public_key"]))

        configStorage["default_prefix"] = gph.rpc.chain_params["prefix"]
        configStorage["default_account"] = register["name"]
    except Exception as e:
        print('[ERROR]init sdk wallet exception. {}'.format(repr(e)))

def test_info():
    while True:
        print('>> info')
        pprint(gph.info())
        time.sleep(2)

def test_finalizeOp_by_transfer_op(from_account, to_account, amount, asset="1.3.0", memo=["", 0]):
        if not from_account or not to_account:
            print("[ERROR]You need to provide an from or to account")
            return

        account = Account(from_account, graphene_instance=gph)
        amount = Amount(amount, asset, graphene_instance=gph)
        to = Account(to_account, graphene_instance=gph)
        if account["id"] == to["id"]:
            print("[ERROR] from != to account")
            return
        
        memoObj=None
        if(len(memo[0]) != 0):
            if(memo[1] == 0):
                memoObj = [0, memo[0]]
            elif[memo[1] == 1]:
                memoObj = [1, Memo(
                    from_account=account,
                    to_account=to,
                    graphene_instance=gph
                ).encrypt(memo[0])
                ]
        # build transfer operation
        op = operations.Transfer(**{
            "from": account["id"],
            "to": to["id"],
            "amount": {
                "amount": int(amount),
                "asset_id": amount.asset["id"]
            },
            "memo": memoObj,
            "prefix": gph.rpc.chain_params["prefix"]
        })
        return gph.finalizeOp(op, account, "active")

def test_sign_by_transfer_op(from_account, to_account, amount, asset="1.3.0", memo=["", 0]):
        if not from_account or not to_account:
            print("[ERROR]You need to provide an from or to account")
            return

        # create transfer op
        account = Account(from_account, graphene_instance=gph)
        amount = Amount(amount, asset, graphene_instance=gph)
        to = Account(to_account, graphene_instance=gph)
        if account["id"] == to["id"]:
            print("[ERROR] from != to account")
            return
        
        memoObj=None
        if(len(memo[0]) != 0):
            if(memo[1] == 0):
                memoObj = [0, memo[0]]
            elif[memo[1] == 1]:
                memoObj = [1, Memo(
                    from_account=account,
                    to_account=to,
                    graphene_instance=gph
                ).encrypt(memo[0])
                ]
        # build transfer operation
        op = operations.Transfer(**{
            "from": account["id"],
            "to": to["id"],
            "amount": {
                "amount": int(amount),
                "asset_id": amount.asset["id"]
            },
            "memo": memoObj,
            "prefix": gph.rpc.chain_params["prefix"]
        })

        # use transaction builder and transaction broadcast
        txbuffer = TransactionBuilder(graphene_instance=gph)
        txbuffer.appendOps(op)
        txbuffer.appendSigner(account, "active")
        txbuffer.sign()
        print("txbuffer >>>: {}".format(txbuffer.json()))
        result = txbuffer.broadcast()
        print("broadcast result: {}".format(result))

def update_memo_key(account=None, key=None):
    if not account:
        print("no account")
        return

    if not key:
        brain_keys = gph.suggest_key()
        key = brain_keys["active_key"]
        print("brain_keys: {}\nkey:{}".format(brain_keys, key))

    try:
        result = gph.update_memo_key(key, account)
        print(result)
    except Exception as e:
        print('[ERROR]error: {}'.format(repr(e)))
        return

def get_object(obj_id):
    obj_result = gph.rpc.get_object(obj_id)
    print(obj_result)

def test():
    # get_object("1.6.34")
    test_info()

def main():
    #test()
    init_wallet()
    # transfer("nicotest", "init1", 10000)
    # test_finalizeOp_by_transfer_op("nicotest", "init1", 20000)
    # update_memo_key("nicotest", key="COCOS5TrJztVAY5F9aWDw5KtDHfdrffQn7F3sjgbL8YyssiKhVCLNf7")
    test_sign_by_transfer_op("nicotest", "init1", 20001)
    pass

if __name__ == '__main__':
    main()


'''
# testnet env 
## 1. test finalizeOp： 
dev@ubuntu:~/data/cocos/Python-Middleware/test$ python3 transaction.py 
chain_params {'chain_id': '1ae3653a3105800f5722c5bda2b55530d0e9e8654314e2f3dc6d2b010da641c5', 'prefix': 'COCOS', 'core_symbol': 'COCOS'}
wallet create status: True
wallet lock status: False

account id: 1.2.246756, public key: COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx

[Operation] args: (<PythonMiddlewarebase.operations.Transfer object at 0x7f675ec56b38>,), kwargs: {}
[Operation] args: ([0, {'amount': {'amount': 2000000000, 'asset_id': '1.3.0'}, 'extensions': [], 'from': '1.2.16', 'to': '1.2.6'}],), kwargs: {}

{'expiration': '2020-08-05T05:44:34',
 'extensions': [],
 'operations': [[0,
                 {'amount': {'amount': 2000000000, 'asset_id': '1.3.0'},
                  'extensions': [],
                  'from': '1.2.16',
                  'to': '1.2.6'}]],
 'ref_block_num': 40445,
 'ref_block_prefix': 4198479032,
 'signatures': ['201c9ce9e29acd0767b9fb266a093bd2e33f9ca14319c2cb74b08066a96d5d6c596dc512fd0389a3de6da917763d21e2c694ad38922641f0889c7d30122f4d342b']}


## 2. test update memo key:
dev@ubuntu:~/data/cocos/Python-Middleware/test$ python3 transaction.py 
chain_params {'chain_id': '1ae3653a3105800f5722c5bda2b55530d0e9e8654314e2f3dc6d2b010da641c5', 'core_symbol': 'COCOS', 'prefix': 'COCOS'}
wallet create status: True
wallet lock status: False

account id: 1.2.16, public key: COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx

[Operation] args: (<PythonMiddlewarebase.operations.Account_update object at 0x7fe9674636d8>,), kwargs: {}
[Operation] args: ([6, {'account': '1.2.16', 'extensions': [], 'new_options': {'extensions': [], 'votes': ['1:0', '1:9', '1:10', '0:11', '0:13', '0:14', '0:21'], 'memo_key': 'COCOS5TrJztVAY5F9aWDw5KtDHfdrffQn7F3sjgbL8YyssiKhVCLNf7'}}],), kwargs: {}

{'expiration': '2020-08-05T05:42:00',
 'extensions': [],
 'operations': [[6,
                 {'account': '1.2.16',
                  'extensions': [],
                  'new_options': {'extensions': [],
                                  'memo_key': 'COCOS5TrJztVAY5F9aWDw5KtDHfdrffQn7F3sjgbL8YyssiKhVCLNf7',
                                  'votes': ['1:0',
                                            '1:9',
                                            '1:10',
                                            '0:11',
                                            '0:13',
                                            '0:14',
                                            '0:21']}}]],
 'ref_block_num': 40373,
 'ref_block_prefix': 2142511142,
 'signatures': ['1f03dee9d330279ed23dc2c588a9c851eebec65d02bc839f2cb0f03c1175569af302f029f50edea810a694600f16682523d8f2cf9e1b2d7a68a6aa2c6c8292e7e3']}
{'trx_id': '648cb2b7d8a69238e0e3277c02ea569c1f95c4cd8a564ec35f2f82ffa1e8fc9c', 'transaction': {'extensions': [], 'operations': [[6, {'account': '1.2.16', 'extensions': {}, 'new_options': {'extensions': [], 'votes': ['1:0', '1:9', '1:10', '0:11', '0:13', '0:14', '0:21'], 'memo_key': 'COCOS5TrJztVAY5F9aWDw5KtDHfdrffQn7F3sjgbL8YyssiKhVCLNf7'}}]], 'signatures': ['1f03dee9d330279ed23dc2c588a9c851eebec65d02bc839f2cb0f03c1175569af302f029f50edea810a694600f16682523d8f2cf9e1b2d7a68a6aa2c6c8292e7e3'], 'ref_block_prefix': 2142511142, 'operation_results': [[1, {'real_running_time': 170, 'fees': [{'amount': 507, 'asset_id': '1.3.1'}]}]], 'ref_block_num': 40373, 'expiration': '2020-08-05T05:42:00'}, 'block_num': 8494519}

## 3. sign transaction and broadcast
dev@ubuntu:~/data/cocos/Python-Middleware/test$ python3 transaction.py 
chain_params {'prefix': 'COCOS', 'chain_id': '1ae3653a3105800f5722c5bda2b55530d0e9e8654314e2f3dc6d2b010da641c5', 'core_symbol': 'COCOS'}
wallet create status: True
wallet lock status: False
account id: 1.2.246756, public key: COCOS56a5dTnfGpuPoWACnYj65dahcXMpTrNQkV3hHWCFkLxMF5mXpx
[Operation] args: (<PythonMiddlewarebase.operations.Transfer object at 0x7f3033207ac8>,), kwargs: {}
[Operation] args: ([0, {'to': '1.2.6', 'amount': {'asset_id': '1.3.0', 'amount': 2000100000}, 'from': '1.2.16', 'extensions': []}],), kwargs: {}
txbuffer >>>: {'signatures': ['1f1673b628d5d0a89074c07aaa9c33c83288c55de925662f518a227779a7d8941e27ea66611fa8832140975d18d2c01dc93cb1ba373b0b0c5fad98677399e9a8cc'], 'operations': [[0, {'to': '1.2.6', 'amount': {'asset_id': '1.3.0', 'amount': 2000100000}, 'from': '1.2.16', 'extensions': []}]], 'ref_block_prefix': 934502227, 'extensions': [], 'expiration': '2020-08-05T07:06:13', 'ref_block_num': 42670}
{'expiration': '2020-08-05T07:06:13',
 'extensions': [],
 'operations': [[0,
                 {'amount': {'amount': 2000100000, 'asset_id': '1.3.0'},
                  'extensions': [],
                  'from': '1.2.16',
                  'to': '1.2.6'}]],
 'ref_block_num': 42670,
 'ref_block_prefix': 934502227,
 'signatures': ['1f1673b628d5d0a89074c07aaa9c33c83288c55de925662f518a227779a7d8941e27ea66611fa8832140975d18d2c01dc93cb1ba373b0b0c5fad98677399e9a8cc']}
broadcast result: {'block_num': 8496816, 'trx_id': 'e87e441cb3d5b7ac91b7ce542dd525a546adea133335b708119640faea967618', 'transaction': {'signatures': ['1f1673b628d5d0a89074c07aaa9c33c83288c55de925662f518a227779a7d8941e27ea66611fa8832140975d18d2c01dc93cb1ba373b0b0c5fad98677399e9a8cc'], 'operations': [[0, {'to': '1.2.6', 'amount': {'asset_id': '1.3.0', 'amount': 2000100000}, 'from': '1.2.16', 'extensions': []}]], 'ref_block_prefix': 934502227, 'extensions': [], 'operation_results': [[1, {'real_running_time': 56, 'fees': [{'asset_id': '1.3.1', 'amount': 10000}]}]], 'expiration': '2020-08-05T07:06:13', 'ref_block_num': 42670}}

'''
