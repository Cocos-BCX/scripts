
## vesting_test.sh
``` shell
account_id="1.2.5"
echo "chain_api >>> get_vesting_balances "${account_id}
curl https://api.cocosbcx.net -d '{"id":1, "method":"call", "params":[0,"get_vesting_balances",["1.2.5"]]}' && echo ""

echo ""

echo "cli_wallet >>> get_vesting_balances "${account_id}
curl http://127.0.0.1:8045 -d '{"id":1, "method":"get_vesting_balances", "params":["1.2.5"]}' && echo ""
```

## vesting_test 执行 
``` text
chain_api >>> get_vesting_balances 1.2.5
{"id":1,"jsonrpc":"2.0","result":[{"id":"1.13.7","owner":"1.2.5","balance":{"amount":"4356800012269","asset_id":"1.3.0"},"policy":[1,{"vesting_seconds":86400,"start_claim":"1970-01-01T00:00:00","coin_seconds_earned":"376426657060041600","coin_seconds_earned_last_update":"2020-03-30T07:32:48"}],"describe":"1.6.1"}]}

cli_wallet >>> get_vesting_balances 1.2.5
{"id":1,"jsonrpc":"2.0","result":[{"id":"1.13.7","owner":"1.2.5","balance":{"amount":"4356800012269","asset_id":"1.3.0"},"policy":[1,{"vesting_seconds":86400,"start_claim":"1970-01-01T00:00:00","coin_seconds_earned":"376426657060041600","coin_seconds_earned_last_update":"2020-03-30T07:32:48"}],"describe":"1.6.1","allowed_withdraw":{"amount":"4356800012269","asset_id":"1.3.0"},"allowed_withdraw_time":"2020-03-30T07:33:10"}]}
```

## 可提取量简单计算公式
``` text
ratio = coin_seconds_earned/balance.amount/vesting_seconds
amount = balance.amount*ratio
```

## 公式测试
``` python
>>> r = 376426657060041600.0/4356800012269.0/86400.0 
>>> 4356800012269 * r
4356790012268.9995
>>> r
0.9999977047374283
>>> 
```  

## 误差
``` python
>>> (4356800012269 - 4356790012268.9995)/100000
100.0000000048828
>>> 
```

