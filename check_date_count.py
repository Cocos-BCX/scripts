# -*- coding:utf-8 -*-
from PythonMiddleware.graphene import Graphene

import sys
import datetime
import time

# from config import *
from utils import Logging

logger = Logging().getLogger()

nodeaddress = "wss://api.cocosbcx.net"

AFTER_DAYS = 30
last_block_date = "1970-01-01" # random default date
result_block_data = {}

def check_block(start_date):
    global last_block_date, AFTER_DAYS, result_block_data
    start_date = start_date

    gph = Graphene(node=nodeaddress)
    info = gph.info()
    logger.info("info: {}".format(info))
    last_block_num = info['head_block_number']
    logger.info("time: {}".format(info["time"]))
    current_time = info["time"]
    current_date = info["time"].split("T")[0]

    start_block_num = 1
    end_block_num = last_block_num

    seconds = compare_time(current_date, start_date)
    logger.info("current_date: {}, start_date: {}, seconds: {}".format(current_date, start_date, seconds))

    if seconds < 3600 * 24 * AFTER_DAYS:
        logger.info("before {} days".format(AFTER_DAYS))
        logger.info("last_block_num: {}, delta: {}".format(last_block_num, 1800 * 24 * AFTER_DAYS))
        end_block_num = last_block_num
        start_block_num = last_block_num - 1800 * 24 * AFTER_DAYS
    else:
        logger.info("after {} days".format(AFTER_DAYS))
        start_block_num = int(last_block_num - seconds/2)
        end_block_num = int(start_block_num + (1800 * 24 * AFTER_DAYS))
        if last_block_num < end_block_num:
            end_block_num = last_block_num
    logger.info('[block num]start: {}, end: {}, last: {}, seconds: {}'.format(start_block_num, end_block_num, last_block_num, seconds))

    for block_num in range(start_block_num, end_block_num+1):
        try:
            block = gph.rpc.get_block(block_num)
            # logger.info("block: {}".format(block))
            timestamp = block["timestamp"]
            block_date = timestamp.split("T")[0]
            
            if block_date != last_block_date:
                # logger.info("last_date: {}, block_num: {}, block: {}".format(last_block_date, block_num, block))
                logger.info("last_date: {}, block_num: {}, block_id: {}, block timestamp: {}".format(last_block_date, 
                    block_num, block["block_id"], block["timestamp"]))
                if last_block_date in result_block_data.keys():
                    logger.info(">>>>>>>>>>>> {}: {}".format(last_block_date, result_block_data[last_block_date]))
                last_block_date = block_date
                result_block_data[block_date] = {
                    "block_total": 0,
                    "trx_total": 0,
                    "ops_total": 0
                }

            block_data = result_block_data[block_date]
            block_data["block_total"] += 1

            transactions = block["transactions"]
            if transactions:
                block_data["trx_total"] += len(transactions)
                for trx in transactions:
                    block_data["ops_total"] += len(trx[1]["operations"])
            result_block_data[block_date] = block_data
        except Exception as e:
            logger.error('get_object exception. block {}, error {}'.format(block_num, repr(e)))
    logger.info("\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>> total result: \n{}".format(result_block_data))

def compare_time(time1, time2):
    s_time = time.mktime(time.strptime(time1,'%Y-%m-%d'))
    e_time = time.mktime(time.strptime(time2,'%Y-%m-%d'))
    return int(s_time) - int(e_time)

def compare_time_test():
    result = compare_time('2020-04-17', '2020-04-19')
    logger.info("result: {}".format(result))

if __name__ == '__main__':
    logger.info('args: {}'.format(sys.argv))
    if len(sys.argv) < 2:
        logger.error('Usage: python3 check.py start_date[2020-07-01]')
        sys.exit(1)
    start_date = sys.argv[1]
    check_block(start_date)

