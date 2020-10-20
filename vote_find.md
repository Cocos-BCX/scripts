vote find  
---------------------

# 1. 功能  
* 支持多账户投票查询  
* 支持多账户对某一投票对象(理事会或见证人)查询  

# 2. 用法  
``` text  
dev@ubuntu:~/CocosBCX/scripts$ python3 vote_find.py  -h
>> sys.argv: ['vote_find.py', '-h']
usage: vote_find.py [-h] [-o VOTE_OBJECT] -a VOTE_ACCOUNTS [VOTE_ACCOUNTS ...]

manual to this script

optional arguments:
  -h, --help            show this help message and exit
  -o VOTE_OBJECT, --vote_object VOTE_OBJECT
                        vote object, witness or committee, if None: find
                        account vote detail
  -a VOTE_ACCOUNTS [VOTE_ACCOUNTS ...], --vote_accounts VOTE_ACCOUNTS [VOTE_ACCOUNTS ...]
                        <Required> vote account list
```  

# 3. 测试  
## 3.1 账户对见证人投票查询  
``` shell
dev@ubuntu:~/CocosBCX/scripts$ python3 vote_find.py  -a 1.2.5  1.2.28498 nicotest -o 1.6.15
>> sys.argv: ['vote_find.py', '-a', '1.2.5', '1.2.28498', 'nicotest', '-o', '1.6.15']
>> parse args: [('vote_accounts', ['1.2.5', '1.2.28498', 'nicotest']), ('vote_object', '1.6.15')]


vote_obj: id:1.6.15, url:bitcoinkeys.cn, vote_id:1:27, account:1.2.28168, total_votes:286745273051998, work_status:True

{
    "1.6.15": {
        "1.2.28498": {
            "asset_id": "1.3.0",
            "amount": "2000000000000"
        },
        "1.2.5": "No Vote Support",
        "nicotest": "No Vote Support",
        "total_votes": 286745273051998
    }
}
```  

## 3.2 账户对理事会投票查询  
``` text    
dev@ubuntu:~/CocosBCX/scripts$ python3 vote_find.py  -a 1.2.5  1.2.1251675  ll0099   -o 1.5.42
>> sys.argv: ['vote_find.py', '-a', '1.2.5', '1.2.1251675', 'll0099', '-o', '1.5.42']
>> parse args: [('vote_accounts', ['1.2.5', '1.2.1251675', 'll0099']), ('vote_object', '1.5.42')]


vote_obj: id:1.5.42, url:www.okex.me, vote_id:0:84, account:1.2.41189, total_votes:116767960622000, work_status:True

{
    "1.5.42": {
        "1.2.1251675": {
            "asset_id": "1.3.0",
            "amount": "519479800000"
        },
        "1.2.5": "No Vote Support",
        "ll0099": "No Vote Support",
        "total_votes": 116767960622000
    }
}
```  

## 3.3 账户投票情况查询  
``` text   
dev@ubuntu:~/CocosBCX/scripts$ python3 vote_find.py  -a 1.2.5  1.2.28498 faucet1
>> sys.argv: ['vote_find.py', '-a', '1.2.5', '1.2.28498', 'faucet1']
>> parse args: [('vote_accounts', ['1.2.5', '1.2.28498', 'faucet1']), ('vote_object', None)]

{
    "1.2.28498": {
        "1.6.36": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.25": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.15": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.27": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.17": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.29": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.26": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.34": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        },
        "1.6.23": {
            "amount": "2000000000000",
            "asset_id": "1.3.0"
        }
    },
    "1.2.5": "No Vote",
    "faucet1": "No Vote"
}
```  