'''
1. 功能
统计每天的链上区块、交易和operation的总数。

输入一个开始日期，统计该日期之后N天的数据，N由AFTER_DAYS全局变量控制，默认是7，可以根据统计需求任意修改。
如果开始日期和最新区块的间隔小于N天，统计最新区块之前的N天数据。

2. 使用
依赖： python-sdk

python3 check_count.py YYYY-MM-DD 

说明： 
日期格式： YYYY-MM-DD

3. 测试
AFTER_DAYS = 7 test record:
---------------------------------------------------
dev@ck-chain-slave-prod-001:~/cocos/data_analysis# nohup python3 check_count.py 2020-06-24 >> console.log 2>&1 &
2020-07-06 16:51:29.443240 [server] [<module>:91] [INFO]: args: ['check_count.py', '2020-06-24']
2020-07-06 16:51:29.585975 [server] [check_block:23] [INFO]: info: {'time': '2020-07-06T08:51:28', 'accounts_registered_this_interval': 18, 'recently_missed_count': 0, 'next_maintenance_time': '2020-07-07T00:00:00', 'current_transaction_count': 0, 'current_witness': '1.6.36', 'id': '2.1.0', 'head_block_number': 9329140, 'last_irreversible_block_num': 9329128, 'current_aslot': 9518886, 'witness_budget': '272600000000', 'head_block_id': '008e59f4f5fa46c80f5a7fd3dfad4dbe204fafc9', 'last_budget_time': '2020-07-06T00:00:00', 'dynamic_flags': 0, 'recent_slots_filled': '340282366920938463463374607431768211455'}
2020-07-06 16:51:29.586223 [server] [check_block:25] [INFO]: time: 2020-07-06T08:51:28
2020-07-06 16:51:29.589969 [server] [check_block:33] [INFO]: current_date: 2020-07-06, start_date: 2020-06-24, seconds: 1036800
2020-07-06 16:51:29.590146 [server] [check_block:41] [INFO]: after 7 days
2020-07-06 16:51:29.590254 [server] [check_block:46] [INFO]: [block num]start: 8810740, end: 9113140, last: 9329140, seconds: 1036800
2020-07-06 16:51:29.599740 [server] [check_block:58] [INFO]: last_date: 1970-01-01, block_num: 8810740, block_id: 008670f41d0a413935d202c7ee7dbb14f79f0835, block timestamp: 2020-06-24T08:48:12
2020-07-06 16:55:49.139138 [server] [check_block:58] [INFO]: last_date: 2020-06-24, block_num: 8838092, block_id: 0086dbcca27f73402123c6be0755a6ecedf2d73c, block timestamp: 2020-06-25T00:00:00
2020-07-06 16:55:49.139421 [server] [check_block:60] [INFO]: >>>>>>>>>>>> 2020-06-24: {'block_total': 27352, 'trx_total': 868, 'ops_total': 868}
2020-07-06 17:02:38.956799 [server] [check_block:58] [INFO]: last_date: 2020-06-25, block_num: 8881283, block_id: 00878483e65099b36de8a288347eab492ffee59e, block timestamp: 2020-06-26T00:00:00
2020-07-06 17:02:38.957072 [server] [check_block:60] [INFO]: >>>>>>>>>>>> 2020-06-25: {'block_total': 43191, 'trx_total': 1726, 'ops_total': 1726}
2020-07-06 17:09:30.549694 [server] [check_block:58] [INFO]: last_date: 2020-06-26, block_num: 8924474, block_id: 00882d3a8e787b69564c8a26e7b4bf9dbf65db20, block timestamp: 2020-06-27T00:00:00
2020-07-06 17:09:30.550018 [server] [check_block:60] [INFO]: >>>>>>>>>>>> 2020-06-26: {'block_total': 43191, 'trx_total': 2043, 'ops_total': 2043}
2020-07-06 17:16:21.686469 [server] [check_block:58] [INFO]: last_date: 2020-06-27, block_num: 8967666, block_id: 0088d5f2cd22ecd5d3194e529274704d2f5bf8e5, block timestamp: 2020-06-28T00:00:00
2020-07-06 17:16:21.686755 [server] [check_block:60] [INFO]: >>>>>>>>>>>> 2020-06-27: {'block_total': 43192, 'trx_total': 2436, 'ops_total': 2436}
2020-07-06 17:23:12.818186 [server] [check_block:58] [INFO]: last_date: 2020-06-28, block_num: 9010857, block_id: 00897ea99a4b7e7e6d49e292a4a9e1190bd204fa, block timestamp: 2020-06-29T00:00:00
2020-07-06 17:23:12.818479 [server] [check_block:60] [INFO]: >>>>>>>>>>>> 2020-06-28: {'block_total': 43191, 'trx_total': 2885, 'ops_total': 2885}
2020-07-06 17:30:03.952442 [server] [check_block:58] [INFO]: last_date: 2020-06-29, block_num: 9054047, block_id: 008a275fbbaf00c7faa2d130217659e8963525b9, block timestamp: 2020-06-30T00:00:00
2020-07-06 17:30:03.952740 [server] [check_block:60] [INFO]: >>>>>>>>>>>> 2020-06-29: {'block_total': 43190, 'trx_total': 2770, 'ops_total': 2770}
2020-07-06 17:36:56.448184 [server] [check_block:58] [INFO]: last_date: 2020-06-30, block_num: 9097239, block_id: 008ad01761e893ecf4550c6c1fe37fc37e685be9, block timestamp: 2020-07-01T00:00:00
2020-07-06 17:36:56.448449 [server] [check_block:60] [INFO]: >>>>>>>>>>>> 2020-06-30: {'block_total': 43192, 'trx_total': 2928, 'ops_total': 2928}
2020-07-06 17:39:28.038644 [server] [check_block:79] [INFO]:

>>>>>>>>>>>>>>>>>>>>>>>>>>> total result:
{'2020-06-24': {'block_total': 27352, 'trx_total': 868, 'ops_total': 868}, '2020-06-30': {'block_total': 43192, 'trx_total': 2928, 'ops_total': 2928}, '2020-06-27': {'block_total': 43192, 'trx_total': 2436, 'ops_total': 2436}, '2020-06-26': {'block_total': 43191, 'trx_total': 2043, 'ops_total': 2043}, '2020-06-28': {'block_total': 43191, 'trx_total': 2885, 'ops_total': 2885}, '2020-06-29': {'block_total': 43190, 'trx_total': 2770, 'ops_total': 2770}, '2020-06-25': {'block_total': 43191, 'trx_total': 1726, 'ops_total': 1726}, '2020-07-01': {'block_total': 15902, 'trx_total': 1061, 'ops_total': 1061}}

3. 结果格式和说明
total result json:
{
    "2020-06-24":{
        "block_total":27352,
        "trx_total":868,
        "ops_total":868
    },
    "2020-06-25":{
        "block_total":43191,
        "trx_total":1726,
        "ops_total":1726
    },
    "2020-06-26":{
        "block_total":43191,
        "trx_total":2043,
        "ops_total":2043
    },
    "2020-06-27":{
        "block_total":43192,
        "trx_total":2436,
        "ops_total":2436
    },
    "2020-06-28":{
        "block_total":43191,
        "trx_total":2885,
        "ops_total":2885
    },
    "2020-06-29":{
        "block_total":43190,
        "trx_total":2770,
        "ops_total":2770
    },
    "2020-06-30":{
        "block_total":43192,
        "trx_total":2928,
        "ops_total":2928
    },
    "2020-07-01":{
        "block_total":15902,
        "trx_total":1061,
        "ops_total":1061
    }
}

说明：首尾日期的数据统计不完整，忽略掉。
原因：获取的区块是根据日期转换计算的，没有做到很细致。
解决： 可以把计算的日期范围变长，比如：AFTER_DAYS调大; 输入的开始日期更早一些。
'''
